#!/usr/bin/env python3
"""Build an annotated, human-readable excerpt of a CPAchecker counterexample.

It keeps only control-flow-relevant CFA edges, drops declarations/type edges,
attaches the original C source line, and appends the SMT model values for the
nondeterministic / state variables that decide the path.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "T23_kernelcapi"
ALGO = "Predicate"


def interesting(edge: str) -> bool:
    keys = (
        "__VERIFIER_error",
        "__VERIFIER_nondet_int",
        "ldv_",
        "mutex_",
        "capi_driver_",
        "Goto: case_",
        "Label: case_",
        "Label: ERROR",
        "Function call",
        "Function start",
        "[!",
        "[tmp",
        "[ldv",
        "while (1)",
        "INIT GLOBAL VARS",
        "ldv_initialize",
        "bgrt_",
    )
    if not any(k in edge for k in keys):
        return False
    noise = (
        "typedef ",
        "struct ",
        "extern ",
        "union ",
        "enum ",
        "char __mod",
        "char __param",
        "static void",
        "static int",
    )
    return not any(k in edge for k in noise)


def main() -> None:
    with (ROOT / "benchmarks" / "tasks.csv").open(encoding="utf-8") as handle:
        tasks = {row["task_id"]: row for row in csv.DictReader(handle)}
    task = tasks[TASK_ID]
    source_path = ROOT / task["source_file"]
    source = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
    out_dir = ROOT / "results" / TASK_ID / ALGO

    trace_lines = (
        (out_dir / "Counterexample.1.txt")
        .read_text(encoding="utf-8", errors="replace")
        .splitlines()
    )
    assignment = (
        (out_dir / "Counterexample.1.assignment.txt")
        .read_text(encoding="utf-8", errors="replace")
        .splitlines()
    )

    # Inline "var == value;" lines are the concrete model values attached to the
    # CFA edge immediately above them. Address/offset equalities of the memory
    # model are filtered out to keep the excerpt readable.
    records: list[list[str]] = []
    last_edge_kept = False
    for raw in trace_lines:
        if (
            raw.startswith(("\t", " "))
            and "=" in raw
            and not raw.lstrip().startswith("N")
        ):
            value = raw.strip()
            if (
                last_edge_kept
                and records
                and len(value) < 90
                and "signed long long int" not in value
                and "(" not in value.split("==")[0]
            ):
                records[-1][3] = (records[-1][3] + " " + value).strip()
            continue
        match = re.match(
            r"^(line[s]? [^:]*|none):\s*(N\d+)\s+-\{(.*)\}->\s*(N\d+)", raw
        )
        if not match:
            continue
        loc, node, edge, successor = match.groups()
        kept = interesting(edge)
        last_edge_kept = kept
        if not kept:
            continue
        line_no_match = re.search(r"(\d+)", loc)
        line_no = int(line_no_match.group(1)) if line_no_match else 0
        src = source[line_no - 1].strip() if 0 < line_no <= len(source) else ""
        records.append([loc, edge.strip(), src, ""])

    key_vars = (
        "__VERIFIER_nondet_int",
        "main::tmp",
        "main::tmp___0",
        "ldv_mutex@",
        "res_seq_",
        "__ADDRESS_OF_capi_drivers",
    )
    key_assignments = [
        line for line in assignment if any(key in line for key in key_vars)
    ]

    lines = [
        f"# {TASK_ID} / {ALGO} 反例轨迹精简摘录",
        "",
        f"源文件: `{task['source_file']}`",
        "",
        "说明: 原始 `Counterexample.1.txt` 共 "
        f"{len(trace_lines)} 行，含大量 typedef / 全局变量初始化边；"
        "此处仅保留与路径约束、函数调用及错误状态相关的 CFA 边，并附源码原文。",
        "",
        "| # | 源码位置 | CFA 边（语句 / 路径条件） | 模型赋值 | 源码原文 |",
        "|---:|---|---|---|---|",
    ]
    for index, (loc, edge, src, values) in enumerate(records, 1):

        def clean(s):
            return s.replace("|", "\\|").replace("\n", " ")

        lines.append(
            f"| {index} | {clean(loc)} | `{clean(edge)}` | {clean(values)} | `{clean(src)}` |"
        )

    lines += [
        "",
        "## SMT 模型中的关键变量赋值（摘自 Counterexample.1.assignment.txt）",
        "",
        "```",
    ]
    lines += key_assignments
    lines += [
        "```",
        "",
        "## 完整赋值规模",
        "",
        f"`Counterexample.1.assignment.txt` 共 {len(assignment)} 行；"
        "其中结构体/指针地址采用位精确 64 位整数建模。",
        "",
    ]

    dest = ROOT / "report" / "反例轨迹精简摘录.md"
    dest.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {dest} with {len(records)} relevant edges")


if __name__ == "__main__":
    main()
