#!/usr/bin/env python3
"""Stepwise demo runner used by DEMO.sh.

Every step performs a real command in a fresh DEMO-* / HIST-* run directory.
Raw tool output stays in logs; the terminal receives only parsed stage
summaries.  Steps fail loudly when the current run is incomplete or when the
observed result does not match the documented case.

User-facing cases are ``tutorial`` (the backlog.c demo case) and ``history``
(the ahci_xgene case).  ``example`` is a compatibility alias: every entry
point normalizes it to ``tutorial``.  The authoritative state keys are
``tutorial_run`` / ``tutorial_step``; a one-time migration in
``scripts/demo_state_migration.py`` selects the run that was actually current
under v3 and preserves its physical path.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import sys

ROOT = pathlib.Path("/work")
LLVM = pathlib.Path("/opt/llvm7")
PLUGIN = ROOT / "build/bbtag/bbTaglib.so"
UBITECT = ROOT / "build/ubitect-original/ubitect"
UBITECT_NODEDUP = ROOT / "build/ubitect-nodedup/ubitect"
KLEE_ORIG = ROOT / "build/klee-original/bin/klee.noexport"
KLEE_EXPORT = ROOT / "build/klee-original/bin/klee"
PYTHON = ROOT / ".venv-linux/bin/python"
DEMO = ROOT / "demo"
STATE = DEMO / "state.json"
RUNS = DEMO / "runs"
HIST = ROOT / "history/ahci_xgene"
TARGET_LINES = {"h1": 825, "h2": 824}


def fail(message: str) -> None:
    raise SystemExit(f"DEMO FAILED: {message}")


def read_json(path: pathlib.Path, default=None):
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def write_json(path: pathlib.Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def require_file(path: pathlib.Path, hint: str) -> None:
    if not path.is_file():
        fail(f"missing {path}; {hint}")


def remove_path(path: pathlib.Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def state() -> dict:
    return read_json(STATE, {}) or {}


def save_state(s: dict) -> None:
    DEMO.mkdir(parents=True, exist_ok=True)
    write_json(STATE, s)


def run_cmd(argv: list[str], cwd: pathlib.Path, log: pathlib.Path) -> int:
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf-8", errors="replace") as f:
        f.write("$ " + shlex.join(argv) + "\n")
        f.flush()
        p = subprocess.run(argv, cwd=cwd, stdout=f, stderr=subprocess.STDOUT)
    return p.returncode


def parse_warnings(path: pathlib.Path) -> list[dict]:
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip().startswith("{"):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                fail(f"invalid warning JSON in {path}: {exc}")
    return rows


def confirm_lines(path: pathlib.Path) -> list[int]:
    if not path.is_file():
        return []
    result = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip():
            try:
                o = json.loads(line)
            except json.JSONDecodeError as exc:
                fail(f"invalid confirm_result JSON in {path}: {exc}")
            if o.get("find") == "Yes":
                result.append(int(o["lineNo"]))
    return sorted(set(result))


def ensure_migrated() -> None:
    """Apply the one-time v3 -> tutorial state migration inside the container."""
    import importlib.util
    path = ROOT / "scripts/demo_state_migration.py"
    if not path.is_file():
        return
    spec = importlib.util.spec_from_file_location("demo_state_migration", path)
    if spec is None or spec.loader is None:
        fail(f"cannot load state migration helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.migrate(ROOT, quiet=True)


def current(kind: str) -> pathlib.Path:
    if kind not in ("tutorial", "history"):
        fail(f"unknown demo case: {kind}")
    s = state()
    key = f"{kind}_run"
    value = s.get(key)
    if not value:
        fail(f"missing demo state: run './DEMO.sh source {kind}' first")
    p = RUNS / value
    if not p.is_dir():
        fail(f"missing demo run directory: {p}")
    return p


def new_run_id(prefix: str) -> str:
    """Return a fresh second-resolution run id, suffixed if already used."""
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    candidate = f"{prefix}-{stamp}"
    n = 2
    while (RUNS / candidate).exists():
        candidate = f"{prefix}-{stamp}-{n}"
        n += 1
    return candidate


def print_kv(label: str, **kw) -> None:
    print(f"[{label}]")
    for k, v in kw.items():
        print(f"  {k}: {v}")


# ---------------------------------------------------------------------------
# tutorial / backlog
# ---------------------------------------------------------------------------

def tutorial_source() -> None:
    run_id = new_run_id("DEMO")
    run = RUNS / run_id / "tutorial"
    (run / "source").mkdir(parents=True)
    shutil.copy2(ROOT / "source/UBITect/example/backlog.c", run / "source/backlog.c")
    s = state(); s["tutorial_run"] = str(run.relative_to(RUNS)); s["tutorial_step"] = "source"; save_state(s)
    lines = (run / "source/backlog.c").read_text(encoding="utf-8").splitlines()
    print(f"run={run_id}")
    print("case=tutorial")
    print("source=source/UBITect/example/backlog.c")
    for n in range(17, 31):
        print(f"{n:4d}  {lines[n-1]}")
    print("target lines: 25 = load/if(backlog); 26 = backlog->irq")


def tutorial_compile() -> None:
    run = current("tutorial")
    src = run / "source/backlog.c"
    require_file(src, "run './DEMO.sh source tutorial' first")
    out = run / "A"
    remove_path(out)
    out.mkdir()
    shutil.copy2(src, out / "backlog.c")
    rc = run_cmd([str(LLVM / "bin/clang"), "-emit-llvm", "-O0", "-g",
              "-fno-short-wchar", "-c", "backlog.c", "-o", "backlog.llbc"],
             out, out / "compile.log")
    if rc != 0:
        fail(f"clang failed rc={rc}; see {out / 'compile.log'}")
    rc = run_cmd([str(LLVM / "bin/llvm-dis"), "backlog.llbc", "-o", "backlog.ll"],
             out, out / "llvm-dis.log")
    if rc != 0:
        fail(f"llvm-dis failed rc={rc}; see {out / 'llvm-dis.log'}")
    rc = run_cmd([str(PYTHON), "-I", str(ROOT / "scripts/getbclist_py3.py"),
              "--llvm-dir", str(LLVM), "--plugin", str(PLUGIN),
              "--workdir", str(out)], out, out / "bbtag.log")
    if rc != 0:
        fail(f"bbTag failed rc={rc}; see {out / 'bbtag.log'}")
    run_cmd([str(LLVM / "bin/llvm-dis"), "backlog.bc", "-o", "backlog.bb.ll"],
        out, out / "llvm-dis-renamed.log")
    s = state(); s["tutorial_step"] = "compile"; save_state(s)
    blocks = re.findall(r"^(backlog\.llbc-test-[0-9]+):", (out / "backlog.bb.ll").read_text(), re.M)
    print_kv("compile tutorial", rc=rc, bitcode=str(out / "backlog.bc"),
             ir=str(out / "backlog.bb.ll"), blocks=", ".join(blocks),
             compile_log=str(out / "compile.log"),
             bbtag_log=str(out / "bbtag.log"))


def tutorial_candidates() -> None:
    run = current("tutorial")
    out = run / "A"
    require_file(out / "backlog.bc", "run './DEMO.sh compile tutorial' first")
    (out / "bitcode.list").write_text(str((out / "backlog.bc").resolve()) + "\n")
    rc = run_cmd([str(UBITECT), "-ubi-analysis", "@bitcode.list"], out,
             out / "stage1.log")
    if rc != 0:
        fail(f"UBITect failed rc={rc}; see {out / 'stage1.log'}")
    rows = parse_warnings(out / "warnings.json")
    if not rows:
        fail(f"no candidate in {out / 'warnings.json'}; inspect stage1.log")
    write_json(out / "warnings.parsed.json", rows)
    s = state(); s["tutorial_step"] = "candidates"; save_state(s)
    print_kv("candidates tutorial", rc=rc, candidates=len(rows),
             lines=", ".join(str(x.get("lineNo")) for x in rows),
             warnings=str(out / "warnings.json"),
             stage1_log=str(out / "stage1.log"))


def klee_one(warning: dict, run_dir: pathlib.Path, label: str,
             export: bool) -> tuple[int, list[int], pathlib.Path | None]:
    d = run_dir / label
    d.mkdir(parents=True, exist_ok=True)
    for name in ("confirm_result.json", "query.smt2", "exit_code.txt"):
        (d / name).unlink(missing_ok=True)
    for old in d.glob("klee-out-*"):
        remove_path(old)
    built = d / "built-in.bc"
    src = pathlib.Path(warning.get("bc") or "")
    if not src.is_file():
        fail(f"warning bitcode missing: {src}")
    rc = run_cmd([str(LLVM / "bin/llvm-link"), "-o", "built-in.bc", str(src)], d,
             d / "llvm-link.log")
    if rc != 0:
        (d / "exit_code.txt").write_text(str(rc) + "\n")
        return rc, [], None
    payload = json.dumps(warning)
    argv = [str(KLEE_EXPORT if export else KLEE_ORIG),
            f"-json={payload}", "./built-in.bc"]
    command_lines = [
        f"cd {shlex.quote(str(d))}",
        "source /work/scripts/container_env.sh",
    ]
    if export:
        command_lines.append(f"export UBITECT_SMT_DUMP={shlex.quote(str(d / 'query.smt2'))}")
    command_lines.append(" ".join(shlex.quote(x) for x in argv))
    (d / "command.txt").write_text("\n".join(command_lines) + "\n", encoding="utf-8")
    if export:
        env = {**os.environ, "UBITECT_SMT_DUMP": str(d / "query.smt2")}
        with (d / "klee.log").open("w", encoding="utf-8") as log:
            p = subprocess.run(argv, cwd=d, stdout=log, stderr=subprocess.STDOUT,
                               env=env)
        rc = p.returncode
    else:
        rc = run_cmd(argv, d, d / "klee.log")
    lines = confirm_lines(d / "confirm_result.json")
    (d / "exit_code.txt").write_text(str(rc) + "\n")
    return rc, lines, d / "query.smt2" if export and (d / "query.smt2").is_file() else None


def tutorial_verify() -> None:
    run = current("tutorial")
    out = run / "A"
    rows = parse_warnings(out / "warnings.json")
    if not rows:
        fail("no candidate; run './DEMO.sh candidates tutorial' first")
    if len(rows) != 1:
        fail(f"A expected 1 upstream candidate, got {len(rows)}; inspect {out / 'warnings.json'}")
    w = rows[0]
    cand = out / "candidate-01"
    remove_path(cand)
    cand.mkdir(parents=True)
    (cand / "warning.json").write_text(json.dumps(w) + "\n", encoding="utf-8")
    rc1, lines1, _ = klee_one(w, cand, "klee-original", False)
    if rc1 != 0:
        fail(f"original KLEE rc={rc1}; see {cand / 'klee-original/klee.log'}")
    rc2, lines2, q = klee_one(w, cand, "klee-smt-export", True)
    if rc2 != 0:
        fail(f"SMT-export KLEE rc={rc2}; see {cand / 'klee-smt-export/klee.log'}")
    if 25 not in lines1:
        fail(f"original KLEE did not confirm line 25; got {lines1}")
    if 25 not in lines2:
        fail(f"SMT-export KLEE did not confirm line 25; got {lines2}")
    if q is None:
        fail(f"no query.smt2 was exported under {cand / 'klee-smt-export'}")
    payload = {
        "run": str(run.relative_to(RUNS)),
        "candidate": "candidate-01",
        "lineNo": w.get("lineNo"),
        "original_rc": rc1,
        "export_rc": rc2,
        "confirmed_original": lines1,
        "confirmed_export": lines2,
        "query": str(q),
    }
    write_json(cand / "verify.json", payload)
    s = state(); s["tutorial_step"] = "verify"; save_state(s)
    print_kv("verify tutorial", original_rc=rc1, export_rc=rc2,
             confirmed=lines1, confirmed_export=lines2,
             query=str(q), verified_candidates="1/1",
             command=str(cand / "klee-smt-export/command.txt"),
             klee_log=str(cand / "klee-smt-export/klee.log"))


def tutorial_constraints() -> None:
    run = current("tutorial")
    q = run / "A/candidate-01/klee-smt-export/query.smt2"
    require_file(q, "run './DEMO.sh verify tutorial' first")
    d = q.parent
    rj = d / "z3-replay.json"
    remove_path(rj)
    rc = run_cmd([str(PYTHON), "-I", str(ROOT / "scripts/replay_z3.py"),
              str(q), "--json-out", str(rj)], d, d / "z3-replay.log")
    data = read_json(rj, {})
    if rc != 0 or not data:
        fail(f"Z3 replay failed rc={rc}; see {d / 'z3-replay.log'}")
    if data.get("result") != "sat":
        fail(f"expected sat for A line 25, got {data.get('result')}")
    s = state(); s["tutorial_step"] = "constraints"; save_state(s)
    print_kv("constraints tutorial", z3_rc=rc, result=data.get("result"),
             model=data.get("model"), query=str(q),
             replay_log=str(d / "z3-replay.log"))


def tutorial_compare() -> None:
    run = current("tutorial")
    a_dir = run / "A"
    require_file(a_dir / "backlog.bc", "run './DEMO.sh compile tutorial' first")
    a_conf = a_dir / "candidate-01/klee-original/confirm_result.json"
    a_query = a_dir / "candidate-01/klee-smt-export/query.smt2"
    require_file(a_conf, "run './DEMO.sh verify tutorial' first")
    require_file(a_query, "run './DEMO.sh verify tutorial' first")
    a_lines = confirm_lines(a_conf)

    original = (run / "source/backlog.c").read_text(encoding="utf-8")
    c_find = "        struct test_struct *backlog;\n"
    d_find = "        if(backlog){\n"
    if original.count(c_find) != 1:
        fail("could not apply C variant: declaration line not found exactly once")
    if original.count(d_find) != 1:
        fail("could not apply D variant: if(backlog) line not found exactly once")
    variants = {
        "A": (original, UBITECT),
        "B": (original, UBITECT_NODEDUP),
        "C": (original.replace(c_find,
                               "        struct test_struct *backlog = NULL;\n"),
              UBITECT),
        "D": (original.replace(d_find, "        if(a && backlog){\n"),
              UBITECT),
    }
    summary = []
    for name, (text, analyzer) in variants.items():
        d = run / "variants" / name
        remove_path(d)
        if name == "A":
            summary.append({
                "case": name, "candidates": len(parse_warnings(a_dir / "warnings.json")),
                "confirmed_objects": len(a_lines),
                "confirmed_use_points": a_lines,
                "lines": a_lines,
                "reused_current_run": True,
            })
            continue
        d.mkdir(parents=True)
        (d / "backlog.c").write_text(text, encoding="utf-8")
        rc = run_cmd([str(LLVM / "bin/clang"), "-emit-llvm", "-O0", "-g",
                  "-fno-short-wchar", "-c", "backlog.c", "-o", "backlog.llbc"],
                 d, d / "compile.log")
        if rc != 0:
            fail(f"{name}: compile failed rc={rc}; see {d / 'compile.log'}")
        rc = run_cmd([str(PYTHON), "-I", str(ROOT / "scripts/getbclist_py3.py"),
                 "--llvm-dir", str(LLVM), "--plugin", str(PLUGIN),
                 "--workdir", str(d)], d, d / "bbtag.log")
        if rc != 0:
            fail(f"{name}: bbTag failed rc={rc}; see {d / 'bbtag.log'}")
        (d / "bitcode.list").write_text(str((d / "backlog.bc").resolve()) + "\n")
        rc = run_cmd([str(analyzer), "-ubi-analysis", "@bitcode.list"], d,
                 d / "stage1.log")
        if rc != 0:
            fail(f"{name}: UBITect failed rc={rc}; see {d / 'stage1.log'}")
        rows = parse_warnings(d / "warnings.json")
        confirmed_objects = 0
        confirmed_lines: list[int] = []
        for i, w in enumerate(rows, 1):
            c = d / f"candidate-{i:02d}"
            c.mkdir()
            (c / "warning.json").write_text(json.dumps(w) + "\n", encoding="utf-8")
            rc2, lines, _ = klee_one(w, c, "klee-original", False)
            if rc2 != 0:
                fail(f"{name} candidate-{i:02d}: KLEE rc={rc2}; see {c / 'klee-original/klee.log'}")
            confirmed_objects += len(lines)
            confirmed_lines.extend(lines)
        summary.append({
            "case": name, "candidates": len(rows),
            "confirmed_objects": confirmed_objects,
            "confirmed_use_points": sorted(set(confirmed_lines)),
            "lines": sorted(set(confirmed_lines)),
        })
    expected = {
        "A": {"candidates": 1, "confirmed_objects": 1, "confirmed_use_points": [25]},
        "B": {"candidates": 2, "confirmed_objects": 2, "confirmed_use_points": [25, 26]},
        "C": {"candidates": 0, "confirmed_objects": 0, "confirmed_use_points": []},
        "D": {"candidates": 1, "confirmed_objects": 0, "confirmed_use_points": []},
    }
    write_json(run / "compare.json", summary)
    s = state(); s["tutorial_step"] = "compare"; save_state(s)
    print_kv("compare tutorial",
             **{x["case"]: f"{x['candidates']} candidates / {x['confirmed_objects']} confirmed objects / {x['confirmed_use_points']} use points"
                for x in summary})
    mismatches = []
    for x in summary:
        e = expected[x["case"]]
        for key in ("candidates", "confirmed_objects", "confirmed_use_points"):
            if x[key] != e[key]:
                mismatches.append(f"{x['case']}.{key}: got {x[key]!r}, expected {e[key]!r}")
    if mismatches:
        fail("A/B/C/D result mismatch: " + "; ".join(mismatches))


# ---------------------------------------------------------------------------
# history / ahci_xgene
# ---------------------------------------------------------------------------

def print_source_window(path: pathlib.Path, first: int, last: int) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    for n in range(first, last + 1):
        print(f"{n:4d}  {lines[n-1]}")


def history_source() -> None:
    run_id = dt.datetime.now(dt.timezone.utc).strftime("HIST-%Y%m%dT%H%M%SZ")
    run = RUNS / run_id / "history"
    run.mkdir(parents=True)
    for name in ("source", "provenance", "harness"):
        shutil.copytree(HIST / name, run / name)
    for name in ("HARNESS_MAPPING.md", "KLEE_BRIDGE.md"):
        shutil.copy2(HIST / name, run / name)
    s = state(); s["history_run"] = str(run.relative_to(RUNS)); s["history_step"] = "source"; save_state(s)
    print(f"run={run_id}")
    for v, src, line in (
        ("H1", "source/ahci_xgene.8ba559fd09bc.c", 825),
        ("H2", "source/ahci_xgene.8134233e8d34.c", 824),
    ):
        print(f"[{v}] official source: {src}; target line {line}")
    print("official patch: 8134233e8d346aaa1c929dc510e75482ae318bce")
    print("target: acpi_get_object_info() failure leaves info unassigned (no write to *out)")
    print("[H1 819-826]")
    print_source_window(run / "source/ahci_xgene.8ba559fd09bc.c", 819, 826)
    print("[H2 819-826]")
    print_source_window(run / "source/ahci_xgene.8134233e8d34.c", 819, 826)


def history_compile() -> None:
    run = current("history")
    for v in ("h1", "h2"):
        d = run / v
        remove_path(d)
        d.mkdir()
        src = run / "harness" / f"ahci_xgene_{v}.c"
        require_file(src, "run './DEMO.sh source history' first")
        shutil.copy2(src, d / src.name)
        rc = run_cmd([str(LLVM / "bin/clang"), "-emit-llvm", "-O0", "-g",
                  "-fno-short-wchar", "-DCONFIG_ACPI",
                  "-DHISTORY_ACPI_FAILURE_ONLY", "-c", src.name,
                  "-o", f"ahci_xgene_{v}.llbc"], d, d / "compile.log")
        if rc != 0:
            fail(f"{v}: compile failed rc={rc}; see {d / 'compile.log'}")
        rc = run_cmd([str(LLVM / "bin/llvm-dis"), f"ahci_xgene_{v}.llbc",
                  "-o", f"ahci_xgene_{v}.ll"], d, d / "llvm-dis.log")
        if rc != 0:
            fail(f"{v}: llvm-dis failed rc={rc}")
        rc = run_cmd([str(PYTHON), "-I", str(ROOT / "scripts/getbclist_py3.py"),
                  "--llvm-dir", str(LLVM), "--plugin", str(PLUGIN),
                  "--workdir", str(d)], d, d / "bbtag.log")
        if rc != 0:
            fail(f"{v}: bbTag failed rc={rc}; see {d / 'bbtag.log'}")
    s = state(); s["history_step"] = "compile"; save_state(s)
    print_kv("compile history", h1="ahci_xgene_h1.bc", h2="ahci_xgene_h2.bc",
             macro="HISTORY_ACPI_FAILURE_ONLY")


def history_candidates() -> None:
    run = current("history")
    rows_by = {}
    for v in ("h1", "h2"):
        d = run / v
        require_file(d / f"ahci_xgene_{v}.bc", "run './DEMO.sh compile history' first")
        (d / "bitcode.list").write_text(str((d / f"ahci_xgene_{v}.bc").resolve()) + "\n")
        rc = run_cmd([str(UBITECT), "-ubi-analysis", "@bitcode.list"], d, d / "stage1.log")
        if rc != 0:
            fail(f"{v}: UBITect failed rc={rc}; see {d / 'stage1.log'}")
        rows = parse_warnings(d / "warnings.json")
        if not rows:
            fail(f"{v}: no candidate in {d / 'warnings.json'}")
        rows_by[v] = rows
        write_json(d / "warnings.parsed.json", rows)
    s = state(); s["history_step"] = "candidates"; save_state(s)
    print_kv("candidates history",
             h1=f"{len(rows_by['h1'])} objects at lines {[r.get('lineNo') for r in rows_by['h1']]}",
             h2=f"{len(rows_by['h2'])} objects at lines {[r.get('lineNo') for r in rows_by['h2']]}")


def norm_inst(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"%[0-9]+", "%N", text.split("!", 1)[0].strip()))


def find_instruction(instructions: pathlib.Path, line_no: int, wanted: str) -> str | None:
    if not instructions.is_file():
        return None
    pattern = re.compile(r"^\s+.*:([0-9]+):([0-9]+):\s*(.*)$")
    target = norm_inst(wanted)
    for line in instructions.read_text(errors="replace").splitlines():
        m = pattern.match(line)
        if m and int(m.group(1)) == line_no:
            text = "  " + m.group(3).lstrip()
            if norm_inst(text) == target:
                return text
    return None


def replay_query(query: pathlib.Path) -> dict:
    rj = query.parent / "z3-replay.json"
    remove_path(rj)
    rc = run_cmd([str(PYTHON), "-I", str(ROOT / "scripts/replay_z3.py"),
              str(query), "--json-out", str(rj)], query.parent,
             query.parent / "z3-replay.log")
    data = read_json(rj, {})
    if rc != 0 or not data:
        fail(f"Z3 replay failed rc={rc}; see {query.parent / 'z3-replay.log'}")
    return data


def history_verify() -> None:
    run = current("history")
    results = {}
    for v, line_no in (("h1", TARGET_LINES["h1"]), ("h2", TARGET_LINES["h2"])):
        d = run / v
        rows = parse_warnings(d / "warnings.json")
        target = [x for x in rows if x.get("lineNo") == line_no]
        if not target:
            fail(f"{v}: no target warning at line {line_no}")
        c_root = d / "candidates"
        remove_path(c_root)
        c_root.mkdir()
        records = []
        for idx, w in enumerate(target, 1):
            c = c_root / f"candidate-{idx:02d}"
            c.mkdir()
            (c / "raw-warning.json").write_text(json.dumps(w) + "\n", encoding="utf-8")
            bridge = dict(w)
            bridge["function"] = "history_entry_failure"
            cal = c / "calibration"
            cal.mkdir()
            rc = run_cmd([str(LLVM / "bin/llvm-link"), "-o", "built-in.bc",
                      str(d / f"ahci_xgene_{v}.bc")], cal, cal / "llvm-link.log")
            if rc != 0:
                fail(f"{v} candidate-{idx:02d}: llvm-link failed rc={rc}")
            calib_argv = [str(KLEE_ORIG), "-debug-print-instructions=all:file",
                          f"-json={json.dumps(bridge)}", "./built-in.bc"]
            rc_cal = run_cmd(calib_argv, cal, cal / "klee.log")
            instr = find_instruction(cal / "klee-out-0/instructions.txt", line_no,
                                     w.get("warning", ""))
            bridge["warning"] = instr or w.get("warning", "")
            write_json(c / "klee-warning.json", bridge)
            write_json(c / "bridge.json", {
                "function": "xgene_ahci_probe -> history_entry_failure",
                "raw_warning_instruction": w.get("warning"),
                "klee_instruction": instr,
                "ssa_changed": instr is not None and norm_inst(instr) == norm_inst(w.get("warning", "")),
                "calibration_exit_code": rc_cal,
                "calibration_timed_out": False,
                "calibration_confirm": (cal / "confirm_result.json").is_file(),
            })
            if rc_cal != 0:
                fail(f"{v} candidate-{idx:02d}: calibration KLEE rc={rc_cal}; see {cal / 'klee.log'}")
            rc1, lines1, _ = klee_one(bridge, c, "klee-original", False)
            if rc1 != 0:
                fail(f"{v} candidate-{idx:02d}: original KLEE rc={rc1}; see {c / 'klee-original/klee.log'}")
            rc2, lines2, q = klee_one(bridge, c, "klee-smt-export", True)
            if rc2 != 0:
                fail(f"{v} candidate-{idx:02d}: SMT-export KLEE rc={rc2}; see {c / 'klee-smt-export/klee.log'}")
            replay = replay_query(q) if q else None
            rec = {
                "index": idx,
                "lineNo": w.get("lineNo"),
                "use": w.get("use"),
                "rank": w.get("rank"),
                "type": w.get("type"),
                "target": True,
                "bridge": {
                    "function": "history_entry_failure",
                    "instruction_found": instr is not None,
                    "instruction": instr,
                },
                "original": {"exit_code": rc1, "confirmed_lines": lines1,
                             "confirmed": bool(lines1)},
                "export": {"exit_code": rc2, "confirmed_lines": lines2,
                           "smt_exported": q is not None,
                           "query": str(q) if q else None,
                           "replay": replay},
            }
            write_json(c / "result.json", rec)
            records.append(rec)

        confirms = []
        for rec in records:
            p = c_root / f"candidate-{rec['index']:02d}" / "klee-original/confirm_result.json"
            if p.is_file():
                confirms.append(p.read_text(encoding="utf-8", errors="replace").rstrip("\n"))
        (d / "confirm_result.json").unlink(missing_ok=True)
        (d / "confirm_result.absent.txt").unlink(missing_ok=True)
        if confirms:
            (d / "confirm_result.json").write_text("\n".join(confirms) + "\n",
                                                   encoding="utf-8")
        else:
            (d / "confirm_result.absent.txt").write_text(
                "No target candidate was confirmed by KLEE in this case.\n",
                encoding="utf-8")

        confirmed_objects = sum(1 for r in records if r["original"]["confirmed"])
        confirmed_use_points = sorted({r["lineNo"] for r in records
                                       if r["original"]["confirmed"]})
        queries = [r["export"]["query"] for r in records if r["export"]["smt_exported"]]
        z3_results = [r["export"]["replay"].get("result")
                      for r in records if r["export"]["replay"]]
        results[v] = {
            "candidates": len(records),
            "confirmed_objects": confirmed_objects,
            "confirmed_use_points": confirmed_use_points,
            "queries": queries,
            "z3_results": z3_results,
            "bridge_found": sum(1 for r in records if r["bridge"]["instruction_found"]),
        }

    h1, h2 = results["h1"], results["h2"]
    if h1["confirmed_objects"] != h1["candidates"]:
        fail(f"H1 expected all {h1['candidates']} target objects confirmed, got {h1['confirmed_objects']}")
    if not h1["queries"]:
        fail("H1 confirmed but exported no query")
    if any(x != "sat" for x in h1["z3_results"]):
        fail(f"H1 expected sat for every replayed query, got {h1['z3_results']}")
    if h1["bridge_found"] != h1["candidates"]:
        fail(f"H1 bridge instruction found {h1['bridge_found']}/{h1['candidates']}")
    if h2["confirmed_objects"] != 0:
        fail(f"H2 target unexpectedly confirmed ({h2['confirmed_objects']} objects)")
    if h2["queries"]:
        fail(f"H2 exported {len(h2['queries'])} target query/queries; expected none")
    if h2["bridge_found"] != 0:
        fail(f"H2 calibration found {h2['bridge_found']} target instruction(s); expected none on the failure path")

    write_json(run / "verify.json", {"scope": "all target warning objects per version", **results})
    s = state(); s["history_step"] = "verify"; save_state(s)
    print_kv("verify history",
             scope="all target objects per version (this demo; matches the formal report count)",
             h1_candidates=h1["candidates"],
             h1_confirmed_objects=h1["confirmed_objects"],
             h1_confirmed_use_points=h1["confirmed_use_points"],
             h1_queries=len(h1["queries"]),
             h1_z3=h1["z3_results"],
             h2_candidates=h2["candidates"],
             h2_confirmed_objects=h2["confirmed_objects"],
             h2_queries=len(h2["queries"]))


def history_constraints() -> None:
    run = current("history")
    rows = []
    for q in sorted((run / "h1/candidates").glob("candidate-*/klee-smt-export/query.smt2")):
        data = replay_query(q)
        if data.get("result") != "sat":
            fail(f"H1 expected sat for {q}, got {data.get('result')}")
        rows.append((q.parent.parent.name, str(q), data))
    if not rows:
        fail("missing H1 query; run './DEMO.sh verify history' first")
    h2_queries = sorted((run / "h2/candidates").glob("candidate-*/klee-smt-export/query.smt2"))
    if h2_queries:
        fail(f"H2 unexpectedly has {len(h2_queries)} query.smt2 file(s)")
    s = state(); s["history_step"] = "constraints"; save_state(s)
    print_kv("constraints history",
             h1_queries=len(rows),
             h1_results=", ".join(f"{name}:{data.get('result')}" for name, _, data in rows),
             h1_model=rows[0][2].get("model"),
             h2_queries=0)


def history_compare() -> None:
    run = current("history")
    summaries = {}
    for v, line_no in (("h1", TARGET_LINES["h1"]), ("h2", TARGET_LINES["h2"])):
        c_root = run / v / "candidates"
        candidates = sorted(p for p in c_root.glob("candidate-*") if p.is_dir())
        if not candidates:
            fail(f"{v}: no candidate directories; run './DEMO.sh verify history' first")
        records = []
        for c in candidates:
            rec = read_json(c / "result.json")
            if not rec:
                fail(f"{v}: missing {c / 'result.json'}; run './DEMO.sh verify history' first")
            records.append(rec)
        target = [r for r in records if r.get("lineNo") == line_no]
        if not target:
            fail(f"{v}: no target result at line {line_no}")
        summaries[v] = {
            "candidates": len(records),
            "target_objects": len(target),
            "confirmed_objects": sum(1 for r in target if r["original"]["confirmed"]),
            "confirmed_use_points": sorted({r["lineNo"] for r in target
                                            if r["original"]["confirmed"]}),
            "queries": sum(1 for r in records if r["export"]["smt_exported"]),
            "z3_results": [r["export"]["replay"].get("result")
                           for r in records if r["export"]["replay"]],
            "bridge_found": sum(1 for r in records if r["bridge"]["instruction_found"]),
        }

    h1 = summaries["h1"]
    h2 = summaries["h2"]
    if h1["confirmed_objects"] != h1["target_objects"] or h1["confirmed_use_points"] != [825]:
        fail(f"H1 comparison failed: {h1}")
    if not h1["queries"] or any(x != "sat" for x in h1["z3_results"]):
        fail(f"H1 comparison failed: queries={h1['queries']} z3={h1['z3_results']}")
    if h2["confirmed_objects"] != 0 or h2["queries"] != 0:
        fail(f"H2 comparison failed: {h2}")

    h1_src = run / "source/ahci_xgene.8ba559fd09bc.c"
    h2_src = run / "source/ahci_xgene.8134233e8d34.c"
    patch = run / "provenance/official-fix.patch"
    require_file(h1_src, "run './DEMO.sh source history' first")
    require_file(h2_src, "run './DEMO.sh source history' first")
    require_file(patch, "run './DEMO.sh source history' first")
    h1_lines = h1_src.read_text(encoding="utf-8").splitlines()
    h2_lines = h2_src.read_text(encoding="utf-8").splitlines()
    if "if (info->valid & ACPI_VALID_CID)" not in h1_lines[824]:
        fail("H1 line 825 is not the expected info->valid read")
    if "} else if (info->valid & ACPI_VALID_CID)" not in h2_lines[823]:
        fail("H2 line 824 is not the expected else-if guard")
    if "} else if (info->valid & ACPI_VALID_CID)" not in patch.read_text(encoding="utf-8"):
        fail("official patch does not contain the expected else-if hunk")

    payload = {
        "run": run.name,
        "scope": "function-level failure-only harness; all target objects",
        "h1": h1,
        "h2": h2,
        "source_checks": {
            "h1_line_825": h1_lines[824].strip(),
            "h2_line_824": h2_lines[823].strip(),
            "official_patch": str(patch),
        },
    }
    write_json(run / "compare.json", payload)
    s = state(); s["history_step"] = "compare"; save_state(s)
    print_kv("compare history",
             run=run.name,
             h1=f"{h1['confirmed_objects']}/{h1['target_objects']} target objects confirmed; use points {h1['confirmed_use_points']}; queries {h1['queries']} ({', '.join(h1['z3_results'])})",
             h2=f"{h2['confirmed_objects']}/{h2['target_objects']} target objects confirmed; target queries {h2['queries']} (expected 0)",
             patch="official fix changes the failure branch to else-if (H2 line 824)",
             boundary="failure-only stubs; input_0=0 is the entry selector, not attacker input")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action")
    ap.add_argument("case")
    args = ap.parse_args()
    if args.case == "example":
        print("note: 'example' is a compatibility alias for 'tutorial'; "
              "using tutorial.", file=sys.stderr)
        args.case = "tutorial"
    if args.case not in ("tutorial", "history"):
        fail("case must be tutorial or history (example is an alias for tutorial)")
    ensure_migrated()
    fn = globals().get(f"{args.case}_{args.action}")
    if fn is None:
        fail(f"unknown step: {args.case} {args.action}")
    fn()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
