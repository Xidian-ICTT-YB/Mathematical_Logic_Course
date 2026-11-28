#!/usr/bin/env python3
"""Build and verify the v3 review package.

The package is a curated review copy, not a runnable image.  Only explicit
paths are copied; build trees, virtual environments, caches, Docker data,
credentials and old run directories are never traversed.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import pathlib
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
KFC = ROOT.parent
NAME = "UBITect_REVIEW_PACKAGE_v3"
ZIP_PATH = ROOT / f"{NAME}.zip"
STAMP = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())

EXAMPLE_RUN = "demo/runs/DEMO-20261104T065000Z/example"
HISTORY_RUN = "demo/runs/HIST-20261104T065006Z/history"
CANONICAL_HISTORY = "history/ahci_xgene/runs/HIST-20261027T133810Z"

ROOT_FILES = [
    "PACKAGE_README.md",
    "README.md",
    "STATE.md",
    "DELIVERABLES.md",
    "ENVIRONMENT.md",
    "HISTORICAL_CASE_REPORT.md",
    "V3_CHANGELOG.md",
    "DEMO.sh",
    "Dockerfile",
    "requirements-host.txt",
    "requirements-host.lock",
    "requirements-linux.txt",
    "requirements-linux.lock",
]

DOC_FILES = [
    "docs/原理与数理逻辑讲解.md",
    "docs/原理与数理逻辑讲解.pdf",
    "docs/录屏操作手册.md",
    "docs/录屏操作手册.pdf",
    "docs/完整演示逐字讲稿.md",
    "docs/完整演示逐字讲稿.pdf",
]

PRESENTATION_FILES = [
    "presentation/PPT逐页内容方案.md",
    "presentation/结果与表述核对.md",
    "presentation/项目理解导读.md",
    "presentation/演示与求解器关系核对.md",
]

DEMO_FILES = [
    "demo/state.json",
    "demo/container.json",
    "demo/verification-20261104T064956Z.json",
    "demo/negative-20261104T064939Z.json",
]

HISTORY_TOP = [
    "history/ahci_xgene/HARNESS_MAPPING.md",
    "history/ahci_xgene/KLEE_BRIDGE.md",
]

METRIC_FILES = [
    "metrics/METRICS_DEFINITIONS.md",
    "metrics/results.csv",
    "metrics/resources.csv",
    "metrics/candidate_timings.csv",
    "metrics/summary.json",
    "metrics/vm_and_build_sample.json",
]

TREE_DIRS = [
    "scripts",
    "ppt_assets",
    "artifacts",
    "patches",
    f"{EXAMPLE_RUN}",
    f"{HISTORY_RUN}",
    CANONICAL_HISTORY,
    "history/ahci_xgene/harness",
    "history/ahci_xgene/source",
    "history/ahci_xgene/provenance",
    "metrics/raw/MET-20261027T133810Z",
    "logs/demo-verification-20261104T064956Z",
    "logs/demo-negative-20261104T064939Z",
]

KEY_REFS = [
    "PACKAGE_README.md",
    "V3_CHANGELOG.md",
    "DEMO.sh",
    "scripts/container_env.sh",
    "scripts/container_demo_step.sh",
    "scripts/container_system_check.sh",
    "scripts/demo_step.py",
    "scripts/demo_host.py",
    "scripts/verify_demo.py",
    "scripts/verify_negative.py",
    "scripts/replay_z3.py",
    "scripts/generate_pdf.py",
    "docs/原理与数理逻辑讲解.pdf",
    "docs/录屏操作手册.pdf",
    "docs/完整演示逐字讲稿.pdf",
    "presentation/PPT逐页内容方案.md",
    "presentation/结果与表述核对.md",
    "ppt_assets/INDEX.md",
    "ppt_assets/figures/runtime_topology.svg",
    "ppt_assets/figures/runtime_topology.png",
    "ppt_assets/figures/runtime_topology.pdf",
    "demo/verification-20261104T064956Z.json",
    "demo/negative-20261104T064939Z.json",
    f"{EXAMPLE_RUN}/A/candidate-01/klee-smt-export/query.smt2",
    f"{EXAMPLE_RUN}/A/candidate-01/klee-smt-export/z3-replay.json",
    f"{EXAMPLE_RUN}/A/warnings.json",
    f"{EXAMPLE_RUN}/variants/D/warnings.json",
    "artifacts/D_short_circuit_control/confirm_result.absent.txt",
    f"{HISTORY_RUN}/h1/candidates/candidate-01/klee-smt-export/query.smt2",
    f"{HISTORY_RUN}/h1/candidates/candidate-01/klee-smt-export/z3-replay.json",
    f"{HISTORY_RUN}/h1/candidates/candidate-01/bridge.json",
    f"{HISTORY_RUN}/h2/confirm_result.absent.txt",
    "artifacts/analysis/real-exports/A_candidate-01-line-25.smt2",
    "artifacts/analysis/real-exports/B_candidate-02-line-26.smt2",
    f"{CANONICAL_HISTORY}/h1/candidates/candidate-01-line-825/klee-smt-export/query.smt2",
    f"{CANONICAL_HISTORY}/h1/candidates/candidate-01-line-825/bridge.json",
    f"{CANONICAL_HISTORY}/h2/confirm_result.absent.txt",
    "patches/0003-smt-export-before-check.patch",
    "metrics/METRICS_DEFINITIONS.md",
    "metrics/results.csv",
    "metrics/resources.csv",
]

IGNORE = shutil.ignore_patterns(
    "__pycache__", "*.pyc", ".DS_Store", "*.swp", "*.tmp", ".git", ".git/*"
)

FORBIDDEN_DIRS = {
    ".git", "__pycache__", ".venv-host", ".venv-linux", ".uv-cache-linux",
    ".uv-python-linux", "build", "downloads", "scratch", "config", ".home-linux",
    ".uv-bin-linux",
}
FORBIDDEN_SUFFIXES = {".raw", ".img", ".qcow2", ".vmdk", ".vdi"}


def copy_file(rel: str, stage: pathlib.Path) -> None:
    src = ROOT / rel
    dst = stage / rel
    if not src.is_file():
        raise SystemExit(f"missing required file: {rel}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree(rel: str, stage: pathlib.Path) -> None:
    src = ROOT / rel
    dst = stage / rel
    if not src.is_dir():
        raise SystemExit(f"missing required directory: {rel}")
    shutil.copytree(src, dst, ignore=IGNORE, symlinks=True)


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build(stage: pathlib.Path) -> list[str]:
    for rel in ROOT_FILES:
        copy_file(rel, stage)
    for rel in DOC_FILES + PRESENTATION_FILES + DEMO_FILES + HISTORY_TOP + METRIC_FILES:
        copy_file(rel, stage)
    for rel in TREE_DIRS:
        copy_tree(rel, stage)

    files = sorted(
        p.relative_to(stage).as_posix()
        for p in stage.rglob("*")
        if p.is_file() and p.name not in ("FILELIST.txt", "SHA256SUMS")
    )
    lines = []
    for rel in files:
        lines.append(f"{rel}\t{(stage / rel).stat().st_size}\n")
    (stage / "FILELIST.txt").write_text(
        "# v3 package payload; excludes FILELIST.txt and SHA256SUMS\n" + "".join(lines),
        encoding="utf-8",
    )

    checksum_files = sorted(
        p.relative_to(stage).as_posix()
        for p in stage.rglob("*")
        if p.is_file() and p.name != "SHA256SUMS"
    )
    with (stage / "SHA256SUMS").open("w", encoding="utf-8") as f:
        for rel in checksum_files:
            f.write(f"{sha256(stage / rel)}  {rel}\n")
    return checksum_files


def zip_stage(stage: pathlib.Path) -> None:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(stage.rglob("*")):
            if not p.is_file():
                continue
            arc = pathlib.PurePosixPath(NAME) / p.relative_to(stage).as_posix()
            zi = zipfile.ZipInfo.from_file(p, arc.as_posix())
            zi.compress_type = zipfile.ZIP_DEFLATED
            mode = stat.S_IMODE(p.stat().st_mode)
            if p.suffix == ".sh" or p.name == "DEMO.sh":
                mode |= 0o111
            zi.external_attr = mode << 16
            zf.writestr(zi, p.read_bytes())


def verify() -> tuple[bool, list[str]]:
    report: list[str] = []
    ok = True
    with tempfile.TemporaryDirectory(prefix="ubitect-v3-extract-", dir=KFC) as td:
        extract = pathlib.Path(td)
        with zipfile.ZipFile(ZIP_PATH) as zf:
            names = zf.namelist()
            bad_names = [
                n for n in names
                if n.startswith("/") or ".." in pathlib.PurePosixPath(n).parts
            ]
            if bad_names:
                ok = False
                report.append(f"FAIL unsafe zip paths: {bad_names[:5]}")
            zf.extractall(extract)
        pkg = extract / NAME
        report.append(f"extracted: {pkg}")
        report.append(f"zip entries: {len(names)}")

        p = subprocess.run(
            ["shasum", "-a", "256", "-c", "SHA256SUMS"],
            cwd=pkg, text=True, capture_output=True,
        )
        report.append(f"shasum rc: {p.returncode}")
        if p.returncode != 0:
            ok = False
            report.append(p.stdout[-2000:])
            report.append(p.stderr[-1000:])

        listed = []
        for line in (pkg / "FILELIST.txt").read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#"):
                continue
            rel, size = line.split("\t", 1)
            listed.append((rel, int(size)))
        actual = sorted(
            q.relative_to(pkg).as_posix()
            for q in pkg.rglob("*")
            if q.is_file() and q.name not in ("FILELIST.txt", "SHA256SUMS")
        )
        if sorted(r for r, _ in listed) != actual:
            ok = False
            report.append("FAIL FILELIST does not match extracted payload")
        else:
            report.append(f"FILELIST payload files: {len(listed)}")

        missing = [rel for rel in KEY_REFS if not (pkg / rel).is_file()]
        if missing:
            ok = False
            report.append(f"FAIL missing key references: {missing}")
        else:
            report.append(f"key references present: {len(KEY_REFS)}")

        bad = []
        for rel in actual:
            parts = pathlib.PurePosixPath(rel).parts
            if any(part in FORBIDDEN_DIRS for part in parts):
                bad.append(rel)
            if pathlib.PurePosixPath(rel).suffix.lower() in FORBIDDEN_SUFFIXES:
                bad.append(rel)
        if bad:
            ok = False
            report.append(f"FAIL forbidden package paths: {bad[:10]}")
        else:
            report.append("forbidden path scan: clean")

        size = ZIP_PATH.stat().st_size
        report.append(f"zip size: {size} bytes ({size / 1024 / 1024:.2f} MiB)")
        if size > 40 * 1024 * 1024:
            report.append("NOTE zip is larger than 40 MiB; inspect before sharing")
    return ok, report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify-only", action="store_true")
    args = ap.parse_args()

    if not args.verify_only:
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="ubitect-v3-stage-", dir=KFC))
        stage = tmp / NAME
        stage.mkdir()
        try:
            files = build(stage)
            zip_stage(stage)
            print(f"staged files: {len(files)}")
            print(f"zip: {ZIP_PATH}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    if not ZIP_PATH.is_file():
        print(f"missing zip: {ZIP_PATH}", file=sys.stderr)
        return 2
    ok, report = verify()
    lines = [
        f"package_verification={STAMP}",
        f"zip={ZIP_PATH}",
        *report,
        f"result={'PASS' if ok else 'FAIL'}",
    ]
    text = "\n".join(lines) + "\n"
    log = ROOT / "logs" / f"package-v3-verify-{STAMP}.txt"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(text, encoding="utf-8")
    print(text)
    print(f"log: {log}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
