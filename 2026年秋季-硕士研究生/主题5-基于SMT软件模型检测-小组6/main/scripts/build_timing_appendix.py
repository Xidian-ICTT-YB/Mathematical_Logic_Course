"""Recompute the 200-run timing appendix from verified logs and saved results."""

import argparse
from collections import Counter
import importlib.util
import json
import math
from pathlib import Path
import statistics
import sys
import tempfile


ALGORITHMS = ["bmc", "k-induction", "predicateAnalysis", "impact"]
LABELS = {"bmc": "BMC", "k-induction": "k-induction", "predicateAnalysis": "谓词抽象", "impact": "IMPACT"}
STATUS_LABELS = {"SAFE": "SAFE", "UNSAFE": "UNSAFE", "TIMEOUT": "超时", "MEMORY_LIMIT": "内存阈值",
                 "JAVA_MEMORY_ERROR": "Java堆错误", "NATIVE_MEMORY_ERROR": "原生内存错误",
                 "ERROR": "工具报错", "UNKNOWN": "UNKNOWN"}
SUCCESS = {"SAFE", "UNSAFE"}
COVERAGE = "v2-20261113-125655-b19929"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def short_name(program):
    filename = Path(program).name
    if ".ko" in filename:
        module = filename.split(".ko", 1)[0]
        separator = "--" if "--" in module else "-"
        return module.rsplit(separator, 1)[-1]
    require("-ko" in filename, "无法提取驱动短名 " + filename)
    return filename.split("-ko", 1)[0].rsplit("-", 1)[-1]


def verify_and_load(root):
    spec = importlib.util.spec_from_file_location("classroom_evidence_demo", root / "demo/run.py")
    demo = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(demo)
    # Reuse the demo check for both the 200 formal runs and the 48 case repeats.
    demo.check(root)
    records = demo.load_runs(root, COVERAGE, 200)
    comparisons = read_json(root / "experiment-v2/review-coverage-20261114/comparison200.json")
    require(len(comparisons) == 200, "论文对照表应有200条主实验记录")
    by_key = {(r["entry"]["task"], r["entry"]["algorithm"]): r for r in comparisons}
    require(len(by_key) == 200, "论文对照表中存在重复的任务与算法组合")
    for record in records:
        result = record["result"]
        entry = result["entry"]
        comparison = by_key[(entry["task"], entry["algorithm"])]
        require(comparison["entry"] == entry, "对照表运行身份不同")
        require(comparison["actual"] == comparison["reparsed_status"] == result["status"], "对照表判定不同")
        require(comparison["expected"] == result["expected"], "对照表标签不同")
        require(comparison["cpu_seconds"] == record["cpu"], "对照表CPU统计不同")
        require((root / comparison["local_log"]).resolve() == record["path"].resolve(), "对照表日志指向不同")
    return records


def derive(root, records):
    rows = [record["result"] for record in records]
    algorithms = []
    for algorithm in ALGORITHMS:
        group = [row for row in rows if row["entry"]["algorithm"] == algorithm]
        require(len(group) == 50, f"{algorithm}应有50条主实验记录")
        successful = [row for row in group if row["status"] in SUCCESS]
        success_times = [row["cpa_cpu_seconds"] for row in successful if row["cpa_cpu_seconds"] is not None]
        wall_times = [row["wall_seconds"] for row in group if row["wall_seconds"] is not None]
        algorithms.append(dict(
            algorithm=algorithm,
            total_runs=len(group),
            success_count=len(successful),
            successful_cpu_observed_count=len(success_times),
            successful_cpu_sum_seconds=round(math.fsum(success_times), 6),
            successful_cpu_median_seconds=round(statistics.median(success_times), 6) if success_times else None,
            all_wall_sum_seconds=round(math.fsum(wall_times), 6),
            missing_wall_count=len(group) - len(wall_times),
            missing_cpu_count=sum(row["cpa_cpu_seconds"] is None for row in group),
            timeout_count=sum(row["status"] == "TIMEOUT" for row in group),
            status_counts=dict(sorted(Counter(row["status"] for row in group).items())),
        ))
    frozen = read_json(root / "experiment-v2/design-20261111/tasks50-frozen.json")
    record_map = {(r["result"]["entry"]["task"], r["result"]["entry"]["algorithm"]): r for r in records}
    tasks = []
    for index, source in enumerate(frozen, 1):
        runs = {}
        for algorithm in ALGORITHMS:
            record = record_map[(source["path"], algorithm)]
            result = record["result"]
            relative_log = record["path"].relative_to(root)
            runs[algorithm] = dict(status=result["status"], cpu_seconds=record["cpu"],
                                   wall_seconds=result["wall_seconds"],
                                   raw_verdict=result["raw_verdict"],
                                   runner_stop_reason=result["runner_stop_reason"],
                                   log=relative_log.as_posix(),
                                   result=relative_log.parent.parent.joinpath("result.json").as_posix())
        tasks.append(dict(task_id=f"T{index:02d}", short_name=short_name(source["path"]),
                          expected=source["expected"], program=source["path"],
                          source_file="experiment-v2/inputs/c/" + source["path"],
                          source_sha256=source["sha256"], runs=runs))
    require(len(tasks) == 50, "冻结清单应有50个任务")
    summary = dict(
        batch=COVERAGE,
        count=200,
        task_count=50,
        definition=dict(success="status in SAFE/UNSAFE; every definite verdict agrees with expected label",
                        cpu_seconds="Total CPU time for CPAchecker from run.log, measured at termination",
                        wall_seconds="wall_seconds from the per-run result.json",
                        missing_cpu="null in JSON; em dash in the readable appendix",
                        aggregation="successful CPU summaries use each algorithm's own solved subset; wall sums use all 50 runs"),
        algorithms=algorithms,
    )
    task_map = dict(batch=COVERAGE, task_id_order="tasks50-frozen.json list order, starting at T01",
                    cpu_unit="seconds", wall_unit="seconds", tasks=tasks)
    return summary, task_map


def display_time(value, places=2):
    return "—" if value is None else f"{value:.{places}f}"


def render_markdown(summary, task_map):
    lines = ["# 四算法运行时间明细", "",
             "本附录对应50个Linux驱动任务的200次正式实验。",
             "",
             "时间单位均为秒。逐题表采用日志中记录的CPAchecker内部CPU时间，表示该次退出时已经记录的消耗。超时条目保留实际数值，资源终止后缺少内部计时的条目以“—”表示。",
             "内部CPU时间与运行器监测的进程组资源具有不同计量范围。部分超时条目的内部CPU低于900秒，其终止原因可在映射中的 `runner_stop_reason` 与原始日志中核查。",
             "",
             "SAFE表示工具证明所检查的安全性质，UNSAFE表示确认了错误路径。超时、内存阈值、Java堆错误、工具报错和UNKNOWN保留各自的运行状态。",
             "",
             "[总README](README.md)给出实验范围与使用说明。[机器可读汇总](experiment-v2/timing-summary.json)保存汇总数值。[任务与日志映射](experiment-v2/timing-task-map.json)提供每个任务的完整输入路径、源码哈希和四份原始日志位置。",
             "", "## 四种配置的耗时汇总", "",
             "成功CPU累计和中位数分别基于各算法得到确定判定的任务。成功任务集合不同，跨算法的总和或中位数需要结合任务身份解释。墙钟累计基于各算法全部50次运行，包含成功、超时与其他终止状态。",
             "",
             "|算法|成功次数|成功CPU累计|成功CPU中位数|50次墙钟累计|内部CPU缺失数|",
             "|---|---:|---:|---:|---:|---:|"]
    for row in summary["algorithms"]:
        lines.append("|" + "|".join([LABELS[row["algorithm"]], str(row["success_count"]),
                     display_time(row["successful_cpu_sum_seconds"], 3),
                     display_time(row["successful_cpu_median_seconds"], 3),
                     display_time(row["all_wall_sum_seconds"], 3), str(row["missing_cpu_count"])]) + "|")
    lines.extend(["", "所有成功条目的内部CPU时间均可读取，全部200次运行的墙钟时间均有记录。本表仅采用50个任务的200次正式实验记录。",
                  "", "## 逐题结果与内部CPU时间", "",
                  "任务编号按冻结清单的原始顺序生成。短名称用于阅读，完整程序身份见JSON映射。同名驱动的不同版本或入口由任务编号区分。每格依次给出判定和内部CPU秒数。"])
    tasks = task_map["tasks"]
    for start in range(0, len(tasks), 10):
        lines.extend(["", f"### T{start+1:02d}至T{min(start+10, len(tasks)):02d}", "",
                      "|任务ID|短名称|BMC|k-induction|谓词抽象|IMPACT|",
                      "|---|---|---|---|---|---|"])
        for task in tasks[start:start+10]:
            cells = [task["task_id"], task["short_name"]]
            for algorithm in ALGORITHMS:
                run = task["runs"][algorithm]
                cells.append(STATUS_LABELS[run["status"]] + " · " + display_time(run["cpu_seconds"]))
            lines.append("|" + "|".join(cells) + "|")
    lines.extend(["", "## 复算方法", "",
                  "生成脚本先检查保存的原始文件及日志判定，再将本表使用的200条正式记录与论文对照表逐一配对。墙钟时间直接读取逐次 `result.json`。",
                  "", "重新生成本附录及JSON可运行以下命令。", "", "```bash",
                  "python3 scripts/build_timing_appendix.py", "```", "",
                  "只读重算并检查三份派生文件与原始记录一致可使用以下命令。", "", "```bash",
                  "python3 scripts/build_timing_appendix.py --check", "```", ""])
    return "\n".join(lines)


def write_atomic(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(content)
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="只读重算并核对派生JSON与Markdown")
    args = parser.parse_args()
    root = args.root.resolve()
    records = verify_and_load(root)
    summary, mapping = derive(root, records)
    outputs = {
        root / "experiment-v2/timing-summary.json": json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        root / "experiment-v2/timing-task-map.json": json.dumps(mapping, ensure_ascii=False, indent=2) + "\n",
        root / "运行时间明细.md": render_markdown(summary, mapping),
    }
    for path, content in outputs.items():
        if args.check:
            require(path.read_text(encoding="utf-8") == content, "派生文件与原始记录不一致 " + str(path))
        else:
            write_atomic(path, content)
        print(("CHECKED " if args.check else "WROTE ") + str(path.relative_to(root)))
    for row in summary["algorithms"]:
        print(row["algorithm"], "success", row["success_count"],
              "CPU sum", row["successful_cpu_sum_seconds"], "CPU median", row["successful_cpu_median_seconds"],
              "wall sum", row["all_wall_sum_seconds"], "missing CPU", row["missing_cpu_count"])


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        print("耗时附录校验失败 " + str(error), file=sys.stderr)
        sys.exit(1)
