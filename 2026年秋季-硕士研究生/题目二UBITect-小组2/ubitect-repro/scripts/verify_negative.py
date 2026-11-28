#!/usr/bin/env python3
"""Isolated negative checks for missing DEMO evidence.

A synthetic state points at an empty run directory.  Four commands that need
missing query/result files must exit non-zero, print ``DEMO FAILED``, and must
not print a SAT result, a confirmed count, or a success summary.  The real
``demo/state.json`` is restored byte-for-byte and the synthetic run is removed
afterwards; logs and the JSON record are kept as evidence.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEMO = ROOT / "DEMO.sh"
STATE = ROOT / "demo/state.json"
RUNS = ROOT / "demo/runs"
LOGS = ROOT / "logs"
CASES = [
    (["constraints", "tutorial"], "missing tutorial query.smt2"),
    (["compare", "tutorial"], "missing tutorial A/backlog.bc"),
    (["verify", "history"], "missing history warnings.json"),
    (["compare", "history"], "missing history candidate results"),
]
SUCCESS_RE = re.compile(
    r"(result:\s*sat|confirmed_objects=|confirmed_use_points=\[|"
    r"STATUS:\s*COMPLETE|DEMO VERIFICATION:\s*PASS)")


def main() -> int:
    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    if not STATE.is_file():
        print("FAIL: demo/state.json missing", file=sys.stderr)
        return 1
    synthetic_id = f"TEST-MISSING-{stamp}"
    synthetic = RUNS / synthetic_id
    logs = LOGS / f"demo-negative-{stamp}"
    logs.mkdir(parents=True, exist_ok=False)
    (synthetic / "tutorial" / "A").mkdir(parents=True)
    (synthetic / "history").mkdir(parents=True)

    start = subprocess.run([str(DEMO), "start"], cwd=ROOT, text=True,
                           capture_output=True)
    if start.returncode != 0:
        print("FAIL: could not start the project container", file=sys.stderr)
        print(start.stdout, start.stderr, file=sys.stderr)
        shutil.rmtree(synthetic, ignore_errors=True)
        return 1

    # Read the state after `start` so a first-run naming migration is included
    # in the byte-for-byte restore.
    original = STATE.read_bytes()
    state = json.loads(original)
    state["tutorial_run"] = f"{synthetic_id}/tutorial"
    state["tutorial_step"] = "source"
    state["history_run"] = f"{synthetic_id}/history"
    state["history_step"] = "source"
    STATE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n",
                     encoding="utf-8")

    results = []
    ok = True
    try:
        for i, (args, reason) in enumerate(CASES, 1):
            log = logs / f"{i:02d}-{'-'.join(args)}.log"
            p = subprocess.run([str(DEMO), *args], cwd=ROOT, text=True,
                               capture_output=True)
            output = p.stdout + p.stderr
            log.write_text(f"$ ./DEMO.sh {' '.join(args)}\n{output}",
                           encoding="utf-8")
            success = bool(SUCCESS_RE.search(output))
            good = p.returncode != 0 and "DEMO FAILED" in output and not success
            ok = ok and good
            results.append({
                "command": ["./DEMO.sh", *args],
                "missing": reason,
                "exit_code": p.returncode,
                "demo_failed": "DEMO FAILED" in output,
                "success_marker_found": success,
                "pass": good,
                "log": str(log.relative_to(ROOT)),
                "first_failure_line": next(
                    (line for line in output.splitlines() if "DEMO FAILED" in line),
                    ""),
            })
            print(f"{'PASS' if good else 'FAIL'} ./DEMO.sh {' '.join(args)} "
                  f"rc={p.returncode} success_marker={success}")
    finally:
        STATE.write_bytes(original)
        shutil.rmtree(synthetic, ignore_errors=True)

    restored = STATE.read_bytes() == original
    ok = ok and restored
    payload = {
        "tested_at_utc": now.isoformat(),
        "synthetic_run": synthetic_id,
        "state_restored_byte_for_byte": restored,
        "all_pass": ok,
        "checks": results,
        "log_dir": str(logs.relative_to(ROOT)),
    }
    record = ROOT / "demo" / f"negative-{stamp}.json"
    record.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"state restored byte-for-byte: {restored}")
    print(f"record: {record.relative_to(ROOT)}")
    print("NEGATIVE VERIFICATION:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
