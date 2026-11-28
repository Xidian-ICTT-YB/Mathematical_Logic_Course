#!/usr/bin/env python3
"""Run the four UBITect backlog.c experiments and preserve real evidence.

This runs inside the linux/amd64 container.  It intentionally uses the author's
custom KLEE and the author's Z3 path encoder; it does not replace symbolic
execution with a hand-written solver script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = pathlib.Path("/work")
LLVM = pathlib.Path("/opt/llvm7")
KLEE_ORIGINAL = ROOT / "build/klee-original/bin/klee.noexport"
KLEE_EXPORT = ROOT / "build/klee-original/bin/klee"
UBITECT_ORIGINAL = ROOT / "build/ubitect-original/ubitect"
UBITECT_NODEDUP = ROOT / "build/ubitect-nodedup/ubitect"
PLUGIN = ROOT / "build/bbtag/bbTaglib.so"
ARTIFACTS = ROOT / "artifacts"
UPSTREAM_EXAMPLE = ROOT / "source/UBITect/example/backlog.c"


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def command_text(argv: list[str]) -> str:
    return shlex.join(argv)


def run_command(
    argv: list[str],
    cwd: pathlib.Path,
    log_path: pathlib.Path,
    timeout: int | None = None,
    extra_env: dict[str, str] | None = None,
    append: bool = False,
) -> dict:
    """Run a command, save command + combined output, and always keep its rc."""
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    mode = "a" if append else "w"
    start = time.monotonic()
    timed_out = False
    with log_path.open(mode, encoding="utf-8", errors="replace") as log:
        log.write(f"$ {command_text(argv)}\n")
        log.flush()
        proc = subprocess.Popen(
            argv,
            cwd=str(cwd),
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
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
    duration = round(time.monotonic() - start, 3)
    return {
        "argv": argv,
        "shell": command_text(argv),
        "cwd": str(cwd),
        "exit_code": proc.returncode,
        "timed_out": timed_out,
        "duration_s": duration,
        "log": str(log_path),
    }


def parse_warning_stream(path: pathlib.Path) -> list[dict]:
    """Parse the author's 'bc path line' + 'JSON object line' alternating stream."""
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    warnings = []
    pending_path = None
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("{"):
            obj = json.loads(stripped)
            warnings.append(
                {
                    "bc_line": pending_path,
                    "warning": obj,
                    "raw_warning": stripped,
                }
            )
            pending_path = None
        else:
            if pending_path is not None:
                raise ValueError(f"{path}: two path lines without a JSON object")
            pending_path = line
    if pending_path is not None:
        raise ValueError(f"{path}: trailing path line without JSON object")
    return warnings


def parse_confirm(path: pathlib.Path) -> dict:
    if not path.is_file():
        return {"exists": False, "raw": "", "objects": []}
    raw = path.read_text(encoding="utf-8", errors="replace")
    objects = []
    for line in raw.splitlines():
        if line.strip():
            objects.append(json.loads(line))
    return {"exists": True, "raw": raw, "objects": objects}


def bc_paths(bc_line: str | None) -> list[str]:
    if not bc_line:
        return []
    value = bc_line.rstrip("\n")
    if value.endswith(":"):
        value = value[:-1]
    return [part for part in value.split(":") if part]


def prepare_case_source(case_id: str, text: str, case_dir: pathlib.Path) -> None:
    case_dir.mkdir(parents=True, exist_ok=False)
    (case_dir / "backlog.c").write_text(text, encoding="utf-8")


def case_summary(case_id: str, title: str, case_dir: pathlib.Path, warnings: list[dict],
                 candidate_records: list[dict], analyzer: pathlib.Path,
                 config_note: str) -> dict:
    original_confirms = []
    export_confirms = []
    for rec in candidate_records:
        original_confirms.extend(rec["original"]["confirmed_lines"])
        export_confirms.extend(rec["export"]["confirmed_lines"])
    summary = {
        "case": case_id,
        "title": title,
        "config_note": config_note,
        "analyzer": str(analyzer),
        "analyzer_sha256": sha256(analyzer),
        "candidate_count": len(warnings),
        "candidate_lines": [w["warning"].get("lineNo") for w in warnings],
        "candidate_uses": [w["warning"].get("use") for w in warnings],
        "confirmed_count_default_reporting": len(original_confirms),
        "confirmed_lines_default_reporting": sorted(set(original_confirms)),
        "confirmed_count_smt_export_build": len(export_confirms),
        "confirmed_lines_smt_export_build": sorted(set(export_confirms)),
        "candidates": candidate_records,
    }
    (case_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def run_klee_variant(
    candidate_dir: pathlib.Path,
    label: str,
    klee_bin: pathlib.Path,
    raw_warning: str,
    paths: list[str],
    export_smt: bool,
) -> dict:
    run_dir = candidate_dir / label
    run_dir.mkdir(parents=True, exist_ok=False)
    link_argv = [str(LLVM / "bin/llvm-link"), "-o", "built-in.bc"] + paths
    link_res = run_command(link_argv, run_dir, run_dir / "llvm-link.log", timeout=60)
    if link_res["exit_code"] != 0:
        return {
            "exit_code": link_res["exit_code"],
            "timed_out": False,
            "confirmed": False,
            "confirmed_lines": [],
            "confirm_result_exists": False,
            "command": None,
            "link": link_res,
            "duration_s": link_res["duration_s"],
            "smt_exported": False,
            "smt_replay": None,
        }

    klee_argv = [str(klee_bin), f"-json={raw_warning}", "./built-in.bc"]
    extra_env = {}
    smt_path = run_dir / "query.smt2"
    if export_smt:
        extra_env["UBITECT_SMT_DUMP"] = str(smt_path)
    else:
        # Never let an inherited diagnostic variable turn the preserved
        # no-export binary into an exporter by accident.
        extra_env["UBITECT_SMT_DUMP"] = ""
    klee_res = run_command(
        klee_argv, run_dir, run_dir / "klee.log", timeout=120, extra_env=extra_env
    )
    (run_dir / "command.json").write_text(
        json.dumps({"argv": klee_argv, "cwd": str(run_dir)}, indent=2) + "\n",
        encoding="utf-8",
    )
    (run_dir / "command.sh").write_text(
        "cd " + shlex.quote(str(run_dir)) + "\n" + shlex.join(klee_argv) + "\n",
        encoding="utf-8",
    )
    confirm_path = run_dir / "confirm_result.json"
    confirm = parse_confirm(confirm_path)
    log = (run_dir / "klee.log").read_text(encoding="utf-8", errors="replace")
    confirmed_lines = sorted(
        {
            int(obj["lineNo"])
            for obj in confirm["objects"]
            if obj.get("find") == "Yes" and "lineNo" in obj
        }
    )
    confirmed = bool(confirmed_lines) and "[SrcCode]" in log

    smt_replay = None
    if smt_path.is_file():
        replay_json = run_dir / "z3-replay.json"
        replay_argv = [
            str(ROOT / ".venv-linux/bin/python"),
            "-I",
            str(ROOT / "scripts/replay_z3.py"),
            str(smt_path),
            "--json-out",
            str(replay_json),
        ]
        replay_res = run_command(
            replay_argv, run_dir, run_dir / "z3-replay.log", timeout=120
        )
        smt_replay = {
            "exit_code": replay_res["exit_code"],
            "result": None,
            "model": None,
        }
        if replay_json.is_file():
            smt_replay.update(json.loads(replay_json.read_text(encoding="utf-8")))

    return {
        "exit_code": klee_res["exit_code"],
        "timed_out": klee_res["timed_out"],
        "duration_s": klee_res["duration_s"],
        "confirmed": confirmed,
        "confirmed_lines": confirmed_lines,
        "confirm_result_exists": confirm["exists"],
        "command": klee_res,
        "link": link_res,
        "smt_exported": smt_path.is_file(),
        "smt_replay": smt_replay,
    }


def run_case(
    case_id: str,
    title: str,
    source_text: str,
    analyzer: pathlib.Path,
    config_note: str,
) -> dict:
    case_dir = ARTIFACTS / f"{case_id}_{title}"
    if case_dir.exists():
        shutil.rmtree(case_dir)
    prepare_case_source(case_id, source_text, case_dir)

    compile_argv = [
        str(LLVM / "bin/clang"),
        "-emit-llvm",
        "-O0",
        "-g",
        "-fno-short-wchar",
        "-c",
        "backlog.c",
        "-o",
        "backlog.llbc",
    ]
    compile_res = run_command(
        compile_argv, case_dir, case_dir / "compile.log", timeout=60
    )
    (case_dir / "compile_command.txt").write_text(
        compile_res["shell"] + "\n", encoding="utf-8"
    )
    if compile_res["exit_code"] != 0:
        raise RuntimeError(f"{case_id}: clang failed, see {case_dir}/compile.log")

    wrapper_argv = [
        str(ROOT / ".venv-linux/bin/python"),
        "-I",
        str(ROOT / "scripts/getbclist_py3.py"),
        "--llvm-dir",
        str(LLVM),
        "--plugin",
        str(PLUGIN),
        "--workdir",
        str(case_dir),
    ]
    wrapper_res = run_command(
        wrapper_argv, case_dir, case_dir / "bbtag.log", timeout=120
    )
    (case_dir / "bbtag_command.txt").write_text(
        wrapper_res["shell"] + "\n", encoding="utf-8"
    )
    (case_dir / "bbtag_exit_code.txt").write_text(
        str(wrapper_res["exit_code"]) + "\n", encoding="utf-8"
    )
    if wrapper_res["exit_code"] != 0:
        raise RuntimeError(f"{case_id}: bbTag wrapper failed, see bbtag.log")

    dis_argv = [
        str(LLVM / "bin/llvm-dis"),
        "backlog.bc",
        "-o",
        "backlog.ll",
    ]
    dis_res = run_command(dis_argv, case_dir, case_dir / "llvm-dis.log", timeout=60)
    if dis_res["exit_code"] != 0:
        raise RuntimeError(f"{case_id}: llvm-dis failed")

    analyzer_argv = [str(analyzer), "-ubi-analysis", "@bitcode.list"]
    analyzer_res = run_command(
        analyzer_argv, case_dir, case_dir / "stage1.log", timeout=120
    )
    (case_dir / "stage1_command.txt").write_text(
        analyzer_res["shell"] + "\n", encoding="utf-8"
    )
    (case_dir / "stage1_exit_code.txt").write_text(
        str(analyzer_res["exit_code"]) + "\n", encoding="utf-8"
    )
    if analyzer_res["exit_code"] != 0:
        raise RuntimeError(f"{case_id}: UBITect failed, see stage1.log")

    warnings = parse_warning_stream(case_dir / "warnings.json")
    if not (case_dir / "warnings.json").is_file():
        (case_dir / "warnings.absent.txt").write_text(
            "The analyzer emitted no warnings.json for this source (no candidates).\n",
            encoding="utf-8",
        )
    (case_dir / "warnings.parsed.json").write_text(
        json.dumps(warnings, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    candidate_records = []
    candidate_root = case_dir / "candidates"
    candidate_root.mkdir()
    for index, warning in enumerate(warnings, 1):
        line_no = warning["warning"].get("lineNo")
        cand_dir = candidate_root / f"candidate-{index:02d}-line-{line_no}"
        cand_dir.mkdir()
        (cand_dir / "warning.json").write_text(
            warning["raw_warning"] + "\n", encoding="utf-8"
        )
        (cand_dir / "warning-context.json").write_text(
            json.dumps(
                {"bc_line": warning["bc_line"], "warning": warning["warning"]},
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        paths = bc_paths(warning["bc_line"])
        if not paths:
            raise RuntimeError(f"{case_id}: candidate has no bitcode path")
        original = run_klee_variant(
            cand_dir,
            "klee-original",
            KLEE_ORIGINAL,
            warning["raw_warning"],
            paths,
            export_smt=False,
        )
        export = run_klee_variant(
            cand_dir,
            "klee-smt-export",
            KLEE_EXPORT,
            warning["raw_warning"],
            paths,
            export_smt=True,
        )
        record = {
            "index": index,
            "lineNo": warning["warning"].get("lineNo"),
            "use": warning["warning"].get("use"),
            "bc_line": warning["bc_line"],
            "original": original,
            "export": export,
            "same_confirmation": original["confirmed_lines"] == export["confirmed_lines"],
        }
        (cand_dir / "result.json").write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        candidate_records.append(record)

    original_raw = []
    export_raw = []
    for rec in candidate_records:
        for label, bucket in (
            ("klee-original", original_raw),
            ("klee-smt-export", export_raw),
        ):
            cand_dir = candidate_root / f"candidate-{rec['index']:02d}-line-{rec['lineNo']}"
            p = cand_dir / label / "confirm_result.json"
            if p.is_file():
                bucket.append(p.read_text(encoding="utf-8", errors="replace").rstrip("\n"))
    if original_raw:
        (case_dir / "confirm_result.json").write_text(
            "\n".join(original_raw) + "\n", encoding="utf-8"
        )
        (case_dir / "confirm_result.export-build.json").write_text(
            "\n".join(export_raw) + "\n", encoding="utf-8"
        )
    else:
        (case_dir / "confirm_result.absent.txt").write_text(
            "No KLEE confirm_result.json was produced (no candidate was confirmed).\n",
            encoding="utf-8",
        )

    note = (
        f"Case {case_id}: {title}\n"
        f"Config: {config_note}\n"
        "Authoritative confirmation run: candidates/*/klee-original (unmodified KLEE binary).\n"
        "Diagnostic comparison: candidates/*/klee-smt-export (same source plus an\n"
        "environment-gated dump immediately before the real Z3 check()).\n"
        "Each candidate directory preserves its own raw confirm_result.json.\n"
        "The case-level confirm_result.json is the same raw-line concatenation the\n"
        "author's parallel path_verify.py performs; it is not a rewritten object.\n"
    )
    (case_dir / "README.txt").write_text(note, encoding="utf-8")
    summary = case_summary(
        case_id,
        title,
        case_dir,
        warnings,
        candidate_records,
        analyzer,
        config_note,
    )
    print(
        f"{case_id}: candidates={summary['candidate_count']} "
        f"lines={summary['candidate_lines']} "
        f"confirmed(original)={summary['confirmed_lines_default_reporting']} "
        f"confirmed(export build)={summary['confirmed_lines_smt_export_build']}",
        flush=True,
    )
    return summary


def write_independent_analysis(real_queries: list[tuple[str, pathlib.Path]]) -> dict:
    out = ARTIFACTS / "analysis"
    if out.exists():
        shutil.rmtree(out)
    (out / "real-exports").mkdir(parents=True)
    (out / "independent").mkdir(parents=True)
    manifest = {
        "note": (
            "real-exports are unchanged SMT-LIB dumps from the author's KLEE/Z3 "
            "encoder. independent formulas are explicitly reconstructed for "
            "teaching and are NOT presented as KLEE logs."
        ),
        "z3_version": None,
        "real_exports": [],
        "independent": [],
    }
    for label, src in real_queries:
        if not src.is_file():
            continue
        dst = out / "real-exports" / f"{label}.smt2"
        shutil.copy2(src, dst)
        replay_json = dst.with_suffix(".result.json")
        replay_argv = [
            str(ROOT / ".venv-linux/bin/python"),
            "-I",
            str(ROOT / "scripts/replay_z3.py"),
            str(dst),
            "--json-out",
            str(replay_json),
        ]
        res = run_command(replay_argv, out, dst.with_suffix(".replay.log"), timeout=120)
        entry = {
            "label": label,
            "source": str(src),
            "smt2": str(dst),
            "sha256": sha256(dst),
            "replay_exit_code": res["exit_code"],
        }
        if replay_json.is_file():
            data = json.loads(replay_json.read_text(encoding="utf-8"))
            manifest["z3_version"] = data.get("z3_version")
            entry.update({"result": data.get("result"), "model": data.get("model")})
        manifest["real_exports"].append(entry)

    independent = {
        "a_zero_and_nonzero_32bit.smt2": """; Independent teaching reconstruction (not a KLEE log).
(set-logic QF_BV)
(declare-fun a () (_ BitVec 32))
(assert (= a #x00000000))
(assert (distinct a #x00000000))
(check-sat)
""",
        "line25_skip_init_32bit.smt2": """; Independent teaching reconstruction (not a KLEE log).
; To skip the initializing block, a == 0.  Reading backlog for if(backlog)
; does not require any constraint on the pointer's residual value.
(set-logic QF_BV)
(declare-fun a () (_ BitVec 32))
(declare-fun backlog () (_ BitVec 64))
(assert (= a #x00000000))
(check-sat)
(get-value (a backlog))
""",
        "line26_requires_nonnull_32bit.smt2": """; Independent teaching reconstruction (not a KLEE log).
; Line 26 is reached only through the true edge of if(backlog).  In addition
; to skipping initialization (a == 0), the residual pointer must be non-zero.
(set-logic QF_BV)
(declare-fun a () (_ BitVec 32))
(declare-fun backlog () (_ BitVec 64))
(assert (= a #x00000000))
(assert (distinct backlog #x0000000000000000))
(check-sat)
(get-value (a backlog))
""",
        "line26_zero_residual_32bit.smt2": """; Independent teaching reconstruction (not a KLEE log).
; Counterexample to line 26 when the residual pointer is zero.
(set-logic QF_BV)
(declare-fun a () (_ BitVec 32))
(declare-fun backlog () (_ BitVec 64))
(assert (= a #x00000000))
(assert (= backlog #x0000000000000000))
(assert (distinct backlog #x0000000000000000))
(check-sat)
""",
    }
    for name, text in independent.items():
        p = out / "independent" / name
        p.write_text(text, encoding="utf-8")
        replay_json = p.with_suffix(".result.json")
        replay_argv = [
            str(ROOT / ".venv-linux/bin/python"),
            "-I",
            str(ROOT / "scripts/replay_z3.py"),
            str(p),
            "--json-out",
            str(replay_json),
        ]
        res = run_command(replay_argv, out, p.with_suffix(".replay.log"), timeout=120)
        entry = {
            "label": name,
            "smt2": str(p),
            "sha256": sha256(p),
            "replay_exit_code": res["exit_code"],
        }
        if replay_json.is_file():
            data = json.loads(replay_json.read_text(encoding="utf-8"))
            manifest["z3_version"] = data.get("z3_version")
            entry.update({"result": data.get("result"), "model": data.get("model")})
        manifest["independent"].append(entry)

    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out / "README.md").write_text(
        "# SAT/SMT evidence\n\n"
        "`real-exports/` contains queries exported by the instrumented KLEE build "
        "immediately before its real `z3_solverr.check()`.  The independent "
        "formulas are teaching reconstructions, not raw KLEE output.\n\n"
        "Key observation: the real query declares `input_0` as a 64-bit bitvector "
        "even though the C parameter `a` is a 32-bit `int`.  This is the author "
        "encoder's `BIT_WIDTH 64` choice, not a 32-bit encoding.\n\n"
        "The D short-circuit candidate has no real export: KLEE terminates the "
        "guided paths before the use block, so it never calls checkUseList().  "
        "The independent a=0-and-a!=0 UNSAT formula must not be described as a "
        "KLEE UNSAT log.\n",
        encoding="utf-8",
    )
    return manifest


def upstream_commit() -> str:
    marker = ROOT / "source/UBITect/UPSTREAM_COMMIT"
    if marker.is_file():
        return marker.read_text(encoding="utf-8").strip()
    return subprocess.check_output(
        ["git", "-C", str(ROOT / "source/UBITect"), "rev-parse", "HEAD"],
        text=True,
    ).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-cases", default="", help="comma-separated A,B,C,D")
    args = ap.parse_args()
    skip = {x.strip().upper() for x in args.skip_cases.split(",") if x.strip()}

    for path in (KLEE_ORIGINAL, KLEE_EXPORT, UBITECT_ORIGINAL, UBITECT_NODEDUP,
                 PLUGIN, LLVM / "bin/clang", UPSTREAM_EXAMPLE):
        if not path.exists():
            print(f"FATAL: missing prerequisite {path}", file=sys.stderr)
            return 2

    ARTIFACTS.mkdir(exist_ok=True)
    original_text = UPSTREAM_EXAMPLE.read_text(encoding="utf-8")
    c_text = original_text.replace(
        "        struct test_struct *backlog;\n",
        "        struct test_struct *backlog = NULL;\n",
    )
    if c_text == original_text:
        raise RuntimeError("could not create C variant")
    d_text = original_text.replace("        if(backlog){\n", "        if(a && backlog){\n")
    if d_text == original_text:
        raise RuntimeError("could not create D variant")

    specs = [
        (
            "A",
            "original_default_dedup",
            original_text,
            UBITECT_ORIGINAL,
            "upstream warningReported() default; unmodified KLEE",
        ),
        (
            "B",
            "no_dedup_reporting",
            original_text,
            UBITECT_NODEDUP,
            "teaching build with -DUBITECT_NO_DEDUP; reporting granularity only",
        ),
        (
            "C",
            "null_initialization_fix",
            c_text,
            UBITECT_ORIGINAL,
            "source-level control: backlog initialized to NULL",
        ),
        (
            "D",
            "short_circuit_control",
            d_text,
            UBITECT_ORIGINAL,
            "source-level control: if(a && backlog)",
        ),
    ]

    summaries = []
    for case_id, title, text, analyzer, note in specs:
        if case_id in skip:
            continue
        summaries.append(run_case(case_id, title, text, analyzer, note))

    real_queries = []
    for case_id in ("A", "B", "C", "D"):
        case_dirs = sorted(ARTIFACTS.glob(f"{case_id}_*"))
        for case_dir in case_dirs:
            for cand_dir in sorted((case_dir / "candidates").glob("candidate-*")):
                q = cand_dir / "klee-smt-export" / "query.smt2"
                if q.is_file():
                    real_queries.append(
                        (f"{case_id}_{cand_dir.name}", q)
                    )
    analysis = write_independent_analysis(real_queries)

    root_summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "container_arch": os.uname().machine,
        "llvm_version": subprocess.check_output(
            [str(LLVM / "bin/llvm-config"), "--version"], text=True
        ).strip(),
        "llvm_has_rtti": subprocess.check_output(
            [str(LLVM / "bin/llvm-config"), "--has-rtti"], text=True
        ).strip(),
        "klee_original_sha256": sha256(KLEE_ORIGINAL),
        "klee_export_build_sha256": sha256(KLEE_EXPORT),
        "ubitect_original_sha256": sha256(UBITECT_ORIGINAL),
        "ubitect_nodedup_sha256": sha256(UBITECT_NODEDUP),
        "bbtag_sha256": sha256(PLUGIN),
        "upstream_commit": upstream_commit(),
        "cases": summaries,
        "analysis_manifest": str(ARTIFACTS / "analysis/manifest.json"),
        "z3_real_query_versions": analysis.get("z3_version"),
    }
    (ARTIFACTS / "summary.json").write_text(
        json.dumps(root_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    lines = [
        "# Four-case result summary",
        "",
        "| case | candidates (lines) | confirmed, original KLEE | confirmed, SMT-export build |",
        "|---|---|---|---|",
    ]
    for s in summaries:
        lines.append(
            f"| {s['case']} {s['title']} | {s['candidate_count']} "
            f"({s['candidate_lines']}) | {s['confirmed_count_default_reporting']} "
            f"({s['confirmed_lines_default_reporting']}) | "
            f"{s['confirmed_count_smt_export_build']} "
            f"({s['confirmed_lines_smt_export_build']}) |"
        )
    lines += [
        "",
        "`klee-original` means the preserved binary built before the SMT-dump patch.",
        "`klee-smt-export` is the same analysis with an environment-gated dump immediately",
        "before the real Z3 `check()`; confirmation line sets must match.",
        "",
    ]
    (ARTIFACTS / "SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
