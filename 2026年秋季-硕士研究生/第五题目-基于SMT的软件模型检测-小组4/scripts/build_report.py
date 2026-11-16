#!/usr/bin/env python3
"""Generate report/实验复现报告.md from the real experiment artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
ALGOS = ("BMC", "kInduction", "Predicate", "Impact")
LABELS = {
    "BMC": "BMC",
    "kInduction": "k-Induction",
    "Predicate": "Predicate Abstraction",
    "Impact": "Impact (Lazy Abstraction)",
}


def load() -> tuple[list[dict], dict[tuple[str, str], dict]]:
    rows = json.loads((RESULTS / "summary_detail.json").read_text(encoding="utf-8"))
    with (ROOT / "benchmarks" / "tasks.csv").open(encoding="utf-8") as handle:
        tasks = list(csv.DictReader(handle))
    return tasks, {(r["task_id"], r["algorithm"]): r for r in rows}


def cell(r: dict, expected: str) -> str:
    verdict = r["verdict"]
    mark = "*" if verdict not in ("TIMEOUT", "UNKNOWN") and verdict != expected else ""
    return f"{verdict}{mark} ({float(r['wall_seconds']):.1f}s)"


def global_table(tasks: list[dict], by_key: dict) -> tuple[list[str], dict]:
    counts = {}
    for algo in ALGOS:
        rs = [by_key[(t["task_id"], algo)] for t in tasks]
        times = [float(r["wall_seconds"]) for r in rs]
        counts[algo] = {
            "TRUE": sum(r["verdict"] == "TRUE" for r in rs),
            "FALSE": sum(r["verdict"] == "FALSE" for r in rs),
            "TIMEOUT": sum(r["verdict"] == "TIMEOUT" for r in rs),
            "UNKNOWN": sum(r["verdict"] == "UNKNOWN" for r in rs),
            "correct": sum(r["correctness"] == "correct" for r in rs),
            "wrong": sum(r["correctness"] == "wrong" for r in rs),
            "total": round(sum(times), 1),
            "avg": round(mean(times), 1),
        }
    lines = [
        "| 算法 | 证明安全 `TRUE` | 发现缺陷 `FALSE` | 超时 `TIMEOUT` | 未知 `UNKNOWN` | 正确判定 | 错误判定 | 平均耗时 (s) | 累计耗时 (s) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for algo in ALGOS:
        c = counts[algo]
        lines.append(
            f"| {LABELS[algo]} | {c['TRUE']} | {c['FALSE']} | {c['TIMEOUT']} | "
            f"{c['UNKNOWN']} | {c['correct']}/{len(tasks)} | {c['wrong']} | "
            f"{c['avg']} | {c['total']} |"
        )
    return lines, counts


def detail_table(tasks: list[dict], by_key: dict) -> list[str]:
    lines = [
        "| 任务 ID | 期望标签 | 源码行数 | 循环关键字 | BMC | k-Induction | Predicate | Impact |",
        "|---|---|---:|---:|---|---|---|---|",
    ]
    for t in tasks:
        exp = t["expected_verdict"].upper()
        cells = [cell(by_key[(t["task_id"], a)], exp) for a in ALGOS]
        lines.append(
            f"| `{t['task_id']}` | {exp} | {t['source_lines']} | {t['loop_keywords']} | "
            + " | ".join(cells)
            + " |"
        )
    return lines


def metrics_line(by_key: dict, task_id: str) -> dict:
    return {a: by_key[(task_id, a)] for a in ALGOS}


def stat(r: dict, key: str, default: str = "—") -> str:
    value = r.get(key)
    if value in (None, ""):
        return default
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def main() -> None:
    tasks, by_key = load()
    global_lines, counts = global_table(tasks, by_key)
    detail_lines = detail_table(tasks, by_key)

    case_id = "T02_bgrt"
    cex_id = "T23_kernelcapi"
    c = metrics_line(by_key, case_id)
    cex = by_key[(cex_id, "Predicate")]

    assignment_path = RESULTS / cex_id / "Predicate" / "Counterexample.1.assignment.txt"
    assignment_count = (
        len(assignment_path.read_text(encoding="utf-8", errors="replace").splitlines())
        if assignment_path.exists()
        else 0
    )
    trace_path = RESULTS / cex_id / "Predicate" / "Counterexample.1.txt"
    trace_count = (
        len(trace_path.read_text(encoding="utf-8", errors="replace").splitlines())
        if trace_path.exists()
        else 0
    )
    smt_path = RESULTS / cex_id / "Predicate" / "Counterexample.1.smt2"
    smt_assert_len = (
        max(
            (
                len(l)
                for l in smt_path.read_text(  # noqa: E741
                    encoding="utf-8", errors="replace"
                ).splitlines()
                if l.startswith("(assert")
            ),
            default=0,
        )
        if smt_path.exists()
        else 0
    )

    total_tasks = len(tasks)
    safe = sum(t["expected_verdict"] == "true" for t in tasks)
    buggy = sum(t["expected_verdict"] == "false" for t in tasks)

    # Additional differences worth reporting.
    diff_tasks = [
        t["task_id"]
        for t in tasks
        if len({by_key[(t["task_id"], a)]["verdict"] for a in ALGOS}) > 1
    ]
    bmctimeout_true = [
        t["task_id"]
        for t in tasks
        if by_key[(t["task_id"], "BMC")]["verdict"] == "TIMEOUT"
        and any(
            by_key[(t["task_id"], a)]["verdict"] == "TRUE"
            for a in ("kInduction", "Predicate", "Impact")
        )
    ]
    pi_diff = [
        (
            t["task_id"],
            by_key[(t["task_id"], "Predicate")],
            by_key[(t["task_id"], "Impact")],
        )
        for t in tasks
        if by_key[(t["task_id"], "Predicate")]["verdict"]
        != by_key[(t["task_id"], "Impact")]["verdict"]
    ]

    all_rows = list(by_key.values())
    unknown_tool = [
        r for r in all_rows if r["verdict"] == "UNKNOWN" and not r["failure_reason"]
    ]
    unknown_crash = [
        r for r in all_rows if r["verdict"] == "UNKNOWN" and r["failure_reason"]
    ]
    unknown_tool_str = ", ".join(
        f"`{r['task_id']}/{r['algorithm']}`" for r in unknown_tool[:12]
    ) + (" …" if len(unknown_tool) > 12 else "")
    unknown_crash_str = ", ".join(
        f"`{r['task_id']}/{r['algorithm']}` ({r['failure_reason']})"
        for r in unknown_crash[:12]
    ) + (" …" if len(unknown_crash) > 12 else "")

    pi_time_diff = sorted(
        [
            (
                t["task_id"],
                float(by_key[(t["task_id"], "Predicate")]["wall_seconds"]),
                float(by_key[(t["task_id"], "Impact")]["wall_seconds"]),
                by_key[(t["task_id"], "Predicate")]["verdict"],
                by_key[(t["task_id"], "Impact")]["verdict"],
            )
            for t in tasks
        ],
        key=lambda x: abs(x[1] - x[2]),
        reverse=True,
    )[:5]
    pi_time_lines = [
        "| 任务 | Predicate (s) | Impact (s) | 差值 (s) | 判定 |",
        "|---|---:|---:|---:|---|",
    ]
    for tid, pt, it, pv, iv in pi_time_diff:
        pi_time_lines.append(
            f"| `{tid}` | {pt:.1f} | {it:.1f} | {abs(pt - it):.1f} | P={pv}, I={iv} |"
        )

    bmc_list_str = ", ".join(f"`{x}`" for x in bmctimeout_true[:16]) + (
        " …" if len(bmctimeout_true) > 16 else ""
    )
    pi_diff_str = (
        (
            "："
            + ", ".join(
                f"`{t}` (Predicate={p['verdict']}, Impact={i['verdict']})"
                for t, p, i in pi_diff[:8]
            )
        )
        if pi_diff
        else ""
    )

    report = f"""# 《数理逻辑》大作业 · 第五题目实验复现报告

## SMT-based Software Model Checking: An Experimental Comparison of Four Algorithms

> 复现对象：Dirk Beyer, Matthias Dangl, *SMT-based Software Model Checking: An Experimental Comparison of Four Algorithms*, VSTTE 2016.
> 补充材料：<https://www.sosy-lab.org/research/k-ind-compare/index-vstte.html>
> 本报告中**所有判定结果、耗时与统计指标均来自本机实际运行 CPAchecker 产生的日志与 `Statistics.txt`**，未使用论文表格中的数值替代实验结果。

---

## 1. 实验设置

### 1.1 宿主机与容器约束

宿主机为 macOS（Apple Silicon M3 Pro, Fish Shell）。CPAchecker 1.6.8 附带的 MathSAT5 位精确求解器依赖 `libmathsat5j.so`，该动态库在补充包中为 `ELF 64-bit x86-64`，无法在 arm64 macOS 原生加载。因此**全部 112 次验证均在 `--platform linux/amd64` 的 Docker 容器内完成**：

| 项目 | 值 |
|---|---|
| 容器镜像 | `cpachecker-vstte:java8`（基于 `ubuntu:20.04` + `openjdk-8-jre-headless`） |
| 平台 | `linux/amd64`（容器内 `uname -m` = `x86_64`） |
| 工具 | 论文补充包内的 `cpachecker-1.6.8-vstte`（`benchmarks/supplements-vstte/CPAchecker`） |
| 求解器 | MathSAT5 5.3.12，`solver.solver=MATHSAT5`，位向量/浮点位精确编码 |
| Java | OpenJDK 8，`-heap 1000M -stack 2048k` |
| 单容器资源 | `--cpus 2 --memory 1400m`；并发 3 个容器 |
| 基准源码 | SoSy-Lab 官方仓库的 `svcomp16` 标签（SV-COMP 2016 冻结版），本地稀疏检出 3 个驱动目录 |
| 规约 | `benchmarks/unreach-call.prp`：`CHECK( init(main()), LTL(G ! call(__VERIFIER_error())) )` |

补充包来自论文官方发布页，本地解压为 `benchmarks/supplements-vstte/`，其中包含论文原始配置、测试集定义（`test/test-sets/*-bitprecise.xml`）与结果差异表；这些 XML 用于**核对四种算法的确切配置名与命令行参数**，而不是直接抄录结果。若该目录缺失，`bash demo/run.sh setup` 会从官方地址按需下载解压，不保留压缩包。

### 1.2 目录结构

```
cpa-exp/
├── benchmarks/
│   ├── supplements-vstte/CPAchecker/   # 论文附带 CPAchecker 1.6.8-vstte
│   ├── sv-comp16/c/                    # SV-COMP 2016 驱动源码（稀疏检出）
│   ├── unreach-call.prp                # 复现使用的规约
│   └── tasks.csv                       # 28 个任务清单（含 SHA-256）
├── results/<task_id>/<algo>/           # 112 个独立输出目录
├── scripts/                            # 选样、批跑、解析、报告生成脚本
└── report/
    ├── 实验复现报告.md            # 本报告
    └── 反例轨迹精简摘录.md  # 带源码行对照的反例精简轨迹
```

### 1.3 任务选取

从 `DeviceDriversLinux64` 对应的 `ldv-linux-3.0/`、`ldv-linux-3.4-simple/`、`ldv-commit-tester/` 三个目录中选出 **{total_tasks} 个任务**：**{safe} 个安全任务**（期望 `TRUE`）与 **{buggy} 个真实缺陷任务**（期望 `FALSE`）。选样依据：

1. 以 `sv-comp16` 文件名中的 `true-unreach-call` / `false-unreach-call` 标记作为 `expected_verdict` 的唯一依据；
2. 对照补充材料 `benchmarks/supplements-vstte/results/algorithms.DeviceDriversLinux64.diff.html`（论文原始结果差异表，勿与本项目根目录的 `results/` 混淆）中 BMC 与其余三种算法存在显著差异的驱动（如 `bgrt`、`kernelcapi`）；
3. 优先保留含 `while (1)` 主循环与 `__VERIFIER_nondet_int()` 分派的状态ful 驱动模型，使 BMC 的"无界循环上无法给出证明"特性可被观察；
4. 每个源码的 SHA-256 记录在 `benchmarks/tasks.csv`，保证可复算；
5. 用 `fnmatch` 把 28 个源码路径逐一匹配 `benchmarks/sv-comp16/c/DeviceDriversLinux64.set` 的通配符规则，**28/28 全部命中**。特别注意：该官方集合对 `ldv-linux-3.0/` 使用 `*_true-unreach-call*.i`（预处理文件），而对 `ldv-linux-3.4-simple/` 与 `ldv-commit-tester/` 使用 `*.c`；本实验严格按扩展名取文件，早期误取 `ldv-linux-3.0/*.c` 的 6 个任务已全部改用官方 `.i` 版本并重跑。`svcomp16` 标签下没有 `.yml`（该年度用 `.set` 定义任务），因此 `expected_verdict` 一律以文件名中的 `true/false-unreach-call` 标记为准。

### 1.4 四种算法的确切配置

以论文补充包的 `test/test-sets/*-bitprecise.xml` 为准，在容器内 `config/` 目录核对后得到：

| 算法 | CPAchecker 参数 | 说明 |
|---|---|---|
| BMC | `-bmc` + `cpa.bounds.maxLoopIterations=1`, `...UpperBound=0`, `...AdjusterFactory=INCREMENT` | 逐步增加展开深度 k 的有界模型检测 |
| k-Induction | `-sv-comp16--k-induction` | 并行组合：基础情形 / 归纳步 + 辅助不变式生成（`invariantGeneration-no-out.properties`） |
| Predicate Abstraction | `-predicateAnalysis-PredAbsRefiner-ABEl-bitprecise` | CEGAR + 谓词抽象 + ABE 块编码 + 插值精化 |
| Impact | `-predicateAnalysis-ImpactRefiner-ABEl-bitprecise` + `cpa.forcedCovering=...PredicateForcedCovering` | 基于插值的惰性抽象（Impact 算法） |

**通用参数**：`-64 -spec /work/benchmarks/unreach-call.prp -timelimit 90s -stats -setprop solver.solver=MATHSAT5`；位精确编码通过 `cpa.predicate.encodeBitvectorAs=BITVECTOR`、`encodeFloatAs=FLOAT` 设置；反例用 CBMC 二次确认（`analysis.checkCounterexamples=true`, `counterexample.checker=CBMC`）——k-Induction 的外层并行分析按论文原始配置不叠加 CBMC 包装（否则并行子线程会异常退出，见 §6）。

每次运行使用 `-outputpath /work/results/<task_id>/<algo>/` 隔离输出，因此 `Statistics.txt`、`CPALog.txt`、`Counterexample.*.txt`、`Counterexample.*.assignment.txt`、`run.log`、`metadata.json` 均不会互相覆盖。

---

## 2. 汇总结果

### 2.1 全局统计（{total_tasks} 个任务 × 4 种算法 = {total_tasks * 4} 次运行）

{chr(10).join(global_lines)}

> 耗时取 `Statistics.txt` / 日志中的 `Total time for CPAchecker`（墙钟秒）。`TIMEOUT` 表示日志出现 `The CPU-time limit of 90s has elapsed`（分析被中断）或被宿主硬超时终止；`UNKNOWN` 表示 CPAchecker 明确返回"incomplete analysis"但**并非**由时限触发（例如不支持的递归/工具异常）。`*` 表示判定与期望标签冲突。
>
> **耗时口径限制**：5 次崩溃运行没有 `Total time for CPAchecker`，改用宿主墙钟兜底；若统一剔除这 5 次，BMC 均值 64.2s（表中 62.9s）、Predicate 13.7s（表中 14.3s）、Impact 14.2s（表中 17.9s，**偏高约 20.8%**），k-Induction 不变。此外 33 次补跑使用了更大的堆与容器内存（GC 行为不同）。因此判定结果可比（CPU 时限统一 90s），但平均/累计耗时只能作数量级参考，不宜作精确性能比较。

### 2.2 单任务对比明细

{chr(10).join(detail_lines)}

> 单元格格式：`判定 (墙钟秒)`。完整数据见 `results/summary.csv`（宽表）、`results/summary_detail.csv`（长表，含全部统计指标）与 `results/summary_detail.json`。

### 2.3 整体有效性与效率分析

按本次实验数据统计：

| 观察 | 数据 |
|---|---|
| BMC 在安全任务上给出 `TRUE` 的次数 | {counts["BMC"]["TRUE"]} |
| BMC 超时/未知次数 | {counts["BMC"]["TIMEOUT"]} / {counts["BMC"]["UNKNOWN"]} |
| k-Induction 正确判定数 | {counts["kInduction"]["correct"]}/{total_tasks} |
| Predicate 正确判定数 | {counts["Predicate"]["correct"]}/{total_tasks} |
| Impact 正确判定数 | {counts["Impact"]["correct"]}/{total_tasks} |
| 四种算法判定不完全一致的任务数 | {len(diff_tasks)} / {total_tasks} |
| BMC 超时而其余算法至少一种证明 `TRUE` 的任务数 | {len(bmctimeout_true)} |

**结论 1（BMC 的能力边界）**：BMC 把程序展开 k 次后构造公式
`Φ_k = I(s0) ∧ ∧_{{i<k}} T(s_i, s_{{i+1}}) ∧ ∨_{{i≤k}} Err(s_i)`。
只有当 `Φ_k` 可满足时才能给出 `FALSE`；`UNSAT` 只说明"深度 k 以内无错误"，对无限循环程序**不能导出 ∀k 的安全性**。LDV 驱动的 `main` 是 `while (1)` 加非确定分派，因此 BMC 会不断提高 k 直到 CPU 时限耗尽，这正是本次实验中 BMC 在多数安全任务上 `TIMEOUT` 的原因。BMC 的理论优势是**找浅层缺陷快**：只要错误路径的展开深度小于 k 即可命中。不过本样本中 BMC 仅在 `T28_poseidon` 上给出 `FALSE`，其余 5 个缺陷任务因 CIL 递归不受支持而返回 `UNKNOWN`（见 §6.5），所以这一优势在本次数据上体现有限，不能据此断言 BMC 擅长找 bug。

**结论 2（k-Induction 的归纳证明）**：k-Induction 在基础情形之外，用
`Inv(s_i) ∧ T(s_i,s_{{i+1}}) ∧ ... ⇒ Inv(s_{{i+1}})` 的归纳步证明不变式，并把"循环头上的断言"当作归纳假设；配合辅助不变式生成（本次实验的 `Successful analysis: config/invariantGeneration-no-out.properties`），可在 `Bound k = 1` 就完成证明。代价是并行子分析需要额外 CPU，因而在大型驱动上更容易触及 90s 时限。

**结论 3（Predicate 与 Impact）**：两者都属于 CEGAR + 反例引导的插值精化，在本次样本上表现最接近且整体正确率最高。差异来自抽象状态的构造方式：Predicate 在每个抽象状态用 SMT 求解**全部**谓词的布尔组合（需要枚举模型 / 构造 BDD），Impact 从 `true` 开始，仅在覆盖检查失败时才沿 ART 的边用 Craig 插值把谓词**下推**到必要的节点，并用 forced covering 复用已覆盖的子树。因此理论上 Impact 的 SMT 求解次数更少，但覆盖检查/forced covering 更频繁；本次实验中 Impact 在 `T20_kbtab`、`T27_vhost_net` 上反而因该环节出现时限或内存失效（见 §6），说明这一权衡在超万行驱动上可能反转。

> 与论文的一致性：论文在 `DeviceDriversLinux64` 上的主要结论是"k-Induction 与基于插值的抽象在证明安全性上显著优于 BMC，而 BMC 在发现浅层缺陷上有成本优势"，本次 {total_tasks} 任务的小规模复现与该趋势一致。由于任务数（{total_tasks} vs 论文全集）、CPU 时限（90s vs 900s）和机器架构（amd64 模拟 vs 原生 x86_64）不同，**绝对数值不与论文直接比较**。还需注意：这 {total_tasks} 个任务是**按"能体现算法差异"人工精选**的（特意多选含 `while (1)` 的安全任务），并非随机抽样，因此下表各算法的正确判定比例带有选择偏差，**只能描述本样本，不能外推为整个 `DeviceDriversLinux64` 数据集上的总体正确率**。

---

## 3. 深度案例一：错误轨迹（Counterexample Trace Analysis）

### 3.1 案例选择与产物

选取 `{cex_id}`（`kernelcapi`，期望 `FALSE`），使用 `Predicate Abstraction` 的输出：

- 判定：`{cex["verdict"]}`，日志为 `{cex["cpachecker_verdict_line"]}`
- 耗时：`{cex["wall_seconds"]}s`（CPU `{cex["cpu_seconds"]}s`）
- 反例文件：`{cex["counterexample_files"]}`
- 关键统计：程序位置 `{stat(cex, "program_locations")}`、CFA 边 `{stat(cex, "cfa_edges")}`、循环 `{stat(cex, "loops")}`、精化次数 `{stat(cex, "refinements")}`、反例校验 `{stat(cex, "cex_checks")}` 次

`Counterexample.1.txt` 共 {trace_count} 行（含大量 `typedef` 与全局变量初始化边）；带源码行对照的精简摘录见 `report/反例轨迹精简摘录.md`。`Counterexample.1.assignment.txt` 给出 SMT 模型，`Counterexample.1.smt2` 是 MathSAT5 导出的路径公式。

### 3.2 被测驱动的状态机

该驱动是 Linux CAPI (ISDN) 子系统 `kernelcapi.ko` 的 LDV 模型。`main`（源码约 13929–14297 行）是一个 `while (1)` 环境循环：

```c
LDV_IN_INTERRUPT = 1;
ldv_initialize();
while (1) {{
    tmp___0 = __VERIFIER_nondet_int();        /* 是否退出循环，line 13977 */
    if (!tmp___0) {{ /* 检查各 file_operations 均已注销，否则继续 */ ... }}
    tmp = __VERIFIER_nondet_int();            /* 选择下一个被调用的回调，line 14020 */
    if (tmp == 0) goto case_0; ... if (tmp == 22) goto case_22; ...
    case_22: capi_driver_stop(...); goto switch_break;
}}
ldv_check_final_state();
```

其中互斥锁被抽象成一个二状态自动机（源码 7894、8000–8012 行）：

```c
int ldv_mutex = 1;                    /* 1 = 未加锁, 2 = 已加锁 */
void mutex_lock(...)      {{ ...; ldv_mutex = 2; }}
void mutex_unlock(...)    {{ if (ldv_mutex == 2) {{ ... }} else ldv_blast_assert(); ldv_mutex = 1; }}
void ldv_blast_assert()  {{ ERROR: __VERIFIER_error(); }}   /* line 7890 */
void ldv_check_final_state() {{ if (ldv_mutex != 1) ldv_blast_assert(); }}
```

`seq_file` 的 `start` 回调（`capi_driver_start`，`case_21`）负责 `mutex_lock`，`stop` 回调（`capi_driver_stop`，`case_22`，源码 13729–13734 行）负责 `mutex_unlock`。**规约要求二者成对出现**；LDV 的环境循环用非确定整数 `tmp` 任意选择回调，因此存在"未调用 start 就调用 stop"的非法序列。

### 3.3 SMT 变量赋值与路径约束

`Counterexample.1.assignment.txt`（共 {assignment_count} 行赋值记录）中的决定性赋值：

| SMT 变量 | 模型值 | 含义 |
|---|---|---|
| `__VERIFIER_nondet_int@2` | `4608` | 第一次非确定选择，`main::tmp___0@3 = 4608 ≠ 0`，故 `while (1)` **继续**循环而不退出 |
| `__VERIFIER_nondet_int@3` | `22` | 第二次非确定选择，`main::tmp@3 = 22`，分派到 `case_22` |
| `main::tmp@3` | `22` | 回调编号 |
| `main::tmp___0@3` | `4608` | 循环继续标志 |
| `ldv_mutex@2` | `1` | 全局锁状态：**未加锁**（初值，未经过任何 `mutex_lock`） |
| `res_seq_capi_driver_open_19@2` 等 | `0` | 各 `file_operations` 注册标志均未置位 |
| `__ADDRESS_OF_capi_drivers_lock` | `9007199791611904` | 位精确 64 位地址常量 |

`Counterexample.1.smt2` 是位精确 SMT-LIB2 公式：变量被声明为 `(_ BitVec 32)` / `(_ BitVec 64)`，例如 `ldv_mutex@2`、`|main::tmp@3|` 均为 32 位位向量，指针为 64 位。整条路径被编码为单个 {smt_assert_len} 字符的 `(assert (let (...) ...))` 嵌套合取，其关键子式（按出现顺序）为：

```lisp
(let ((.def_530  (= ldv_mutex@2 (_ bv1 32))))                 ; 初值：未加锁
(let ((.def_1444 (= __VERIFIER_nondet_int@2 |main::tmp___0@3|)))
(let ((.def_1445 (= |main::tmp___0@3| (_ bv0 32))))
(let ((.def_1448 (not .def_1445)))                            ; ¬(tmp___0 = 0)：循环继续
(let ((.def_1527 (= __VERIFIER_nondet_int@3 |main::tmp@3|)))
(let ((.def_1529 (= |main::tmp@3| (_ bv0 32)))) (not ...))    ; ¬(tmp = 0)
...
(let ((.def_1639 (= |main::tmp@3| (_ bv22 32))))               ; tmp = 22 → case_22
(let ((.def_1718 (= ldv_mutex@2 (_ bv2 32))))
(let ((.def_1721 (not .def_1718)))                             ; ¬(ldv_mutex = 2) → 断言失败分支
```

于是路径约束的合取可简化为：

```
tmp___0 ≠ 0  ∧  tmp = 22  ∧  ldv_mutex = 1  ∧  ¬(ldv_mutex = 2)
```

它显然 **SAT**，MathSAT5 给出的模型即上表；CBMC 反例校验 1 次、不可行路径 0 次（`Number of counterexample checks: 1`, `Number of infeasible paths: 0`），确认该反例是**真实可行路径**而非抽象假阳。

### 3.4 从 `main` 到 `__VERIFIER_error()` 的逐步控制流

下表按 `Counterexample.1.txt` 的 CFA 边顺序给出（完整 65 步见 `report/反例轨迹精简摘录.md`）：

| 步 | 源码行 | CFA 边 / 路径条件 | 状态变化 |
|---:|---|---|---|
| 1 | 7894 | `INIT GLOBAL VARS` / `int ldv_mutex = 1;` | `ldv_mutex = 1`，所有 `res_seq_*_open_* = 0` |
| 2 | 13966 | `ldv_initialize();` | 环境初始化 |
| 3 | 13977 | `tmp___0 = __VERIFIER_nondet_int();` | 模型取 `4608` |
| 4 | 13979 | `[!(tmp___0 == 0)]` | `4608 ≠ 0` 成立 → **不退出** `while (1)` |
| 5 | 14020 | `tmp = __VERIFIER_nondet_int();` | 模型取 `22` |
| 6–28 | 14022–14085 | `[!(tmp == 0)] … [!(tmp == 21)]` | 前 22 个 `if` 分支逐一被否定 |
| 29 | 14088 | `[tmp == 22]` | 命中 `case_22` |
| 30 | 14089 / 14254 | `Goto: case_22` → `Label: case_22` | 进入回调分派目标 |
| 31 | 14256 | `capi_driver_stop(var_group1, var_capi_driver_stop_17_p1)` | **调用 `stop` 回调，但从未调用过 `start`** |
| 32 | 13731 | `mutex_unlock(&capi_drivers_lock)` | 进入锁模型 |
| 33 | 8003 | `[!(ldv_mutex == 2)]`，模型 `ldv_mutex == 1` | 期望"已加锁"，实际"未加锁"，走 `else` 分支 |
| 34 | 8007 | `ldv_blast_assert()` | 调用断言失败处理 |
| 35 | 7890 | `Label: ERROR` → `__VERIFIER_error();` | 到达规约禁止的 `call(__VERIFIER_error())`，判定 `FALSE` |

**驱动状态转换视角**：锁状态机的合法迁移是 `1 --mutex_lock--> 2 --mutex_unlock--> 1`。本轨迹中状态始终停留在 `1`，却在 `1` 上执行了只应从 `2` 出发的 `mutex_unlock` 迁移；`ldv_check_final_state()` 与 `ldv_blast_assert()` 把这条"API 使用规约违背"编码成可达的 `ERROR` 标签。由于规约是 `LTL(G ! call(__VERIFIER_error()))`，存在一条到达 `ERROR` 的有限路径即构成 `FALSE` 反例。

**算法视角**：Predicate Abstraction 只需 1 次 CEGAR 精化、0 个由插值新发现的谓词（`Number of predicate refinements: 0`）就沿一条具体路径直达目标状态——因为这是**存在性**问题：`∃` 一条路径使 `Φ` 可满足。这与 §2.3 中 BMC 在安全任务上必须处理**全称**问题 `∀k ¬Φ_k` 形成鲜明对照，也解释了为何"找 bug"普遍比"证明安全"容易。

---

## 4. 深度案例二：算法结果差异（Algorithmic Difference Case Study）

### 4.1 案例：`{case_id}`（`bgrt`，ACPI BGRT 表驱动）

四种算法在同一次批跑中的实测结果：

| 算法 | 判定 | 墙钟耗时 | Bound k | 精化次数 | 关键统计 |
|---|---|---:|---:|---:|---|
| BMC | {c["BMC"]["verdict"]} | {c["BMC"]["wall_seconds"]}s | {stat(c["BMC"], "bound_k")} | — | 展开到第 {stat(c["BMC"], "bound_k")} 层后 CPU 时限耗尽 |
| k-Induction | {c["kInduction"]["verdict"]} | {c["kInduction"]["wall_seconds"]}s | {stat(c["kInduction"], "bound_k")} | — | 并行分析 {stat(c["kInduction"], "number_of_algorithms")} 路，成功者 `{stat(c["kInduction"], "successful_analysis")}` |
| Predicate | {c["Predicate"]["verdict"]} | {c["Predicate"]["wall_seconds"]}s | — | {stat(c["Predicate"], "refinements")} | 发现谓词 {stat(c["Predicate"], "predicates_discovered")} 个，SMT sat 检查 {stat(c["Predicate"], "smt_sat_checks")} 次 |
| Impact | {c["Impact"]["verdict"]} | {c["Impact"]["wall_seconds"]}s | — | {stat(c["Impact"], "refinements")} | 发现谓词 {stat(c["Impact"], "predicates_discovered")} 个，SMT sat 检查 {stat(c["Impact"], "smt_sat_checks")} 次 |

BMC 的 `Total time for CPAchecker` 约为其余三者的 **{float(c["BMC"]["wall_seconds"]) / max(float(c["kInduction"]["wall_seconds"]), 0.001):.0f} 倍**（k-Induction 对比）与 **{float(c["BMC"]["wall_seconds"]) / max(float(c["Impact"]["wall_seconds"]), 0.001):.0f} 倍**（Impact 对比），且依旧只得到 CPAchecker 的 `UNKNOWN, incomplete analysis`（本报告按时限归类为 `TIMEOUT`）；其余三种算法在数秒内给出完备的 `TRUE` 证明。

### 4.2 源码结构：为什么 BMC 无法收敛

`32_1_cilled_true-unreach-call_ok_nondet_linux-3.4-32_1-drivers--acpi--bgrt.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c`（3425 行）的 `main`（3208–3273 行）：

```c
void main(void) {{
  LDV_IN_INTERRUPT = 1;
  ldv_initialize();
  tmp___7 = bgrt_init();
  if (tmp___7) goto ldv_final;

  while (1) {{                              /* line 3231 */
    tmp___9 = __VERIFIER_nondet_int();      /* line 3234：是否退出 */
    if (tmp___9) {{ /* 继续 */ }} else goto while_break;
    tmp___8 = __VERIFIER_nondet_int();      /* line 3242：选择回调 */
    if (tmp___8 == 0) {{ show_image(...); }} /* 唯一回调，不改锁状态 */
  }}
  bgrt_exit();
ldv_final:
  ldv_check_final_state();                  /* main line 3271；定义见 3404，要求 ldv_mutex == 1 */
}}
```

结构特征：

1. **无界循环**：`while (1)` 的退出由非确定整数 `tmp___9` 控制，不存在静态上界；循环体可以执行任意多轮。
2. **循环体几乎不改变状态**：唯一回调 `show_image` 只读取 BGRT 表；`ldv_mutex` 在整个循环中保持初值 `1`。
3. **错误点是"最终状态检查"**：`ldv_blast_assert()` 只可能由 `ldv_check_final_state()` 在 `ldv_mutex ≠ 1` 时触发，而这一点需要跨任意多轮循环的不变式才能排除。

对任意给定的 k，BMC 只能证明"前 k 轮内不违规"；由于 `tmp___9` 可取任意非零值，公式 `Φ_k` 对每个 k 都 UNSAT，但**没有任何有限的 k 能推出 ∀k**。`bgrt` 的 BMC `Statistics.txt` 给出了这一过程的精确代价分解：

| 指标 | 本次实测值 | 含义 |
|---|---:|---|
| `Bound k` | {stat(c["BMC"], "bound_k")} | 时限内达到的展开深度 |
| `Maximum loop iteration reached` | {stat(c["BMC"], "max_loop_iteration")} | 循环实际被展开的最大次数 |
| `Time for BMC formula creation` | {stat(c["BMC"], "bmc_formula_time")}s | 构造位向量路径公式 |
| `Time for final sat check` | {stat(c["BMC"], "final_sat_check_time")}s | 错误路径存在性查询（每轮 UNSAT，极快） |
| **`Time for bounding assertions check`** | **{stat(c["BMC"], "bounding_assertions_time")}s** | **判断"是否还有执行超过当前 k 轮"，每轮 SAT → 必须继续增大 k** |
| `Time for Analysis` | {stat(c["BMC"], "analysis_time")}s | 分析总时长 |
| `Number of target states` | {stat(c["BMC"], "target_states")} | 展开后到达的错误状态数（0 表示未发现违规） |

可见绝大部分 CPU 时间（{stat(c["BMC"], "bounding_assertions_time")}s / {stat(c["BMC"], "analysis_time")}s）花在 `checkBoundingAssertions` 上：它必须证明"已完全展开"才能**可靠地**返回 `TRUE`。在 `bgrt` 上该检查始终可满足，k 便一路增长到 {stat(c["BMC"], "bound_k")} 直到 90s CPU 时限耗尽，最终只输出 `UNKNOWN, incomplete analysis`（本报告归类为 `TIMEOUT`）。

> 反例对照（说明 BMC 并非"永远不会返回 TRUE"）：在 `T14_vfb` 上，日志显示 BMC 于 `Bound k = 1`、`Maximum loop iteration reached = 2` 时执行了 `Starting assertions check`，随后在 {stat(by_key[("T14_vfb", "BMC")], "wall_seconds")}s 返回 `TRUE` 且未触发 CPU 时限。按 `AbstractBMCAlgorithm.checkBoundingAssertions` 的语义，这意味着边界断言为 UNSAT（不存在超过当前 k 的执行）；**日志本身并未显式打印 UNSAT 字样，此为依据算法语义的推断**。这说明 BMC 的能力边界取决于**能否证明循环被完全展开**，而不只是"程序有没有循环"。本次样本中绝大多数 LDV 驱动的主循环带非确定退出条件，因此该检查无法在有限 k 内通过。

### 4.3 其余三种算法为什么能证明

**k-Induction**：把问题从 `∀k` 转化为有限的两步检查。

- 基础情形（base case）：对 k=1 做 BMC，验证 `I(s0) ⇒ ¬Err(s1)`；
- 归纳步（step case）：在循环头假设"前 k 步安全"，用 SMT 证明第 k+1 步仍安全；对循环内的 `ldv_mutex` 这个循环不变量，归纳步公式
  `ldv_mutex = 1 ∧ T(s_i, s_{{i+1}}) ⇒ ldv_mutex' = 1`
  是**归纳成立**的，因为循环体不写 `ldv_mutex`。
- 辅助不变式生成（并行第 2 路 `invariantGeneration-no-out.properties`）用基于模板/数据流的不变式把 `ldv_mutex = 1` 提供给归纳步。`Statistics.txt` 显示 `Number of algorithms used: {stat(c["kInduction"], "number_of_algorithms")}`、`Successful analysis: {stat(c["kInduction"], "successful_analysis")}`、`Bound k: {stat(c["kInduction"], "bound_k")}` —— **归纳深度 1 即完成**，因此 `TRUE` 只需 {c["kInduction"]["wall_seconds"]}s。

**Predicate Abstraction（CEGAR + Craig 插值）**：从空谓词集出发，沿抽象可达图找到一条"伪反例"，用 CBMC/求解器判定其可行性；若不可行，对路径公式 `A ∧ B`（A 为前缀、B 为后缀）求 Craig 插值 `I` 满足 `A ⇒ I` 且 `I ∧ B` 不可满足，把 `I` 中出现的原子谓词加入精度并重新抽象。对 `bgrt`，只需 `{stat(c["Predicate"], "refinements")}` 次精化、`{stat(c["Predicate"], "predicates_discovered")}` 个谓词（本质即 `ldv_mutex = 1`）即可把抽象状态空间收紧到能证明覆盖：`Number of SMT sat checks: {stat(c["Predicate"], "smt_sat_checks")}`、`Time for refinements: {stat(c["Predicate"], "refinement_time")}s`、`Number of loops: {stat(c["Predicate"], "loops")}`、程序位置 `{stat(c["Predicate"], "program_locations")}`。

**Impact（惰性抽象）**：不在每个节点上求全部谓词的抽象后置，而是把 ART 节点初始标记为 `true`；只有当某节点可能被覆盖时才用插值把谓词沿路径**逐个下推**，并用 `forced covering` 让已证明安全的子树被整体复用。`Statistics.txt` 中 `Number of refinements: {stat(c["Impact"], "refinements")}`、`Number of SMT sat checks: {stat(c["Impact"], "smt_sat_checks")}`、`Attempted forced coverings` 等字段反映了这一策略。对 `bgrt` 这种"循环体不改变锁状态"的程序，覆盖检查可以迅速把整个无限循环折叠为有限 ART，因此耗时最短（{c["Impact"]["wall_seconds"]}s）。

> 说明：CPAchecker 1.6.8 的 `Statistics.txt` **不单独导出"Craig 插值调用次数"**这一计数器（配置中的插值由 `PredicateAbstractionRefiner` 内部完成）；本实验可观测且与插值直接相关的代理指标是 `Number of refinements` / `Number of successful refinements` / `Number of predicate refinements` / `Number of predicates discovered` / `Time for refinements`，上表与 `results/summary_detail.csv` 均如实记录这些字段，未虚构插值次数。

### 4.4 根本原因小结

差异不来自求解器（四者均为 MathSAT5 位精确），而来自**证明义务的量词结构**：

| 算法 | 证明义务 | 在 `bgrt` 上的后果 |
|---|---|---|
| BMC | `∃k ≤ K: Φ_k` SAT？ 只能证伪 | 无界循环 → 有限 K 内 UNSAT 无意义 → 超时 |
| k-Induction | `I ∧ T ⇒ I'`（归纳不变式） | `ldv_mutex = 1` 归纳成立 → k=1 即证 |
| Predicate | CEGAR 用插值构造不变式谓词 | 1 次精化得到同一不变式 → 快速证 |
| Impact | 惰性下推插值 + forced covering | 无限循环被折叠覆盖 → 最快 |

### 4.5 其他差异任务

四种算法判定不完全一致的任务共 **{len(diff_tasks)}** 个，其中 BMC 超时而其余算法至少有一种证明 `TRUE` 的共 **{len(bmctimeout_true)}** 个：
{bmc_list_str}。

Predicate 与 Impact 判定出现分歧的任务共 **{len(pi_diff)}** 个{pi_diff_str}。需强调：`T20_kbtab/Impact` 的 `TIMEOUT` 并非证明能力不足——其日志显示 CPU 时限触发时 CPAchecker 正卡在 `InterpolationManager.buildCounterexampleTrace` / `PredicateForcedCovering.tryForcedCovering` 生成插值反例轨迹，属 Impact 特有的 forced-covering 开销与 90s 资源限制叠加的结果。其余 27 个任务上两者判定完全一致，差异主要体现在耗时；绝对耗时差最大的 5 个任务为：

{chr(10).join(pi_time_lines)}

由此可见：Impact 的惰性插值/覆盖策略在"状态空间较大但不变式简单"的驱动上通常更快；而 Predicate 在需要较多谓词组合枚举时才显现额外开销。个别任务上两者同时触及 90s 时限，差值不具统计意义。

---

## 5. 复现步骤（一键重跑）

**推荐入口**：`demo/run.sh` 封装了环境自检、幂等准备、冒烟测试与正式实验，冒烟测试写入独立的 `demo/smoke_results/`，不会污染正式 `results/`。

```bash
bash demo/run.sh check     # 环境自检（含容器内 x86_64 平台核验）
bash demo/run.sh setup     # 幂等准备：镜像 / 补充包 / 源码 / 任务清单
bash demo/run.sh smoke     # 冒烟测试：2 任务 × 4 算法，约 2 分钟
bash demo/run.sh full      # 正式实验：112 次运行 + 统计 + 报告
bash demo/run.sh report    # 只重新生成统计表与报告

# 从头完整重跑（覆盖已有 run.log / metadata.json）
RERUN=1 bash demo/run.sh full
# 更保守的资源档位（更少 OOM，耗时更长）
WORKERS=2 MEMORY=2400 HEAP=1800 bash demo/run.sh full
# 只查看将执行的命令
DRY_RUN=1 bash demo/run.sh full
```

等价的手动命令链如下（不使用 `demo/run.sh` 时）：

```bash
# 1. 基础镜像与论文补充包
docker pull --platform linux/amd64 ubuntu:20.04
docker build --platform linux/amd64 -t cpachecker-vstte:java8 scripts/docker
curl -L --fail --retry 2 \\
  https://www.sosy-lab.org/research/k-ind-compare/supplements-vstte.tar.bz2 \\
  | tar -xj -C benchmarks

# 2. SV-COMP 2016 源码（稀疏检出，避免全量下载）
git clone --depth 1 --branch svcomp16 --filter=blob:none --sparse \\
  https://gitlab.com/sosy-lab/benchmarking/sv-benchmarks.git benchmarks/sv-comp16
git -C benchmarks/sv-comp16 sparse-checkout set --skip-checks \\
  c/properties/unreach-call.prp c/ldv-linux-3.0 c/ldv-linux-3.4-simple c/ldv-commit-tester

# 3. 选样 / 批跑 / 解析 / 报告
python3 scripts/select_tasks.py
python3 scripts/run_experiments.py --workers 3 --timelimit 90 \
  --hard-timeout 400 --memory 1800 --heap 1400
python3 scripts/parse_results.py
python3 scripts/make_trace_excerpt.py
python3 scripts/build_report.py
```

单任务单算法可单独运行：`python3 scripts/run_experiments.py --tasks T02_bgrt --algos BMC kInduction --rerun`。

---

## 6. 局限性与工程注意事项

1. **架构与性能**：amd64 容器在 Apple Silicon 上经指令翻译运行，绝对耗时高于原生 x86_64；CPU 时限 90s 与论文 900s 不同，故只做趋势性对照，不做绝对数值对比。更关键的是资源量级：论文补充包的四个 test-set XML 均为 `memlimit="15000 MB"`、`-heap 10000M`，而本实验 Docker 虚拟机总内存仅 5.85 GB、Java 堆 1–4 GB。**4 次 OOM 与相当一部分 TIMEOUT 主要源于这一 2.5–10 倍的堆/内存差距，而非算法固有的证明能力上限**，不能据此断言这些算法无法处理相应驱动。
2. **k-Induction 配置陷阱**：最初把 `analysis.checkCounterexamples=true` / `counterexample.checker=CBMC` 叠加到外层 `-sv-comp16--k-induction` 并行配置时，日志出现 `ParallelAlgorithm.handleFutureResults: unexpected exception` 并返回虚假的 `UNKNOWN`。按补充包 `test/test-sets/k-induction-bitprecise.xml` 的原始配置去掉外层 CBMC 包装、保留 `limits.time.cpu.thread=10000s` 后，k-Induction 恢复为正常的 `TRUE`（见 `results/T02_bgrt/kInduction/run.log`）。这说明**工具异常必须与算法结论严格区分**，本报告已将所有非时限型 `UNKNOWN` 单独归类。
3. **宿主硬超时**：个别大任务在 CPAchecker 已触发 90s CPU 时限后的清理阶段被宿主硬超时终止，日志缺少最终的 `Verification result` 行；这类运行按 `TIMEOUT` 统计，并在 `metadata.json` 中以 `outer_timeout: true` 标记；后续已用更大的硬超时补跑（见第 6 条）。
4. **插值计数器缺失**：见 §4.3 说明，`Statistics.txt` 不含独立的 Craig 插值次数，报告使用精化/谓词计数作为可观测代理。
5. **`UNKNOWN` 的语义**：本次共 {len(unknown_tool)} 次 `UNKNOWN` 是 CPAchecker 明确返回的"incomplete analysis"：{unknown_tool_str or "无"}，日志均含 `Unsupported feature (recursion)`（例如 `T23_kernelcapi/BMC` 第 11605 行 `protocol_message_2_pars`、`T24_p54usb` 第 10959 行 `p54u_resume` 函数指针递归、`T25_libfc/BMC` 第 15567 行 `fc_exch_release`）。这是 CPAchecker 1.6.8 对 CIL 转换后递归调用的处理限制，**不是"算法证明程序安全"**。另有 {len(unknown_crash)} 次 `UNKNOWN` 来自工具/资源失效（无最终判定行）：{unknown_crash_str or "无"}。两类都单独归为 `UNKNOWN`，绝不冒充 `TRUE`。
6. **失效运行的处置**：首轮批跑出现 5 次宿主硬超时（`rc=124`，CPAchecker 已触发 90s CPU 时限但清理阶段被 150s 墙钟硬超时截断）与 6 次异常退出（5 次容器/Java 堆内存不足 `rc=137` 或 `OutOfMemoryError`，集中在 `T25_libfc`、`T26_usb_storage`、`T27_vhost_net` 等超万行驱动；1 次 `T27_vhost_net/kInduction` 在 `ARGPathExporter.writeProofWitness` 导出证明见证时被 CPAchecker 自身的 10s 强制终止逻辑打断，日志中已可见 `Error path found and confirmed by counterexample check with CBMC`）。这些运行**不参与算法结论**，而是用 `--hard-timeout 300~400`、容器内存 2000–4800 MB、Java 堆 1500–4000 MB 分 8 组补跑；其中 4 次运行在 Docker 虚拟机 5.85 GB 总内存上限下仍被 OOM 终止，最终如实记为 `UNKNOWN`；`metadata.json` 中保留 `returncode`、`outer_timeout`、`container_memory_mb`、`java_heap_mb` 供审计。
7. **标签来源与版本边界**：`expected_verdict` 一律以 `svcomp16` 文件名中的 `true/false-unreach-call` 标记为准（该年度用 `.set` 定义任务，没有 `.yml`）；全部 112 次运行均只使用 `benchmarks/sv-comp16/` 的源码与 `benchmarks/unreach-call.prp`（`call(__VERIFIER_error())`）。上游仓库的后续版本把错误函数改名为 `reach_error()`、规约公式改为 `LTL(G ! call(reach_error()))`，并在源码末尾引入 `model/*.env.c` 环境模型，与本次规约不兼容，故未纳入实验，也不存在混用。
8. **结果目录的残留文件**：补跑采用 `--rerun`（直接覆盖 `run.log` / `metadata.json` 等，不删除旧文件），因此少数目录存在早于本次运行时间戳的输出，例如 `T17_pppox/BMC/Counterexample.1.txt`（`.c` 版本运行时产生）与 `T25_libfc/BMC/Counterexample.1.txt`（首轮超时运行产生）。**判定结论全部取自本次 `run.log`，不受残留文件影响**；但在引用反例文件时必须核对时间戳，且应优先以 `FALSE` 判定的目录为准。此外有 6 次 `UNKNOWN` 的 BMC 运行也导出了 `Counterexample.1.*`（工具在遇到不支持的递归时写出的潜在错误路径），这些不是经过确认的反例。

---

## 7. 交付物清单

| 文件 | 内容 |
|---|---|
| `report/实验复现报告.md` | 完整实验报告（实验设置、全局统计、深入案例与局限说明） |
| `report/实验结果汇总.md` | 全局统计表 + 单任务明细表（报告目录副本，便于单独阅读） |
| `report/反例轨迹精简摘录.md` | 反例轨迹精简摘录（含 65 步源码行与模型赋值，视频演示专用） |
| `report/算法结果差异演示.md` | 算法结果差异深度解析（T02_bgrt 案例与全局差异，视频演示专用） |
| `report/口播稿.md` | 工具运行讲解视频录制脚本与演示操作指引 |
| `results/summary.csv` | 单任务宽表（4 算法判定 + 耗时） |
| `results/summary_detail.csv` / `.json` | 逐次运行的全部统计指标 |
| `results/summary.md` | 全局统计表 + 单任务明细表（原始导出） |
| `results/<task>/<algo>/run.log`, `Statistics.txt`, `Counterexample.*` | 112 次运行的原始产物 |
| `benchmarks/tasks.csv` | 任务清单与 SHA-256 |
| `scripts/*.py`, `scripts/docker/Dockerfile` | 全部可复现脚本 |
| `demo/run.sh` | 一键运行入口：`check` / `setup` / `smoke` / `full` / `report` |
| `demo/smoke_results/` | 冒烟测试产物（与正式结果隔离） |

---

*报告由 `scripts/build_report.py` 依据 `results/summary_detail.json` 自动生成；所有数值均可回溯到对应的 `run.log` / `Statistics.txt`。*
"""
    (ROOT / "report" / "实验复现报告.md").write_text(report, encoding="utf-8")
    print(f"Wrote report/实验复现报告.md ({len(report)} chars)")
    print(
        f"  tasks={total_tasks}, differing={len(diff_tasks)}, bmc_timeout_but_true={len(bmctimeout_true)}, P/I verdict diffs={len(pi_diff)}"
    )


if __name__ == "__main__":
    main()
