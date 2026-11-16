#!/usr/bin/env python3
"""Parse CPAchecker run.log / Statistics.txt artifacts into summary tables.

The parser is deliberately strict about the origin of a verdict: it only
accepts the line "Verification result: ..." printed by CPAchecker itself, and
distinguishes UNKNOWN caused by the CPU-time limit (reported as TIMEOUT) from
UNKNOWN caused by unsupported features / tool exceptions.
"""

from __future__ import annotations

import csv
import json
import re
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
ALGOS = ("BMC", "kInduction", "Predicate", "Impact")

VERDICT_RE = re.compile(r"^Verification result:\s*(TRUE|FALSE|UNKNOWN)", re.M)
TIME_RE = re.compile(r"^Total time for CPAchecker:\s*([\d.]+)s", re.M)
CPU_TIME_RE = re.compile(r"^Total CPU time for CPAchecker:\s*([\d.]+)s", re.M)
TIMEOUT_RE = re.compile(r"CPU-time limit of .*? has elapsed", re.I)

# Statistics.txt keys recorded for the in-depth case studies.
METRIC_PATTERNS = OrderedDict(
    [
        ("bound_k", r"^Bound k:\s*(\d+)"),
        ("program_locations", r"^Number of program locations:\s*(\d+)"),
        ("cfa_edges", r"^Number of CFA edges:\s*(\d+)"),
        ("loops", r"^Number of loops:\s*(\d+)"),
        ("reached_locations", r"^  Number of reached locations:\s*(\d+)"),
        ("refinements", r"^Number of refinements:\s*(\d+)"),
        ("successful_refinements", r"^Number of successful refinements:\s*(\d+)"),
        ("predicate_refinements", r"^Number of predicate refinements:\s*(\d+)"),
        ("predicates_discovered", r"^Number of predicates discovered:\s*(\d+)"),
        ("smt_sat_checks", r"^Number of SMT sat checks:\s*(\d+)"),
        ("coverage_checks", r"^Number of coverage checks:\s*(\d+)"),
        ("max_abe_block", r"^Max ABE block size:\s*(\d+)"),
        ("bmc_formula_time", r"^Time for BMC formula creation:\s*([\d.]+)s"),
        (
            "bounding_assertions_time",
            r"^Time for bounding assertions check:\s*([\d.]+)s",
        ),
        ("final_sat_check_time", r"^Time for final sat check:\s*([\d.]+)s"),
        ("max_loop_iteration", r"^Maximum loop iteration reached:\s*(\d+)"),
        ("target_states", r"^  Number of target states:\s*(\d+)"),
        ("refinement_time", r"^Time for refinements:\s*([\d.]+)s"),
        ("smt_solver_time", r"^Total time for SMT solver \(w/o itp\):\s*([\d.]+)s"),
        ("analysis_time", r"^Time for Analysis:\s*([\d.]+)s"),
        ("cex_checks", r"^Number of counterexample checks:\s*(\d+)"),
        ("number_of_algorithms", r"^Number of algorithms used:\s*(\d+)"),
        ("successful_analysis", r"^Successful analysis:\s*(.+)$"),
    ]
)


def parse_statistics(path: Path) -> dict[str, object]:
    metrics: dict[str, object] = {}
    if not path.exists():
        return metrics
    text = path.read_text(encoding="utf-8", errors="replace")
    for key, pattern in METRIC_PATTERNS.items():
        match = re.search(pattern, text, re.M)
        if not match:
            continue
        value = match.group(1).strip()
        metrics[key] = float(value) if re.fullmatch(r"[\d.]+", value) else value
    return metrics


def parse_one(task_id: str, algo: str, expected: str) -> dict[str, object]:
    out = RESULTS / task_id / algo
    meta_path = out / "metadata.json"
    log_path = out / "run.log"
    stats_path = out / "Statistics.txt"
    metadata = (
        json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    )
    log = (
        log_path.read_text(encoding="utf-8", errors="replace")
        if log_path.exists()
        else ""
    )

    match = VERDICT_RE.search(log)
    raw = match.group(1) if match else None
    timed_out = bool(TIMEOUT_RE.search(log)) or bool(metadata.get("outer_timeout"))
    not_run = not meta_path.exists() and not log_path.exists()
    if not_run:
        verdict = "NOT_RUN"
    elif raw in ("TRUE", "FALSE"):
        verdict = raw
    elif timed_out:
        # The CPAchecker CPU-time limit fired, or the host killed the container.
        verdict = "TIMEOUT"
    elif raw is None:
        # No verdict line at all: tool crash / container OOM, not an algorithm result.
        verdict = "UNKNOWN"
    else:
        verdict = "UNKNOWN"

    rc = metadata.get("returncode")
    if timed_out:
        failure_reason = (
            "cpu_time_limit" if TIMEOUT_RE.search(log) else "host_hard_timeout"
        )
    elif rc == 137:
        failure_reason = "container_memory_limit"
    elif rc == 1 and "OutOfMemoryError" in log:
        failure_reason = "java_heap_oom"
    elif rc not in (0, None):
        failure_reason = "tool_exception"
    else:
        failure_reason = ""

    wall = TIME_RE.search(log)
    cpu = CPU_TIME_RE.search(log)
    runtime = (
        float(wall.group(1)) if wall else float(metadata.get("wall_seconds") or 0.0)
    )
    cpu_runtime = (
        float(cpu.group(1)) if cpu else float(metadata.get("wall_seconds") or 0.0)
    )

    counterexamples = sorted(
        p.name for p in out.glob("Counterexample.*") if p.is_file()
    )
    metrics = parse_statistics(stats_path)
    metrics.update(
        {
            "task_id": task_id,
            "algorithm": algo,
            "expected_verdict": expected.upper(),
            "verdict": verdict,
            "wall_seconds": round(runtime, 3),
            "cpu_seconds": round(cpu_runtime, 3),
            "outer_timeout": bool(metadata.get("outer_timeout")),
            "failure_reason": failure_reason,
            "returncode": metadata.get("returncode"),
            "container_memory_mb": metadata.get("container_memory_mb"),
            "java_heap_mb": metadata.get("java_heap_mb"),
            "cpachecker_verdict_line": (match.group(0) if match else ""),
            "counterexample_files": ";".join(counterexamples),
            "has_assignment": any("assignment" in name for name in counterexamples),
        }
    )
    if verdict == "NOT_RUN":
        metrics["correctness"] = "not_run"
    elif verdict == expected.upper():
        metrics["correctness"] = "correct"
    elif verdict in ("TIMEOUT", "UNKNOWN"):
        metrics["correctness"] = "inconclusive"
    else:
        metrics["correctness"] = "wrong"
    return metrics


def fmt(value: object) -> str:
    return "" if value is None or value == "" else str(value)


def verdict_cell(verdict: str, seconds: float, expected: str) -> str:
    mark = (
        ""
        if verdict in ("TIMEOUT", "UNKNOWN", "NOT_RUN")
        else ("*" if verdict != expected else "")
    )
    return f"{verdict}{mark} ({seconds:.1f}s)"


def main() -> None:
    with (ROOT / "benchmarks" / "tasks.csv").open(encoding="utf-8") as handle:
        tasks = list(csv.DictReader(handle))

    rows = [
        parse_one(task["task_id"], algo, task["expected_verdict"])
        for task in tasks
        for algo in ALGOS
    ]
    by_key = {(r["task_id"], r["algorithm"]): r for r in rows}

    # ---- results/summary.csv : one row per task, wide format ----
    wide_fields = [
        "task_id",
        "short_name",
        "category",
        "expected_verdict",
        "source_lines",
        "source_loops",
        "sha256",
    ]
    for algo in ALGOS:
        wide_fields += [
            f"{algo}_verdict",
            f"{algo}_seconds",
            f"{algo}_cpu_seconds",
            f"{algo}_bound_k",
            f"{algo}_refinements",
            f"{algo}_correctness",
        ]
    with (RESULTS / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=wide_fields)
        writer.writeheader()
        for task in tasks:
            row = {
                "task_id": task["task_id"],
                "short_name": task["short_name"],
                "category": task["category"],
                "expected_verdict": task["expected_verdict"].upper(),
                "source_lines": task["source_lines"],
                "source_loops": task["loop_keywords"],
                "sha256": task["sha256"],
            }
            for algo in ALGOS:
                r = by_key[(task["task_id"], algo)]
                row.update(
                    {
                        f"{algo}_verdict": r["verdict"],
                        f"{algo}_seconds": r["wall_seconds"],
                        f"{algo}_cpu_seconds": r["cpu_seconds"],
                        f"{algo}_bound_k": fmt(r.get("bound_k")),
                        f"{algo}_refinements": fmt(r.get("refinements")),
                        f"{algo}_correctness": r["correctness"],
                    }
                )
            writer.writerow(row)

    # ---- results/summary_detail.csv : long format with all statistics ----
    long_fields = list(rows[0].keys())
    with (RESULTS / "summary_detail.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=long_fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: fmt(row.get(key)) for key in long_fields})

    with (RESULTS / "summary_detail.json").open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, ensure_ascii=False, indent=2)

    # ---- results/summary.md : tables for the report ----
    counts: dict[str, dict[str, int]] = {}
    for algo in ALGOS:
        subset = [r for r in rows if r["algorithm"] == algo]
        counts[algo] = {  # type: ignore
            "TRUE": sum(r["verdict"] == "TRUE" for r in subset),
            "FALSE": sum(r["verdict"] == "FALSE" for r in subset),
            "TIMEOUT": sum(r["verdict"] == "TIMEOUT" for r in subset),
            "UNKNOWN": sum(r["verdict"] == "UNKNOWN" for r in subset),
            "NOT_RUN": sum(r["verdict"] == "NOT_RUN" for r in subset),
            "correct": sum(r["correctness"] == "correct" for r in subset),
            "total_time": round(sum(float(r["wall_seconds"]) for r in subset), 1),  # type: ignore
            "avg_time": round(
                sum(float(r["wall_seconds"]) for r in subset) / len(subset),  # type: ignore
                1,
            ),
        }

    lines = [
        "# 全局统计（28 个任务 × 4 种算法）",
        "",
        "| 算法 | 证明安全 TRUE | 发现缺陷 FALSE | 超时 TIMEOUT | 未知 UNKNOWN | 正确判定数 | 平均耗时 (s) | 累计耗时 (s) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for algo in ALGOS:
        c = counts[algo]
        lines.append(
            f"| {algo} | {c['TRUE']} | {c['FALSE']} | {c['TIMEOUT']} | "
            f"{c['UNKNOWN']} | {c['correct']}/28 | {c['avg_time']} | {c['total_time']} |"
        )
    lines += [
        "",
        "> 耗时为 CPAchecker 报告的 `Total time for CPAchecker`（墙钟时间）；"
        "`TIMEOUT` 表示日志中出现 CPU-time limit 到达 / 分析被中断，或被宿主硬超时终止。",
        "",
        "# 单任务对比明细",
        "",
        "| 任务 | 期望 | BMC | k-Induction | Predicate | Impact |",
        "|---|---|---|---|---|---|",
    ]
    for task in tasks:
        exp = task["expected_verdict"].upper()
        cells = [
            verdict_cell(
                by_key[(task["task_id"], a)]["verdict"],  # type: ignore
                float(by_key[(task["task_id"], a)]["wall_seconds"]),  # type: ignore
                exp,
            )
            for a in ALGOS
        ]
        lines.append(f"| `{task['task_id']}` | {exp} | " + " | ".join(cells) + " |")
    lines += [
        "",
        "> 单元格格式：`判定 (墙钟秒)`；`*` 标记判定与期望标签不一致（错误判定）。",
        "",
    ]
    summary_content = "\n".join(lines)
    (RESULTS / "summary.md").write_text(summary_content, encoding="utf-8")
    (ROOT / "report" / "实验结果汇总.md").write_text(summary_content, encoding="utf-8")

    print(f"Parsed {len(rows)} runs from {len(tasks)} tasks")
    for algo in ALGOS:
        print(algo, counts[algo])
        if counts[algo]["NOT_RUN"]:
            print(f"  WARNING: {counts[algo]['NOT_RUN']} runs have no artifacts yet")
    print(
        "Wrote results/summary.csv, summary_detail.csv, summary_detail.json, summary.md, report/实验结果汇总.md"
    )


if __name__ == "__main__":
    main()
