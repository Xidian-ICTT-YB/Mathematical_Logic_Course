#!/usr/bin/env python3
"""Write the in-container run metadata for one A-D pipeline execution."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess


def cmd(argv: list[str]) -> str:
    try:
        return subprocess.check_output(argv, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:  # pragma: no cover - diagnostics only
        return f"unavailable: {type(exc).__name__}: {exc}"


def sha256(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def parse_stages(path: pathlib.Path) -> list[dict]:
    stages = []
    if not path.is_file():
        return stages
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if " rc=" in line:
            name, rc = line.rsplit(" rc=", 1)
            try:
                code = int(rc)
            except ValueError:
                code = None
            stages.append({"stage": name, "exit_code": code})
    return stages


def parse_timings(path: pathlib.Path) -> list[dict]:
    timings = []
    if not path.is_file():
        return timings
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        try:
            timings.append({"stage": parts[0], "exit_code": int(parts[1]),
                            "duration_s": float(parts[2])})
        except ValueError:
            continue
    return timings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--started-at", required=True)
    ap.add_argument("--finished-at", required=True)
    ap.add_argument("--stage-file", required=True)
    ap.add_argument("--timing-file", default="")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    root = pathlib.Path("/work")
    venv = root / ".venv-linux"
    py = venv / "bin/python"
    payload = {
        "run_id": args.run_id,
        "started_utc": args.started_at,
        "finished_utc": args.finished_at,
        "container": {
            "uname": cmd(["uname", "-srm"]),
            "arch": cmd(["uname", "-m"]),
            "os_release": cmd(["bash", "-lc", ". /etc/os-release; echo \"$PRETTY_NAME\""]),
        },
        "toolchain": {
            "uv": cmd(["uv", "--version"]),
            "python": cmd([str(py), "--version"]) if py.is_file() else "missing",
            "cmake": cmd([str(venv / "bin/cmake"), "--version"]).splitlines()[0]
            if (venv / "bin/cmake").is_file() else "missing",
            "z3": cmd([str(py), "-c", "import z3; print(z3.get_version_string())"])
            if py.is_file() else "missing",
            "llvm": cmd(["/opt/llvm7/bin/llvm-config", "--version"]),
            "llvm_has_rtti": cmd(["/opt/llvm7/bin/llvm-config", "--has-rtti"]),
            "clang": cmd(["/opt/llvm7/bin/clang", "--version"]).splitlines()[0],
        },
        "binaries_sha256": {
            "bbtag": sha256(root / "build/bbtag/bbTaglib.so"),
            "ubitect_original": sha256(root / "build/ubitect-original/ubitect"),
            "ubitect_nodedup": sha256(root / "build/ubitect-nodedup/ubitect"),
            "klee_original": sha256(root / "build/klee-original/bin/klee.noexport"),
            "klee_export": sha256(root / "build/klee-original/bin/klee"),
        },
        "stages": parse_stages(pathlib.Path(args.stage_file)),
        "stage_timings": parse_timings(pathlib.Path(args.timing_file))
        if args.timing_file else [],
        "pipeline_exit_code": max(
            (s["exit_code"] for s in parse_stages(pathlib.Path(args.stage_file))
             if s["exit_code"] is not None),
            default=0,
        ),
    }
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(f"metadata: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
