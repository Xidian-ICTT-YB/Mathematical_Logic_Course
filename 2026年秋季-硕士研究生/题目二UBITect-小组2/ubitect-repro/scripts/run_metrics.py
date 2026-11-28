#!/usr/bin/env python3
"""Measure reproducible, selected UBITect stages with GNU time -v.

Runs inside the linux/amd64 container.  It never writes into artifacts/ or the
A-D evidence; all repeat outputs go under metrics/raw/<run_id>/.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import pathlib
import re
import shlex
import shutil
import statistics
import subprocess
import sys
import time

ROOT = pathlib.Path("/work")
LLVM = pathlib.Path("/opt/llvm7")
PLUGIN = ROOT / "build/bbtag/bbTaglib.so"
UBITECT = ROOT / "build/ubitect-original/ubitect"
KLEE_ORIG = ROOT / "build/klee-original/bin/klee.noexport"
PYTHON = ROOT / ".venv-linux/bin/python"
METRICS = ROOT / "metrics"
RAW = METRICS / "raw"
ART = ROOT / "artifacts"


def run_timed(argv: list[str], cwd: pathlib.Path, stage: str, repeat: int,
              run_raw: pathlib.Path, timeout: int = 120) -> dict:
    d = run_raw / stage / f"run-{repeat:02d}"
    d.mkdir(parents=True, exist_ok=True)
    time_log = d / "time.txt"
    command_log = d / "command.log"
    start = time.monotonic()
    timed_out = False
    with command_log.open("w", encoding="utf-8", errors="replace") as log:
        log.write("$ " + shlex.join(argv) + "\n")
        log.flush()
        proc = subprocess.Popen(
            ["/usr/bin/time", "-v", "-o", str(time_log), *argv],
            cwd=str(cwd), stdout=log, stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(proc.pid, 9)
            except ProcessLookupError:
                pass
            proc.wait()
    wall = round(time.monotonic() - start, 4)
    max_rss_kb = None
    if time_log.is_file():
        text = time_log.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", text)
        if m:
            max_rss_kb = int(m.group(1))
    record = {
        "stage": stage,
        "repeat": repeat,
        "argv": argv,
        "cwd": str(cwd),
        "exit_code": proc.returncode,
        "timed_out": timed_out,
        "wall_s": wall,
        "max_rss_kb": max_rss_kb,
        "time_log": str(time_log),
        "command_log": str(command_log),
    }
    (d / "record.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def cgroup() -> dict:
    out = {}
    for key, name in (("current", "memory.current"), ("peak", "memory.peak"),
                      ("max", "memory.max")):
        p = pathlib.Path("/sys/fs/cgroup") / name
        try:
            out[key] = int(p.read_text().strip())
        except Exception:
            out[key] = None
    return out


def copy_file(src: pathlib.Path, dst: pathlib.Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def prep_backlog(work: pathlib.Path) -> dict:
    src = ROOT / "source/UBITect/example/backlog.c"
    d = work / "backlog"
    d.mkdir(parents=True)
    shutil.copy2(src, d / "backlog.c")
    cmd = [str(LLVM / "bin/clang"), "-emit-llvm", "-O0", "-g",
           "-fno-short-wchar", "-c", "backlog.c", "-o", "backlog.llbc"]
    compile = subprocess.run(cmd, cwd=d, capture_output=True, text=True)
    if compile.returncode != 0:
        raise RuntimeError(compile.stderr)
    subprocess.run([str(PYTHON), "-I", str(ROOT / "scripts/getbclist_py3.py"),
                    "--llvm-dir", str(LLVM), "--plugin", str(PLUGIN),
                    "--workdir", str(d)], check=True)
    subprocess.run([str(LLVM / "bin/llvm-link"), "-o", "built-in.bc",
                    "backlog.bc"], cwd=d, check=True)
    return {
        "source": str(d / "backlog.c"),
        "llbc": str(d / "backlog.llbc"),
        "bc": str(d / "backlog.bc"),
        "builtin": str(d / "built-in.bc"),
        "warning": str(ART / "A_original_default_dedup/candidates/candidate-01-line-25/warning.json"),
        "query": str(ART / "analysis/real-exports/A_candidate-01-line-25.smt2"),
    }


def history_run() -> pathlib.Path:
    candidates = []
    for p in sorted((ROOT / "history/ahci_xgene/runs").glob("*/summary.json")):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        if d.get("target_h1_confirmed") and not d.get("target_h2_confirmed"):
            candidates.append((p.stat().st_mtime, p.parent))
    if not candidates:
        raise RuntimeError("no passing historical run found")
    return max(candidates)[1]


def prep_history(work: pathlib.Path, version: str, run_dir: pathlib.Path) -> dict:
    d = work / version
    d.mkdir(parents=True)
    case = run_dir / version
    shutil.copy2(case / f"ahci_xgene_{version}.c", d / f"ahci_xgene_{version}.c")
    shutil.copy2(case / f"ahci_xgene_{version}.llbc", d / f"ahci_xgene_{version}.llbc")
    shutil.copy2(case / f"ahci_xgene_{version}.bc", d / f"ahci_xgene_{version}.bc")
    shutil.copy2(case / f"ahci_xgene_{version}.bb.ll", d / f"ahci_xgene_{version}.bb.ll")
    cand = case / "candidates/candidate-01-line-825" if version == "h1" else \
        case / "candidates/candidate-01-line-824"
    shutil.copy2(cand / "klee-warning.json", d / "klee-warning.json")
    shutil.copy2(cand / "klee-original/built-in.bc", d / "built-in.bc")
    return {
        "source": str(d / f"ahci_xgene_{version}.c"),
        "llbc": str(d / f"ahci_xgene_{version}.llbc"),
        "bc": str(d / f"ahci_xgene_{version}.bc"),
        "builtin": str(d / "built-in.bc"),
        "warning": str(d / "klee-warning.json"),
        "query": str(cand / "klee-smt-export/query.smt2") if version == "h1" else None,
    }


def prep_all(work: pathlib.Path) -> dict:
    hist = history_run()
    return {
        "backlog": prep_backlog(work),
        "h1": prep_history(work, "h1", hist),
        "h2": prep_history(work, "h2", hist),
        "history_run": str(hist),
    }


def repeat_stage(name: str, argv: list[str], cwd: pathlib.Path,
                 run_raw: pathlib.Path, timeout: int = 120) -> list[dict]:
    return [run_timed(argv, cwd, name, i, run_raw, timeout) for i in (1, 2, 3)]


def stage_dir(run_raw: pathlib.Path, name: str, repeat: int) -> pathlib.Path:
    d = run_raw / name / f"run-{repeat:02d}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_all(run_raw: pathlib.Path, prep: dict) -> dict:
    records = []
    # A: compile, bbtag, analyzer, KLEE, replay.
    for i in (1, 2, 3):
        d = stage_dir(run_raw, "compile_backlog_A", i)
        for f in ("backlog.c",):
            copy_file(ROOT / "source/UBITect/example/backlog.c", d / f)
        records.append(run_timed(
            [str(LLVM / "bin/clang"), "-emit-llvm", "-O0", "-g",
             "-fno-short-wchar", "-c", "backlog.c", "-o", "backlog.llbc"],
            d, "compile_backlog_A", i, run_raw, 60))
    for i in (1, 2, 3):
        d = stage_dir(run_raw, "bbtag_backlog_A", i)
        copy_file(pathlib.Path(prep["backlog"]["llbc"]), d / "backlog.llbc")
        records.append(run_timed(
            [str(PYTHON), "-I", str(ROOT / "scripts/getbclist_py3.py"),
             "--llvm-dir", str(LLVM), "--plugin", str(PLUGIN),
             "--workdir", str(d)], d, "bbtag_backlog_A", i, run_raw, 120))
    for i in (1, 2, 3):
        d = stage_dir(run_raw, "analyze_backlog_A", i)
        copy_file(pathlib.Path(prep["backlog"]["bc"]), d / "backlog.bc")
        (d / "bitcode.list").write_text(str(d / "backlog.bc") + "\n")
        records.append(run_timed(
            [str(UBITECT), "-ubi-analysis", "@bitcode.list"], d,
            "analyze_backlog_A", i, run_raw, 120))
    for i in (1, 2, 3):
        d = stage_dir(run_raw, "klee_backlog_A", i)
        copy_file(pathlib.Path(prep["backlog"]["builtin"]), d / "built-in.bc")
        copy_file(pathlib.Path(prep["backlog"]["warning"]), d / "warning.json")
        payload = json.loads((d / "warning.json").read_text())
        records.append(run_timed(
            [str(KLEE_ORIG), f"-json={json.dumps(payload)}", "./built-in.bc"],
            d, "klee_backlog_A", i, run_raw, 120))
    for i in (1, 2, 3):
        d = stage_dir(run_raw, "replay_backlog_A", i)
        copy_file(pathlib.Path(prep["backlog"]["query"]), d / "query.smt2")
        records.append(run_timed(
            [str(PYTHON), "-I", str(ROOT / "scripts/replay_z3.py"),
             str(d / "query.smt2")], d, "replay_backlog_A", i, run_raw, 120))

    for v in ("h1", "h2"):
        s = prep[v]
        for i in (1, 2, 3):
            d = stage_dir(run_raw, f"compile_history_{v}", i)
            copy_file(pathlib.Path(s["source"]), d / f"ahci_xgene_{v}.c")
            records.append(run_timed(
                [str(LLVM / "bin/clang"), "-emit-llvm", "-O0", "-g",
                 "-fno-short-wchar", "-DCONFIG_ACPI",
                 "-DHISTORY_ACPI_FAILURE_ONLY", "-c", f"ahci_xgene_{v}.c",
                 "-o", f"ahci_xgene_{v}.llbc"], d,
                f"compile_history_{v}", i, run_raw, 60))
        for i in (1, 2, 3):
            d = stage_dir(run_raw, f"bbtag_history_{v}", i)
            copy_file(pathlib.Path(s["llbc"]), d / f"ahci_xgene_{v}.llbc")
            records.append(run_timed(
                [str(PYTHON), "-I", str(ROOT / "scripts/getbclist_py3.py"),
                 "--llvm-dir", str(LLVM), "--plugin", str(PLUGIN),
                 "--workdir", str(d)], d, f"bbtag_history_{v}", i, run_raw, 120))
        for i in (1, 2, 3):
            d = stage_dir(run_raw, f"analyze_history_{v}", i)
            copy_file(pathlib.Path(s["bc"]), d / f"ahci_xgene_{v}.bc")
            (d / "bitcode.list").write_text(str(d / f"ahci_xgene_{v}.bc") + "\n")
            records.append(run_timed(
                [str(UBITECT), "-ubi-analysis", "@bitcode.list"], d,
                f"analyze_history_{v}", i, run_raw, 180))
        for i in (1, 2, 3):
            d = stage_dir(run_raw, f"klee_history_{v}", i)
            copy_file(pathlib.Path(s["builtin"]), d / "built-in.bc")
            copy_file(pathlib.Path(s["warning"]), d / "warning.json")
            payload = json.loads((d / "warning.json").read_text())
            records.append(run_timed(
                [str(KLEE_ORIG), f"-json={json.dumps(payload)}", "./built-in.bc"],
                d, f"klee_history_{v}", i, run_raw, 120))
        if s["query"]:
            for i in (1, 2, 3):
                d = stage_dir(run_raw, f"replay_history_{v}", i)
                copy_file(pathlib.Path(s["query"]), d / "query.smt2")
                records.append(run_timed(
                    [str(PYTHON), "-I", str(ROOT / "scripts/replay_z3.py"),
                     str(d / "query.smt2")], d,
                    f"replay_history_{v}", i, run_raw, 120))
    return {"stages": records}


def parse_warnings(path: pathlib.Path) -> list[dict]:
    rows = []
    for line in path.read_text().splitlines():
        if line.strip().startswith("{"):
            rows.append(json.loads(line))
    return rows


def confirm_lines(path: pathlib.Path) -> list[int]:
    if not path.is_file():
        return []
    out = []
    for line in path.read_text().splitlines():
        if line.strip():
            o = json.loads(line)
            if o.get("find") == "Yes":
                out.append(int(o["lineNo"]))
    return sorted(set(out))


def functional_rows(summary: dict, hist: dict) -> list[dict]:
    rows = []
    for c in summary["cases"]:
        cid = c["case"]
        warnings = []
        for cand in c["candidates"]:
            warnings.append(cand)
        raw_objects = c["candidate_count"]
        use_points = len({x["lineNo"] for x in warnings})
        # backlog target-line mapping
        target_lines = {"A": {25}, "B": {25, 26}, "C": set(), "D": {25}}[cid]
        target = [x for x in warnings if x["lineNo"] in target_lines]
        confirmed = [x for x in target if x["original"]["confirmed"]]
        solver = "none"
        if any(x["export"].get("smt_replay") for x in warnings):
            solver = ",".join(sorted({str(x["export"]["smt_replay"].get("result")) for x in warnings
                                      if x["export"].get("smt_replay")}))
        rows.append({
            "case": cid, "version": cid, "report_mode": c["config_note"],
            "warning_objects": raw_objects,
            "independent_use_points": use_points,
            "target_warning_objects": len(target),
            "target_confirmed_objects": len(confirmed),
            "target_confirmed_use_points": len({x["lineNo"] for x in confirmed}),
            "klee_candidates_run": sum(1 for x in warnings if x["original"]),
            "timeouts": sum(int(bool(x["original"]["timed_out"])) for x in warnings),
            "errors": sum(int(x["original"]["exit_code"] not in (0,)) for x in warnings),
            "solver_status": solver,
            "repeat_consistency": "A:3/3" if cid == "A" else "not repeated this round",
        })
    for s in hist["histories"]:
        v = s["version"]
        target_line = s["target_line"]
        target = [x for x in s["candidates"] if x["lineNo"] == target_line]
        confirmed = [x for x in target if x["original"]["confirmed"]]
        solver = "none"
        if any(x["export"].get("smt_replay") for x in target):
            solver = ",".join(sorted({str(x["export"]["smt_replay"].get("result"))
                                      for x in target
                                      if x["export"].get("smt_replay")}))
        rows.append({
            "case": f"ahci_xgene_{v}", "version": v,
            "report_mode": "historical function-level failure-only harness",
            "warning_objects": s["candidate_count"],
            "independent_use_points": len({x["lineNo"] for x in s["candidates"]}),
            "target_warning_objects": len(target),
            "target_confirmed_objects": len(confirmed),
            "target_confirmed_use_points": len({x["lineNo"] for x in confirmed}),
            "klee_candidates_run": len(s["candidates"]),
            "timeouts": sum(int(bool(x["original"]["timed_out"])) for x in s["candidates"]),
            "errors": sum(int(x["original"]["exit_code"] != 0) for x in s["candidates"]),
            "solver_status": solver,
            "repeat_consistency": f"{v}:3/3",
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args()
    run_id = args.run_id or dt.datetime.now(dt.timezone.utc).strftime("MET-%Y%m%dT%H%M%SZ")
    run_raw = RAW / run_id
    if run_raw.exists():
        print(f"FATAL: exists: {run_raw}", file=sys.stderr)
        return 2
    run_raw.mkdir(parents=True)
    work = run_raw / "work"
    work.mkdir()
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    cg_start = cgroup()
    prep = prep_all(work)
    prep_info = {
        "started_utc": started,
        "history_run": prep["history_run"],
        "inputs": {k: {kk: vv for kk, vv in v.items()} for k, v in prep.items()
                   if k in ("backlog", "h1", "h2")},
        "cgroup_start": cg_start,
        "cold_build": "unavailable; existing image/toolchain reused (not re-installed)",
    }
    (run_raw / "prep.json").write_text(json.dumps(prep_info, indent=2) + "\n")
    result = run_all(run_raw, prep)
    records = result["stages"]
    cg_end = cgroup()
    (run_raw / "manifest.json").write_text(json.dumps({
        "run_id": run_id,
        "started_utc": started,
        "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "container_arch": os.uname().machine,
        "records": records,
        "cgroup_start": cg_start,
        "cgroup_end": cg_end,
        "prep": prep_info,
    }, indent=2) + "\n")

    # resources.csv: one row per repeat.
    with (METRICS / "resources.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "stage", "repeat", "wall_s", "max_rss_kb", "exit_code", "timed_out",
            "time_log", "command_log"])
        w.writeheader()
        for r in records:
            w.writerow({k: r[k] for k in w.fieldnames})

    # Aggregate stage medians and ranges from all three raw values.
    grouped: dict[str, list[dict]] = {}
    for r in records:
        grouped.setdefault(r["stage"], []).append(r)
    stage_summary = {}
    for stage, rs in grouped.items():
        walls = [r["wall_s"] for r in rs]
        rss = [r["max_rss_kb"] for r in rs if r["max_rss_kb"] is not None]
        stage_summary[stage] = {
            "n": len(rs),
            "wall_s": {"values": walls, "median": statistics.median(walls),
                       "min": min(walls), "max": max(walls)},
            "max_rss_kb": {"values": rss,
                           "median": statistics.median(rss) if rss else None,
                           "min": min(rss) if rss else None,
                           "max": max(rss) if rss else None},
            "exit_codes": [r["exit_code"] for r in rs],
            "timeouts": sum(int(r["timed_out"]) for r in rs),
        }

    art_summary = json.loads((ART / "summary.json").read_text())
    hist = json.loads((pathlib.Path(prep["history_run"]) / "summary.json").read_text())
    frows = functional_rows(art_summary, hist)
    with (METRICS / "results.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(frows[0].keys()))
        w.writeheader()
        w.writerows(frows)

    def dir_bytes(p: pathlib.Path) -> int:
        return sum(x.stat().st_size for x in p.rglob("*") if x.is_file())
    resources = {
        "stage_summary": stage_summary,
        "cgroup": {"start": cg_start, "end": cg_end},
        "vm_config": {"cpus": 6, "memory_mib": 8192, "disk_size_mib": 102400,
                      "source": "Docker Desktop settings"},
        "build_first_time": "unavailable; cold image/KLEE build was not re-run in this round",
        "disk_bytes": {
            "artifacts": dir_bytes(ART),
            "history": dir_bytes(ROOT / "history"),
            "metrics": dir_bytes(METRICS),
            "build": dir_bytes(ROOT / "build"),
        },
        "measurement_note": (
            "max_rss_kb is per-process GNU time peak; cgroup values are container "
            "lifetime/current, not per-stage peaks; VM configuration is not measured "
            "usage. build_first_time is unavailable rather than zero."
        ),
    }
    out = {
        "run_id": run_id,
        "functional": frows,
        "resources": resources,
        "raw_dir": str(run_raw),
    }
    (METRICS / "summary.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({
        "run_id": run_id, "raw_dir": str(run_raw),
        "stages": {k: {"n": v["n"], "median_wall_s": v["wall_s"]["median"],
                       "range_wall_s": [v["wall_s"]["min"], v["wall_s"]["max"]],
                       "median_rss_kb": v["max_rss_kb"]["median"]}
                   for k, v in stage_summary.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
