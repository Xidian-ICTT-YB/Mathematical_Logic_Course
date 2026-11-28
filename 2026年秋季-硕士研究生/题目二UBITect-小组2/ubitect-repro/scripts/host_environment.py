#!/usr/bin/env python3
"""Collect macOS/Docker/container metadata for the reproduction record.

Runs under the host-only uv virtualenv.  It deliberately reads only explicit
paths and never opens config/deepseek.env or prints environment variables.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
KFC = ROOT.parent
ART = ROOT / "artifacts"
HOME = pathlib.Path.home()


def run_json(argv: list[str], timeout: int = 60):
    try:
        out = subprocess.check_output(
            argv, text=True, stderr=subprocess.PIPE, timeout=timeout
        ).strip()
        return json.loads(out)
    except Exception as exc:  # record the failure, do not hide it
        return {"error": f"{type(exc).__name__}: {exc}"}


def run_text(argv: list[str], timeout: int = 60):
    try:
        return {
            "ok": True,
            "output": subprocess.check_output(
                argv, text=True, stderr=subprocess.STDOUT, timeout=timeout
            ).strip(),
        }
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def sha256(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def parse_kv(path: pathlib.Path) -> dict:
    if not path.is_file():
        return {}
    result = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            result[k] = v
    return result


def docker_settings() -> dict:
    socket = HOME / "Library/Containers/com.docker.docker/Data/backend.sock"
    try:
        out = subprocess.check_output(
            [
                "curl",
                "-sS",
                "--unix-socket",
                str(socket),
                "http://localhost/app/settings/gui",
            ],
            text=True,
            stderr=subprocess.PIPE,
            timeout=10,
        )
        data = json.loads(out)["settings"]
        keys = [
            "vm.resources.cpus",
            "vm.resources.memoryMiB",
            "vm.resources.swapMiB",
            "vm.resources.diskSizeMiB",
            "vm.resources.dataFolder",
            "vm.rosetta.enabled",
            "vm.hypervisor.mac",
            "fileSharingType.mac",
        ]
        return {
            "ok": True,
            "socket": str(socket),
            "settings": {k: data.get(k) for k in keys},
        }
    except Exception as exc:
        return {"ok": False, "socket": str(socket), "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-exit", type=int, default=None)
    ap.add_argument("--started-at", default="")
    ap.add_argument("--finished-at", default="")
    ap.add_argument("--container-image", default="ubitect-repro:base")
    args = ap.parse_args()

    docker = shutil.which("docker")
    if docker is None:
        docker = "/Applications/Docker.app/Contents/Resources/bin/docker"

    system = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "macos": run_text(["sw_vers"]).get("output"),
        "uname": platform.uname()._asdict(),
        "architecture": platform.machine(),
        "memory_bytes": run_text(["sysctl", "-n", "hw.memsize"]).get("output"),
        "disk": run_text(
            ["df", "-k", str(KFC)]
        ).get("output"),
        "python_host": sys.version,
        "python_host_executable": sys.executable,
        "python_host_arch": platform.machine(),
        "uv": run_text(["uv", "--version"]).get("output"),
        "uv_path": shutil.which("uv"),
        "claude": run_text(["claude", "--version"]).get("output"),
        "claude_path": shutil.which("claude"),
    }

    docker_version = run_json([docker, "version", "--format", "{{json .}}"])
    docker_info_full = run_json([docker, "info", "--format", "{{json .}}"])
    docker_info_keys = [
        "ServerVersion",
        "Architecture",
        "OSType",
        "KernelVersion",
        "NCPU",
        "MemTotal",
        "Driver",
        "DockerRootDir",
        "Name",
    ]
    docker_info = (
        {k: docker_info_full.get(k) for k in docker_info_keys}
        if isinstance(docker_info_full, dict) and "error" not in docker_info_full
        else docker_info_full
    )

    image = run_json(
        [docker, "image", "inspect", args.container_image, "--format", "{{json .}}"]
    )
    ubuntu_image = run_json(
        [docker, "image", "inspect", "ubuntu:24.04", "--format", "{{json .}}"]
    )
    ecr_image = run_json(
        [
            docker,
            "image",
            "inspect",
            "public.ecr.aws/ubuntu/ubuntu:24.04",
            "--format",
            "{{json .}}",
        ]
    )

    docker_app = pathlib.Path("/Applications/Docker.app")
    docker_app_version = None
    if (docker_app / "Contents/Info.plist").is_file():
        p = run_text(
            [
                "/usr/libexec/PlistBuddy",
                "-c",
                "Print :CFBundleShortVersionString",
                str(docker_app / "Contents/Info.plist"),
            ]
        )
        docker_app_version = p.get("output")

    dmg = KFC / "downloads/Docker-4.96.3-arm64.dmg"
    container_versions = parse_kv(ROOT / "logs/toolchain-versions.txt")
    summary = {}
    if (ART / "summary.json").is_file():
        summary = json.loads((ART / "summary.json").read_text(encoding="utf-8"))

    artifact_secret_names = [
        str(p.relative_to(ROOT))
        for p in ART.rglob("*")
        if p.is_file() and ("deepseek" in p.name.lower() or p.name == "deepseek.env")
    ]

    docker_meta = {
        "cli_path": docker,
        "client": docker_version.get("Client") if isinstance(docker_version, dict) else None,
        "server": docker_version.get("Server") if isinstance(docker_version, dict) else None,
        "info": docker_info,
        "desktop_app_path": str(docker_app),
        "desktop_app_version": docker_app_version,
        "desktop_dmg_path": str(dmg) if dmg.is_file() else None,
        "desktop_dmg_sha256": sha256(dmg),
        "vm": docker_settings(),
        "images": {
            "ubitect_repro": image,
            "ubuntu_24_04_local": ubuntu_image,
            "ubuntu_24_04_ecr_source": ecr_image,
        },
    }

    host_record = {
        "system": system,
        "docker": docker_meta,
        "project_root": str(ROOT),
        "kfc_root": str(KFC),
        "separate_python_environments": {
            "host": {
                "path": str(ROOT / ".venv-host/bin/python"),
                "version": run_text([str(ROOT / ".venv-host/bin/python"), "--version"]).get("output"),
                "uv_cache": str(KFC / "cache/uv"),
                "python_install_dir": str(KFC / "tools/python"),
            },
            "container": {
                "path": "/work/.venv-linux/bin/python",
                "version": container_versions.get("python"),
                "uv_cache": "/work/.uv-cache-linux",
                "python_install_dir": "/work/.uv-python-linux",
            },
        },
        "container": {
            "platform": "linux/amd64",
            "versions": container_versions,
        },
        "source": {
            "repository": "https://github.com/seclab-ucr/UBITect",
            "pinned_commit": "fb97a1554f6fc3a5e8b35f680a8bfe2b82a79848",
            "dockerfile_sha256": sha256(ROOT / "Dockerfile"),
            "requirements_linux_sha256": sha256(ROOT / "requirements-linux.txt"),
            "requirements_linux_lock_sha256": sha256(ROOT / "requirements-linux.lock"),
            "patches": {
                p.name: sha256(p) for p in sorted((ROOT / "patches").glob("*.patch"))
            },
        },
        "artifact_summary_present": bool(summary),
        "artifact_paths_contain_secret_filename": artifact_secret_names,
    }

    (ART / "host-environment.json").write_text(
        json.dumps(host_record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    run_record = {
        "started_at": args.started_at,
        "finished_at": args.finished_at,
        "container_exit_code": args.run_exit,
        "host_command": "./REPRODUCE.sh",
        "container_image_requested": args.container_image,
        "container_image_id": image.get("Id") if isinstance(image, dict) else None,
        "container_image_arch": image.get("Architecture") if isinstance(image, dict) else None,
        "container_platform": "linux/amd64",
        "host_python_venv": str(ROOT / ".venv-host/bin/python"),
        "container_python_venv": "/work/.venv-linux/bin/python",
        "summary": str(ART / "summary.json"),
        "validation": str(ART / "VALIDATION.json"),
    }
    (ART / "RUN_METADATA.json").write_text(
        json.dumps(run_record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print("Host metadata written to artifacts/host-environment.json")
    print("Run metadata written to artifacts/RUN_METADATA.json")
    print(
        "Docker image:",
        image.get("Id") if isinstance(image, dict) else "unknown",
        "arch=",
        image.get("Architecture") if isinstance(image, dict) else "unknown",
    )
    print("Docker VM settings:", json.dumps(docker_meta["vm"].get("settings", {}), sort_keys=True))
    if artifact_secret_names:
        print("ERROR: secret-named files in artifacts:", artifact_secret_names, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
