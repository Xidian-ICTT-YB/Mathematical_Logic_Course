#!/usr/bin/env python3
"""Record the real host/Docker environment around one run (stdlib only)."""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys


def run(argv: list[str], timeout: int = 30) -> dict:
    exe = shutil.which(argv[0])
    if not exe:
        return {"argv": argv, "available": False, "output": ""}
    try:
        p = subprocess.run(argv, text=True, capture_output=True, timeout=timeout)
        return {
            "argv": argv,
            "available": True,
            "exit_code": p.returncode,
            "output": (p.stdout + p.stderr).strip(),
        }
    except Exception as exc:
        return {"argv": argv, "available": True, "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--image", default="")
    ap.add_argument("--run-id", default="")
    ap.add_argument("--mode", default="")
    ap.add_argument("--started-at", default="")
    ap.add_argument("--finished-at", default="")
    ap.add_argument("--exit-code", type=int, default=None)
    args = ap.parse_args()

    project = pathlib.Path(__file__).resolve().parent.parent
    docker = shutil.which("docker")
    image_info = {}
    if docker and args.image:
        p = subprocess.run(
            [docker, "image", "inspect", args.image, "--format",
             "{{json .}}"], text=True, capture_output=True)
        if p.returncode == 0:
            try:
                raw = json.loads(p.stdout)
                image_info = {
                    "reference": args.image,
                    "id": raw.get("Id"),
                    "created": raw.get("Created"),
                    "os": raw.get("Os"),
                    "architecture": raw.get("Architecture"),
                    "size": raw.get("Size"),
                }
            except json.JSONDecodeError:
                image_info = {"reference": args.image, "inspect_error": "invalid JSON"}
        else:
            image_info = {"reference": args.image, "inspect_error": p.stderr.strip()}

    payload = {
        "run_id": args.run_id,
        "mode": args.mode,
        "started_utc": args.started_at,
        "finished_utc": args.finished_at,
        "exit_code": args.exit_code,
        "project": str(project),
        "host": {
            "uname": run(["uname", "-a"])["output"],
            "machine": run(["uname", "-m"])["output"],
            "sw_vers": run(["sw_vers"]),
            "python3": run(["python3", "--version"]),
            "uv": run(["uv", "--version"]),
            "docker_cli": run(["docker", "--version"]),
            "docker_server": run(["docker", "version", "--format",
                                  "{{.Server.Version}} {{.Server.Arch}}"]),
            "disk": run(["df", "-h", str(project)]),
        },
        "image": image_info,
    }
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(f"host environment: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
