#!/usr/bin/env python3
"""Regenerate PPT tables, code snippets and data snapshots from measured files."""
from __future__ import annotations

import csv
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
TABLES = ROOT / "ppt_assets/tables"
CODE = ROOT / "ppt_assets/code"
DATA = ROOT / "ppt_assets/data"


def latest_history() -> pathlib.Path:
    items = []
    for p in (ROOT / "history/ahci_xgene/runs").glob("*/summary.json"):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        if d.get("target_h1_confirmed") and not d.get("target_h2_confirmed"):
            items.append((p.stat().st_mtime, p.parent))
    if not items:
        raise SystemExit("no passing historical run; run REPRODUCE_ALL.sh first")
    return max(items)[1]


def main() -> int:
    for d in (TABLES, CODE, DATA):
        d.mkdir(parents=True, exist_ok=True)
    for src, dst in [
        (ROOT / "metrics/results.csv", DATA / "results.csv"),
        (ROOT / "metrics/resources.csv", DATA / "resources.csv"),
        (ROOT / "metrics/summary.json", DATA / "metrics-summary.json"),
        (ROOT / "metrics/candidate_timings.csv", DATA / "candidate_timings.csv"),
        (ROOT / "artifacts/summary.json", DATA / "backlog-summary.json"),
    ]:
        shutil.copy2(src, dst)
    hist = latest_history()
    shutil.copy2(hist / "summary.json", DATA / "history-summary.json")

    rows = list(csv.DictReader((ROOT / "metrics/results.csv").open()))
    md = ["# 案例结果表", "",
          "| 案例 | 模式 | warning 对象 | 独立 use 点 | 目标确认对象 | 目标确认 use 点 | 求解状态 |",
          "|---|---|---:|---:|---:|---:|---|"]
    for r in rows:
        md.append(f"| {r['case']} | {r['report_mode']} | {r['warning_objects']} | "
                  f"{r['independent_use_points']} | {r['target_confirmed_objects']} | "
                  f"{r['target_confirmed_use_points']} | {r['solver_status']} |")
    (TABLES / "case_results.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    with (TABLES / "case_results.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    s = json.loads((ROOT / "metrics/summary.json").read_text())["resources"]["stage_summary"]
    md = ["# 阶段耗时与进程 RSS", "",
          "| 阶段 | n | 中位墙钟/s | 范围/s | 中位峰值 RSS/KiB |",
          "|---|---:|---:|---|---:|"]
    with (TABLES / "stage_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["stage", "n", "median_wall_s", "min_wall_s", "max_wall_s", "median_rss_kb"])
        for k, v in s.items():
            wall = v["wall_s"]; rss = v["max_rss_kb"]
            md.append(f"| {k} | {v['n']} | {wall['median']:.4f} | "
                      f"{wall['min']:.4f}–{wall['max']:.4f} | "
                      f"{rss['median'] if rss['median'] is not None else 'NA'} |")
            w.writerow([k, v["n"], wall["median"], wall["min"], wall["max"], rss["median"]])
    (TABLES / "stage_metrics.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    source_rows = [
        ("backlog A/B/D", "backlog.c", 25, "if(backlog) load", "UBI use / pointer load", "A default reports 25; B teaching also 26"),
        ("backlog B", "backlog.c", 26, "backlog->irq dereference", "conditional on nonzero residual pointer", "B only"),
        ("ahci_xgene H1", "drivers/ata/ahci_xgene.c", 825, "if (info->valid & ACPI_VALID_CID)", "target UBI read after failure", "H1 confirmed via failure-only harness"),
        ("ahci_xgene H2", "drivers/ata/ahci_xgene.c", 824, "else if (info->valid & ACPI_VALID_CID)", "official fix blocks failure read", "H2 target not confirmed"),
    ]
    with (TABLES / "source_path_map.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case", "source", "line", "construct", "role", "evidence"])
        w.writerows(source_rows)
    md = ["# 源码行 → use 点映射", "", "| 案例 | 源码 | 行 | 构造 | 含义 | 证据 |", "|---|---|---:|---|---|---|"]
    for r in source_rows:
        md.append("| " + " | ".join(map(str, r)) + " |")
    (TABLES / "source_path_map.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    bl = (ROOT / "source/UBITect/example/backlog.c").read_text().splitlines()
    (CODE / "backlog_snippet.c").write_text("\n".join(bl[16:29]) + "\n", encoding="utf-8")
    for v, src in [("h1", "history/ahci_xgene/source/ahci_xgene.8ba559fd09bc.c"),
                   ("h2", "history/ahci_xgene/source/ahci_xgene.8134233e8d34.c")]:
        lines = (ROOT / src).read_text().splitlines()
        (CODE / f"ahci_{v}_snippet.c").write_text("\n".join(lines[816:828]) + "\n", encoding="utf-8")
    shutil.copy2(ROOT / "history/ahci_xgene/provenance/official-fix.patch", CODE / "official_fix.diff")
    for src, dst in [
        ("artifacts/analysis/real-exports/A_candidate-01-line-25.smt2", "backlog_line25.smt2"),
        ("artifacts/analysis/real-exports/B_candidate-02-line-26.smt2", "backlog_line26.smt2"),
    ]:
        if (ROOT / src).is_file():
            shutil.copy2(ROOT / src, CODE / dst)
    h1q = hist / "h1/candidates/candidate-01-line-825/klee-smt-export/query.smt2"
    if h1q.is_file():
        shutil.copy2(h1q, CODE / "history_h1_line825.smt2")
    (CODE / "history_h2_line824_absent.txt").write_text(
        "No KLEE SMT query was exported for H2: the failure-only path never reaches line 824.\n",
        encoding="utf-8")
    print(f"tables/code/data regenerated; history={hist.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
