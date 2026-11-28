#!/usr/bin/env python3
"""Run the historical ahci_xgene H1/H2 case with the author's UBITect/KLEE.

The runner uses the real historical driver function excerpt and documented
kernel-interface stubs.  It does not touch the A-D artifacts.
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import hashlib
import json
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import sys
import time

ROOT = pathlib.Path("/work")
LLVM = pathlib.Path("/opt/llvm7")
PLUGIN = ROOT / "build/bbtag/bbTaglib.so"
UBITECT = ROOT / "build/ubitect-original/ubitect"
KLEE_ORIG = ROOT / "build/klee-original/bin/klee.noexport"
KLEE_EXPORT = ROOT / "build/klee-original/bin/klee"
HIST = ROOT / "history/ahci_xgene"
RUNS = HIST / "runs"
TARGET_LINES = {"h1": 825, "h2": 824}


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def cmd_text(argv: list[str]) -> str:
    return shlex.join(argv)


def run_command(argv: list[str], cwd: pathlib.Path, log: pathlib.Path,
                timeout: int | None = None, env_extra: dict | None = None) -> dict:
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    start = time.monotonic()
    with log.open("w", encoding="utf-8", errors="replace") as f:
        f.write("$ " + cmd_text(argv) + "\n")
        f.flush()
        proc = subprocess.Popen(
            argv, cwd=cwd, stdout=f, stderr=subprocess.STDOUT,
            start_new_session=True, env=env,
        )
        try:
            proc.wait(timeout=timeout)
            timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(proc.pid, 9)
            except ProcessLookupError:
                pass
            proc.wait()
    return {
        "argv": argv,
        "shell": cmd_text(argv),
        "cwd": str(cwd),
        "exit_code": proc.returncode,
        "timed_out": timed_out,
        "duration_s": round(time.monotonic() - start, 3),
        "log": str(log),
    }


def parse_warning_stream(path: pathlib.Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    result, bc_line = [], None
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith("{"):
            if bc_line is None:
                raise RuntimeError("JSON warning without bc path")
            result.append({"bc_line": bc_line, "raw": s,
                           "warning": json.loads(s)})
            bc_line = None
        else:
            if bc_line is not None:
                raise RuntimeError("two bc path lines without warning")
            bc_line = line
    if bc_line is not None:
        raise RuntimeError("trailing bc path line")
    return result


def parse_confirm(path: pathlib.Path) -> dict:
    if not path.is_file():
        return {"exists": False, "objects": [], "raw": ""}
    raw = path.read_text(encoding="utf-8", errors="replace")
    return {
        "exists": True,
        "objects": [json.loads(x) for x in raw.splitlines() if x.strip()],
        "raw": raw,
    }


def norm_inst(text: str) -> str:
    """Ignore SSA numeric names; keep types, operands and text."""
    text = text.split("!", 1)[0].strip()
    text = re.sub(r"%[0-9]+", "%N", text)
    text = re.sub(r"\s+", " ", text)
    return text


def find_klee_instruction(instructions: pathlib.Path, line_no: int,
                         wanted: str) -> str | None:
    if not instructions.is_file():
        return None
    target = norm_inst(wanted)
    pattern = re.compile(r"^\s+.*:([0-9]+):([0-9]+):\s*(.*)$")
    found = []
    for line in instructions.read_text(encoding="utf-8", errors="replace").splitlines():
        m = pattern.match(line)
        if not m:
            continue
        if int(m.group(1)) != line_no:
            continue
        # KLEE's Instruction::print() prefixes instructions with two spaces;
        # the log's colon-delimited prefix consumed them.  Restore the exact
        # spelling that Encode::isWarning() compares against.
        text = "  " + m.group(3).lstrip()
        if norm_inst(text) == target:
            found.append(text)
    return found[0] if found else None


def parse_candidates(case_dir: pathlib.Path, version: str) -> list[dict]:
    raw_rows = parse_warning_stream(case_dir / "warnings.json")
    target_line = TARGET_LINES[version]
    candidates = []
    for i, row in enumerate(raw_rows, 1):
        w = row["warning"]
        candidates.append({
            "index": i,
            "lineNo": w.get("lineNo"),
            "use": w.get("use"),
            "type": w.get("type"),
            "rank": w.get("rank"),
            "target_line": w.get("lineNo") == target_line,
            "raw": row["raw"],
            "warning": w,
            "bc_line": row["bc_line"],
        })
    return candidates


def copy_context(run_dir: pathlib.Path) -> None:
    shutil.copytree(HIST / "source", run_dir / "source",
                    ignore=shutil.ignore_patterns("*.pyc"))
    shutil.copytree(HIST / "provenance", run_dir / "provenance")
    shutil.copytree(HIST / "harness", run_dir / "harness")
    for name in ("HARNESS_MAPPING.md", "KLEE_BRIDGE.md"):
        shutil.copy2(HIST / name, run_dir / name)


def run_case(run_dir: pathlib.Path, version: str) -> dict:
    case_dir = run_dir / version
    case_dir.mkdir(parents=True)
    src = HIST / "harness" / f"ahci_xgene_{version}.c"
    shutil.copy2(src, case_dir / src.name)

    compile_argv = [
        str(LLVM / "bin/clang"), "-emit-llvm", "-O0", "-g",
        "-fno-short-wchar", "-DCONFIG_ACPI", "-DHISTORY_ACPI_FAILURE_ONLY",
        "-c", src.name, "-o", f"ahci_xgene_{version}.llbc",
    ]
    compile_res = run_command(compile_argv, case_dir, case_dir / "compile.log",
                              timeout=60)
    (case_dir / "compile_command.txt").write_text(compile_res["shell"] + "\n",
                                                  encoding="utf-8")
    if compile_res["exit_code"] != 0:
        raise RuntimeError(f"{version}: clang failed")
    dis = run_command([str(LLVM / "bin/llvm-dis"),
                       f"ahci_xgene_{version}.llbc", "-o",
                       f"ahci_xgene_{version}.ll"], case_dir,
                      case_dir / "llvm-dis.log", timeout=60)
    if dis["exit_code"] != 0:
        raise RuntimeError(f"{version}: llvm-dis failed")

    bbtag_argv = [
        str(ROOT / ".venv-linux/bin/python"), "-I",
        str(ROOT / "scripts/getbclist_py3.py"),
        "--llvm-dir", str(LLVM), "--plugin", str(PLUGIN),
        "--workdir", str(case_dir),
    ]
    bbtag = run_command(bbtag_argv, case_dir, case_dir / "bbtag.log", timeout=120)
    (case_dir / "bbtag_command.txt").write_text(bbtag["shell"] + "\n")
    if bbtag["exit_code"] != 0:
        raise RuntimeError(f"{version}: bbTag failed")
    dis = run_command([str(LLVM / "bin/llvm-dis"),
                       f"ahci_xgene_{version}.bc", "-o",
                       f"ahci_xgene_{version}.bb.ll"], case_dir,
                      case_dir / "llvm-dis-renamed.log", timeout=60)
    if dis["exit_code"] != 0:
        raise RuntimeError(f"{version}: renamed llvm-dis failed")

    analysis = run_command(
        [str(UBITECT), "-ubi-analysis", "@bitcode.list"], case_dir,
        case_dir / "stage1.log", timeout=180,
    )
    (case_dir / "stage1_command.txt").write_text(analysis["shell"] + "\n")
    (case_dir / "stage1_exit_code.txt").write_text(
        str(analysis["exit_code"]) + "\n")
    if analysis["exit_code"] != 0:
        raise RuntimeError(f"{version}: UBITect failed")

    candidates = parse_candidates(case_dir, version)
    (case_dir / "warnings.parsed.json").write_text(
        json.dumps(candidates, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    cand_root = case_dir / "candidates"
    cand_root.mkdir()
    records = []
    for c in candidates:
        cdir = cand_root / f"candidate-{c['index']:02d}-line-{c['lineNo']}"
        cdir.mkdir()
        (cdir / "raw-warning.json").write_text(c["raw"] + "\n", encoding="utf-8")
        (cdir / "raw-warning-context.json").write_text(
            json.dumps({"bc_line": c["bc_line"], "warning": c["warning"]},
                       indent=2, sort_keys=True) + "\n", encoding="utf-8")

        # Calibration: run KLEE with the raw warning solely to learn KLEE's
        # instruction spelling after module loading/renumbering.
        calib_dir = cdir / "calibration"
        calib_dir.mkdir()
        bridge_obj = json.loads(c["raw"])
        bridge_obj["function"] = "history_entry_failure"
        calib_warning = calib_dir / "warning-raw-entry.json"
        calib_warning.write_text(json.dumps(bridge_obj) + "\n", encoding="utf-8")
        calib_argv = [
            str(KLEE_ORIG), "-debug-print-instructions=all:file",
            f"-json={json.dumps(bridge_obj)}", "./built-in.bc",
        ]
        link = run_command(
            [str(LLVM / "bin/llvm-link"), "-o", "built-in.bc",
             str(case_dir / f"ahci_xgene_{version}.bc")],
            calib_dir, calib_dir / "llvm-link.log", timeout=60,
        )
        calib = run_command(calib_argv, calib_dir, calib_dir / "klee.log",
                            timeout=120)
        (calib_dir / "command.json").write_text(
            json.dumps({"argv": calib_argv, "cwd": str(calib_dir)}, indent=2) + "\n")

        bridge_inst = None
        instr = calib_dir / "klee-out-0/instructions.txt"
        if instr.is_file():
            # Reconstruct the same instruction first, without the debug suffix.
            bridge_inst = find_klee_instruction(
                instr, int(c["lineNo"]), c["warning"].get("warning", ""))
        bridge_obj["warning"] = bridge_inst or c["warning"].get("warning", "")
        klee_warning = cdir / "klee-warning.json"
        klee_warning.write_text(json.dumps(bridge_obj, indent=2) + "\n",
                                encoding="utf-8")
        raw_pretty = json.dumps(c["warning"], indent=2, sort_keys=True).splitlines()
        bridge_pretty = json.dumps(bridge_obj, indent=2, sort_keys=True).splitlines()
        diff = "\n".join(difflib.unified_diff(
            raw_pretty, bridge_pretty, fromfile="raw-warning.json",
            tofile="klee-warning.json", lineterm=""))
        (cdir / "klee-bridge.diff").write_text(diff + "\n", encoding="utf-8")
        (cdir / "bridge.json").write_text(json.dumps({
            "function": "xgene_ahci_probe -> history_entry_failure",
            "raw_warning_instruction": c["warning"].get("warning"),
            "klee_instruction": bridge_inst,
            "ssa_changed": bridge_inst is not None and
                norm_inst(bridge_inst) == norm_inst(c["warning"].get("warning", "")),
            "calibration_exit_code": calib["exit_code"],
            "calibration_timed_out": calib["timed_out"],
            "calibration_confirm": (calib_dir / "confirm_result.json").is_file(),
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        def klee_variant(label: str, binary: pathlib.Path, export: bool) -> dict:
            d = cdir / label
            d.mkdir()
            lk = run_command(
                [str(LLVM / "bin/llvm-link"), "-o", "built-in.bc",
                 str(case_dir / f"ahci_xgene_{version}.bc")],
                d, d / "llvm-link.log", timeout=60,
            )
            argv = [str(binary), f"-json={json.dumps(bridge_obj)}", "./built-in.bc"]
            extra = {"UBITECT_SMT_DUMP": str(d / "query.smt2") if export else ""}
            res = run_command(argv, d, d / "klee.log", timeout=120, env_extra=extra)
            (d / "command.json").write_text(json.dumps(
                {"argv": argv, "cwd": str(d)}, indent=2) + "\n")
            (d / "command.sh").write_text(
                shlex.quote(str(d)) + "\n" + shlex.join(argv) + "\n")
            confirm = parse_confirm(d / "confirm_result.json")
            lines = sorted({int(o["lineNo"]) for o in confirm["objects"]
                            if o.get("find") == "Yes" and "lineNo" in o})
            log_text = (d / "klee.log").read_text(encoding="utf-8", errors="replace")
            replay = None
            q = d / "query.smt2"
            if q.is_file():
                rj = d / "z3-replay.json"
                rr = run_command([
                    str(ROOT / ".venv-linux/bin/python"), "-I",
                    str(ROOT / "scripts/replay_z3.py"), str(q),
                    "--json-out", str(rj),
                ], d, d / "z3-replay.log", timeout=120)
                replay = {"exit_code": rr["exit_code"], "result": None, "model": None}
                if rj.is_file():
                    replay.update(json.loads(rj.read_text(encoding="utf-8")))
            return {
                "exit_code": res["exit_code"],
                "timed_out": res["timed_out"],
                "confirmed": bool(lines) and "[SrcCode]" in log_text,
                "confirmed_lines": lines,
                "confirm_result_exists": confirm["exists"],
                "command": res,
                "smt_exported": q.is_file(),
                "smt_replay": replay,
                "link": lk,
            }

        original = klee_variant("klee-original", KLEE_ORIG, False)
        export = klee_variant("klee-smt-export", KLEE_EXPORT, True)
        rec = {
            **c,
            "target": c["target_line"],
            "bridge": {
                "function": "history_entry_failure",
                "instruction_found": bridge_inst is not None,
                "instruction": bridge_inst,
            },
            "original": original,
            "export": export,
            "same_confirmation": original["confirmed_lines"] == export["confirmed_lines"],
        }
        (cdir / "result.json").write_text(
            json.dumps(rec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        records.append(rec)

    confirms = []
    for rec in records:
        p = cand_root / f"candidate-{rec['index']:02d}-line-{rec['lineNo']}" / "klee-original" / "confirm_result.json"
        if p.is_file():
            confirms.append(p.read_text(encoding="utf-8", errors="replace").rstrip("\n"))
    if confirms:
        (case_dir / "confirm_result.json").write_text(
            "\n".join(confirms) + "\n", encoding="utf-8")
    else:
        (case_dir / "confirm_result.absent.txt").write_text(
            "No target candidate was confirmed by KLEE in this case.\n",
            encoding="utf-8")

    target = [r for r in records if r["target"]]
    target_confirmed = [r for r in target if r["original"]["confirmed"]]
    summary = {
        "version": version,
        "target_line": TARGET_LINES[version],
        "source": f"drivers/ata/ahci_xgene.c:{TARGET_LINES[version]}",
        "compile": compile_res,
        "bbtag": bbtag,
        "analysis": analysis,
        "candidate_count": len(records),
        "target_warning_count": len(target),
        "target_confirmed_count": len(target_confirmed),
        "target_confirmed_lines": sorted({r["lineNo"] for r in target_confirmed}),
        "other_warning_count": len(records) - len(target),
        "candidates": records,
    }
    (case_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"{version}: candidates={len(records)} target={len(target)} "
        f"target_confirmed={len(target_confirmed)} "
        f"lines={sorted({r['lineNo'] for r in target_confirmed})}",
        flush=True,
    )
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args()
    run_id = args.run_id or dt.datetime.now(dt.timezone.utc).strftime("HIST-%Y%m%dT%H%M%SZ")
    run_dir = RUNS / run_id
    if run_dir.exists():
        print(f"FATAL: run directory exists: {run_dir}", file=sys.stderr)
        return 2
    for p in (LLVM / "bin/clang", PLUGIN, UBITECT, KLEE_ORIG, KLEE_EXPORT,
              HIST / "harness/ahci_xgene_h1.c"):
        if not p.exists():
            print(f"FATAL: missing {p}", file=sys.stderr)
            return 3
    RUNS.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir()
    copy_context(run_dir)
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    summaries = []
    for v in ("h1", "h2"):
        summaries.append(run_case(run_dir, v))
    finished = dt.datetime.now(dt.timezone.utc).isoformat()
    result = {
        "run_id": run_id,
        "started_utc": started,
        "finished_utc": finished,
        "container_arch": os.uname().machine,
        "upstream_commit": "8134233e8d346aaa1c929dc510e75482ae318bce",
        "parent_commit": "8ba559fd09bcf4e87faad3efa465dacf04c076c9",
        "source_function": "drivers/ata/ahci_xgene.c:xgene_ahci_probe",
        "target_lines": TARGET_LINES,
        "histories": summaries,
        "target_h1_confirmed": any(
            s["version"] == "h1" and s["target_confirmed_count"] > 0
            for s in summaries),
        "target_h2_confirmed": any(
            s["version"] == "h2" and s["target_confirmed_count"] > 0
            for s in summaries),
        "note": (
            "H1/H2 use the same real function excerpt, same stubs, compiled "
            "with -DHISTORY_ACPI_FAILURE_ONLY. KLEE entry-function and warning "
            "SSA bridge are documented in KLEE_BRIDGE.md. This is a function-"
            "level under-constrained model, not a kernel/hardware run."
        ),
    }
    (run_dir / "summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (run_dir / "README.md").write_text(
        "# Historical ahci_xgene run " + run_id + "\n\n"
        "This directory is self-contained evidence for the Linux commit "
        "`8134233e8d346aaa1c929dc510e75482ae318bce` and its parent.  The full "
        "`xgene_ahci_probe()` body is in `harness/`, mapped to the original "
        "line numbers.  See `HARNESS_MAPPING.md`, `KLEE_BRIDGE.md`, and each "
        "candidate's raw and bridged warning JSON.  This is a function-level "
        "stub model, not a kernel build or hardware execution.\n",
        encoding="utf-8")
    print(f"run_dir={run_dir}", flush=True)
    if not result["target_h1_confirmed"] or result["target_h2_confirmed"]:
        print("HISTORICAL TARGET CHECK FAILED", file=sys.stderr)
        return 1
    print("HISTORICAL TARGET CHECK: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
