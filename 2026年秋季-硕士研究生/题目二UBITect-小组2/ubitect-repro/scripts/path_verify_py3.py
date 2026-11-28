#!/usr/bin/env python3
"""Author-compatible, sequential Python 3 replacement for path_verify.py.

It parses the author's alternating warnings.json stream, invokes the real
LLVM 7 llvm-link, and invokes the author's custom KLEE once per candidate with
the original warning JSON.  There is no psutil or Python 2 dependency.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import shlex
import subprocess
import sys


def parse_stream(path: pathlib.Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    result = []
    bc_line = None
    for line in lines:
        line = line.rstrip("\n")
        if not line.strip():
            continue
        if line.lstrip().startswith("{"):
            if bc_line is None:
                raise ValueError("JSON object without a preceding bc path line")
            result.append({"bc_line": bc_line, "raw_json": line})
            bc_line = None
        else:
            if bc_line is not None:
                raise ValueError("two bc path lines without a JSON object")
            bc_line = line
    if bc_line is not None:
        raise ValueError("trailing bc path line without JSON object")
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("warnings_json")
    ap.add_argument("--klee", default="/work/build/klee-original/bin/klee.noexport")
    ap.add_argument("--llvm-link", default="/opt/llvm7/bin/llvm-link")
    ap.add_argument("--home", default="/work")
    ap.add_argument("--out", default=".")
    ap.add_argument("--timeout", type=int, default=120)
    args = ap.parse_args()

    src = pathlib.Path(args.warnings_json).resolve()
    out = pathlib.Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    candidates = parse_stream(src)
    if not candidates:
        print("no candidates in warnings.json", file=sys.stderr)
        return 3

    confirms = []
    failures = 0
    for index, candidate in enumerate(candidates, 1):
        run_dir = out / f"path-verify-{index:02d}"
        if run_dir.exists():
            import shutil
            shutil.rmtree(run_dir)
        run_dir.mkdir()
        (run_dir / "warning.json").write_text(candidate["raw_json"] + "\n", encoding="utf-8")

        bc_line = candidate["bc_line"].strip()
        if bc_line.endswith(":"):
            bc_line = bc_line[:-1]
        bc_paths = [x for x in bc_line.split(":") if x]
        link_argv = [args.llvm_link, "-o", "built-in.bc"] + bc_paths
        (run_dir / "llvm-link.command").write_text(shlex.join(link_argv) + "\n", encoding="utf-8")
        with (run_dir / "llvm-link.log").open("w", encoding="utf-8") as log:
            link = subprocess.run(link_argv, cwd=run_dir, stdout=log, stderr=subprocess.STDOUT)
        if link.returncode != 0:
            failures += 1
            print(f"candidate {index}: llvm-link failed rc={link.returncode}", file=sys.stderr)
            continue

        klee_argv = [args.klee, f"-json={candidate['raw_json']}", "./built-in.bc"]
        (run_dir / "klee.command").write_text(shlex.join(klee_argv) + "\n", encoding="utf-8")
        with (run_dir / "klee.log").open("w", encoding="utf-8") as log:
            try:
                proc = subprocess.run(
                    klee_argv, cwd=run_dir, stdout=log, stderr=subprocess.STDOUT,
                    timeout=args.timeout, start_new_session=True,
                )
                rc = proc.returncode
            except subprocess.TimeoutExpired:
                rc = 124
        (run_dir / "klee.exit_code").write_text(str(rc) + "\n", encoding="utf-8")
        if rc != 0:
            failures += 1
        confirm = run_dir / "confirm_result.json"
        if confirm.is_file():
            confirms.append(confirm.read_text(encoding="utf-8", errors="replace").rstrip("\n"))
        print(f"candidate {index}: klee rc={rc} confirm={confirm.is_file()}", flush=True)

    if confirms:
        (out / "confirm_result.json").write_text("\n".join(confirms) + "\n", encoding="utf-8")
    print(f"candidates={len(candidates)} confirmed_files={len(confirms)} failures={failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
