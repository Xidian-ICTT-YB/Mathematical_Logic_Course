#!/usr/bin/env python3
"""Replay and check the saved experiment evidence with Python's standard library."""

import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import statistics
import subprocess
import sys


COVERAGE = "v2-20261113-125655-b19929"
REPEATS = "v2-20261112-165952-5a0340"
ALGORITHMS = ["bmc", "k-induction", "predicateAnalysis", "impact"]
STATUSES = ["SAFE", "UNSAFE", "TIMEOUT", "MEMORY_LIMIT", "JAVA_MEMORY_ERROR", "ERROR", "UNKNOWN"]
SUCCESS = {"SAFE", "UNSAFE"}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_parser(root):
    path = root / "scripts/v2_evidence.py"
    spec = importlib.util.spec_from_file_location("saved_evidence_parser", path)
    module = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(module)
    return module.parse_log


def load_runs(root, batch_name, expected_count):
    batch = root / "experiment-v2/evidence" / batch_name
    schedule = read_json(batch / "schedule.json")
    aggregate = read_json(batch / "results.json")
    require((batch / "COMPLETE").is_file(), f"批次缺少完成记录 {batch_name}")
    require(len(schedule) == len(aggregate) == expected_count, f"批次数量不符 {batch_name}")
    parse_log = load_parser(root)
    records = []
    for index, (entry, saved) in enumerate(zip(schedule, aggregate), 1):
        result_path = batch / f"{index:03d}/result.json"
        result = read_json(result_path)
        require(result == saved and result["entry"] == entry, f"计划或汇总不一致 {result_path}")
        log_path = result_path.parent / Path(result["log"]).parent.name / "run.log"
        text = log_path.read_text(encoding="utf-8", errors="replace")
        parsed = parse_log(text, result["exit_code"], result["runner_stop_reason"])
        require(parsed["status"] == result["status"], f"日志重解析结果不同 {log_path}")
        cpu_matches = re.findall(r"^Total CPU time for CPAchecker:\s*([\d.]+)s", text, re.M)
        cpu_seconds = float(cpu_matches[-1]) if cpu_matches else None
        require(cpu_seconds == result["cpa_cpu_seconds"], f"CPU统计不一致 {log_path}")
        require(result["status"] not in SUCCESS or result["status"] == result["expected"],
                f"判定与标签冲突 {log_path}")
        records.append(dict(result=result, text=text, path=log_path, cpu=cpu_seconds))
    keys = [(r["entry"]["task"], r["entry"]["algorithm"], r["entry"]["repeat"]) for r in aggregate]
    require(len(set(keys)) == expected_count, f"运行计划存在重复组合 {batch_name}")
    return records


def trace_directory(root):
    trace = root / "evidence/vhost-trace"
    if trace.is_dir():
        return trace
    raise FileNotFoundError("缺少 vhost 补充导出证据目录")


def check(root):
    print("校验保存的实验输入与原始证据")
    count = 0
    reviews = [(COVERAGE, "review-coverage-20261114"), (REPEATS, "review-repeat-20261113")]
    for batch_name, review in reviews:
        manifest = read_json(root / "experiment-v2" / review / "local-evidence-sha256.json")
        for relative, expected in manifest.items():
            path = root / "experiment-v2/evidence" / batch_name / relative
            require(sha256(path) == expected, f"文件校验失败 {path}")
        count += len(manifest)
        print(f"  {batch_name} 的 {len(manifest)} 个文件通过 SHA256 校验")
    tasks = read_json(root / "experiment-v2/design-20261111/tasks50-frozen.json")
    require(len(tasks) == len({task["path"] for task in tasks}) == 50, "冻结任务清单应有50个不同任务")
    for task in tasks:
        path = root / "experiment-v2/inputs/c" / task["path"]
        require(sha256(path) == task["sha256"], f"源码校验失败 {path}")
        require(sha256(path.parent / "ALL.prp") == task["property_sha256"], f"属性校验失败 {path.parent}")
    trace = trace_directory(root)
    trace_hashes = read_json(root / "demo/trace-sha256.json")
    for relative, expected in trace_hashes.items():
        require(sha256(trace / relative) == expected, f"轨迹文件校验失败 {relative}")
    load_runs(root, COVERAGE, 200)
    load_runs(root, REPEATS, 48)
    print(f"  50个源码与对应属性文件、{len(trace_hashes)}个轨迹文件通过校验")
    print("  248次运行的计划、逐次结果、汇总和日志重新解析结果一致")
    print(f"校验完成，共核验 {count} 个主实验及重复实验文件。\n")


def summary(root):
    records = load_runs(root, COVERAGE, 200)
    counts = Counter(record["result"]["status"] for record in records)
    saved = read_json(root / "experiment-v2/review-coverage-20261114/summary.json")
    require(counts == Counter(saved["counts"]), "重算总表与保存的审计汇总不一致")
    print("50个任务的正式覆盖实验，每种配置运行50次")
    print("SAFE为证明安全，UNSAFE为确认错误，其余状态表示本次未给出确定结论。")
    print("算法                 SAFE UNSAFE TIMEOUT 内存阈值 Java堆错误 ERROR UNKNOWN")
    for algorithm in ALGORITHMS:
        subtotal = Counter(record["result"]["status"] for record in records
                           if record["result"]["entry"]["algorithm"] == algorithm)
        values = " ".join(f"{subtotal[status]:7d}" for status in STATUSES)
        print(f"{algorithm:18s} {values}")
    predicate = [r for r in records if r["result"]["entry"]["algorithm"] == "predicateAnalysis"]
    recursion = sum("Unsupported feature (recursion)" in r["text"] for r in predicate
                    if r["result"]["status"] == "ERROR")
    p_counts = Counter(r["result"]["status"] for r in predicate)
    solved = p_counts["SAFE"] + p_counts["UNSAFE"]
    print(f"\n谓词抽象给出{solved}个确定结论。{p_counts['ERROR']}个ERROR中，{recursion}个日志含不支持递归诊断。")
    print(f"其余结果为{p_counts['TIMEOUT']}次超时、{p_counts['MEMORY_LIMIT']}次内存阈值终止。所有确定判定均与基准标签一致。")
    pairs = defaultdict(dict)
    for record in records:
        entry = record["result"]["entry"]
        pairs[entry["task"]][entry["algorithm"]] = record
    common = [pair for pair in pairs.values()
              if pair["predicateAnalysis"]["result"]["status"] in SUCCESS
              and pair["impact"]["result"]["status"] in SUCCESS]
    p_time = sum(pair["predicateAnalysis"]["cpu"] for pair in common)
    i_time = sum(pair["impact"]["cpu"] for pair in common)
    p_wins = sum(pair["predicateAnalysis"]["cpu"] < pair["impact"]["cpu"] for pair in common)
    print(f"\n两种抽象配置共同解决{len(common)}个任务，工具内部CPU累计为{p_time:.2f}秒和{i_time:.2f}秒。")
    print(f"这批单次测量中，谓词抽象在{p_wins}题上较快，IMPACT在{len(common)-p_wins}题上较快。\n")


def pcd(root):
    records = load_runs(root, REPEATS, 48)
    selected = [r for r in records if "--paride--pcd.ko" in r["result"]["entry"]["task"]]
    require(len(selected) == 16, "pcd重复案例应有16次运行")
    print("pcd案例，四种配置各重复四轮")
    for algorithm in ALGORITHMS:
        group = sorted((r for r in selected if r["result"]["entry"]["algorithm"] == algorithm),
                       key=lambda r: r["result"]["entry"]["repeat"])
        states = "/".join(r["result"]["status"] for r in group)
        print(f"  {algorithm:18s} {states}")
        if all(r["result"]["status"] in SUCCESS for r in group):
            times = [r["cpu"] for r in group]
            print(f"    CPU原始值 {times} 秒，中位数 {statistics.median(times):.3f} 秒")
    print("\n每轮日志中的抽象统计")
    print("算法/轮次                 抽象调用   缓存命中   布尔抽象   抽象模块秒")
    for algorithm in ["predicateAnalysis", "impact"]:
        for record in sorted(selected, key=lambda r: r["result"]["entry"]["repeat"]):
            entry = record["result"]["entry"]
            if entry["algorithm"] != algorithm:
                continue
            patterns = [r"^Number of abstractions:\s*(\d+)", r"^\s*Times result was cached:\s*(\d+)",
                        r"^\s*Times boolean abs was used:\s*(\d+)", r"^\s*Time for abstraction:\s*([\d.]+)s"]
            values = []
            for pattern in patterns:
                match = re.search(pattern, record["text"], re.M)
                require(match is not None, f"日志缺少统计项 {pattern}")
                values.append(match.group(1))
            print(f"  {algorithm}/{entry['repeat']}".ljust(27) + " ".join(v.rjust(10) for v in values))
    print("\n9700次抽象调用包含缓存命中。缓存命中减少了需要执行布尔抽象的次数。")
    print("两种配置的缓存利用和实际抽象计算次数不同，这为耗时差异提供了具体证据。")
    print("该观察来自完整配置对比；确认某一个开关的因果作用还需要单独对照。")
    coverage = load_runs(root, COVERAGE, 200)
    later = next(r for r in coverage if "--paride--pcd.ko" in r["result"]["entry"]["task"]
                 and r["result"]["entry"]["algorithm"] == "impact")
    print(f"后续50题批次中IMPACT在pcd上耗时{later['cpu']:.2f}秒，跨批次耗时会波动。")
    example = next(r for r in selected if r["result"]["entry"]["algorithm"] == "predicateAnalysis")
    print(f"原始日志示例 {example['path'].relative_to(root)}\n")


def vhost(root):
    trace = trace_directory(root)
    log = (trace / "run.log").read_text(encoding="utf-8", errors="replace")
    require("Error path found and confirmed by counterexample check with CBMC." in log,
            "vhost日志缺少CBMC确认信息")
    require("Verification result: FALSE" in log, "vhost轨迹运行没有返回FALSE")
    print("vhost错误轨迹，读取独立补充导出运行")
    print("日志记录CBMC确认反例，最终判定FALSE。以下行号指输入基准源码。")
    core = trace / "output/Counterexample.1.core.txt"
    selected_lines = {12138, 11116, 10988, 12056, 10660, 12051, 12054, 11626}
    for line in core.read_text(encoding="utf-8").splitlines():
        match = re.match(r"line (\d+):", line)
        if match and int(match.group(1)) in selected_lines:
            print("  " + line)
    print("\n模型状态从1变为2，表示第一次加锁已经发生。")
    print("第二次加锁的包装函数检查同一个模型状态，值为2时触发错误函数。")
    print("设备锁与队列锁在此基准中共用模型变量，结论适用于这个转换后的验证程序。")
    print(f"证据文件 {core.relative_to(root)}\n")


def live(root, run):
    require(sys.platform.startswith("linux"), "新验证执行入口需要配置好的Linux服务器。")
    required = ["scripts/run_v2.py", "tools/java8/bin/java", "tools/supplements-vstte/CPAchecker/scripts/cpa.sh"]
    for relative in required:
        require((root / relative).is_file(), f"新验证缺少运行依赖 {root / relative}")
    command = [sys.executable, str(root / "scripts/run_v2.py"), "--root", str(root),
               "--schedule", "demo/live-schedule.json"]
    if run:
        command.append("--run")
    print("调用原实验运行器检查pata_marvell演示任务" if not run else "启动一次pata_marvell谓词抽象验证，输出到新的results批次", flush=True)
    return subprocess.call(command)


def main():
    parser = argparse.ArgumentParser(description="读取已保存的真实实验记录进行课堂演示；--live可在已配置服务器执行新验证。")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="项目或解压后的提交包根目录")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--check", action="store_true", help="校验输入、证据哈希和248次运行一致性")
    actions.add_argument("--summary", action="store_true", help="从原始日志重算200次主表")
    actions.add_argument("--case", choices=["pcd", "vhost"], help="展示一个真实案例")
    actions.add_argument("--all", action="store_true", help="依次完成校验、统计和两个案例")
    actions.add_argument("--live", action="store_true", help="Linux服务器上的新验证预检查；加--execute执行")
    parser.add_argument("--execute", action="store_true", help="与--live合用，明确启动一次新的验证")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.execute and not args.live:
        parser.error("--execute需要与--live同时使用")
    if args.live:
        return live(root, args.execute)
    print("课堂证据演示：读取已保存的真实验证运行。\n")
    if args.check or args.all:
        check(root)
    if args.summary or args.all:
        summary(root)
    if args.case == "pcd" or args.all:
        pcd(root)
    if args.case == "vhost" or args.all:
        vhost(root)
    if not any([args.check, args.summary, args.case, args.all]):
        parser.print_help()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, ImportError) as error:
        print(f"演示停止：{error}", file=sys.stderr)
        sys.exit(1)
