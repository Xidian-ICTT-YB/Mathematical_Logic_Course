#!/usr/bin/env python3
"""Collect a compact, traceable evidence set from one acceptance run.

The full run tree stays in the project; this script copies the files that
support the A-D/H1-H2 conclusions and the PPT, then writes a checksum manifest
and a human-readable results summary.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import shutil
import sys


def load(path: pathlib.Path):
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=str(pathlib.Path(__file__).resolve().parent.parent))
    ap.add_argument("--out", default="")
    ap.add_argument("--run-id", default="")
    ap.add_argument("--history-run", default="")
    args = ap.parse_args()

    root = pathlib.Path(args.project).resolve()
    out = pathlib.Path(args.out).resolve() if args.out else root / "verification"
    out.mkdir(parents=True, exist_ok=True)
    ev = out / "evidence"
    ev.mkdir(parents=True, exist_ok=True)

    summary = load(root / "artifacts/summary.json")
    acceptance = load(root / "artifacts/ACCEPTANCE.json")
    validation = load(root / "artifacts/VALIDATION.json")
    metadata = load(root / "artifacts/RUN_METADATA.json")
    host_env = load(root / "artifacts/reproduce-all-host-environment.json") or \
        load(root / "artifacts/host-environment.json")
    run_id = args.run_id or (metadata or {}).get("run_id") or ""
    hist_run = args.history_run or ""
    if not hist_run:
        last = root / "history/ahci_xgene/runs/LAST_RUN.txt"
        if last.is_file():
            hist_run = last.read_text(encoding="utf-8").strip()

    copied: list[tuple[str, pathlib.Path]] = []

    def copy(rel: str, required: bool = False) -> None:
        src = root / rel
        if not src.is_file():
            if required:
                raise SystemExit(f"missing required evidence file: {rel}")
            return
        dst = ev / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append((rel, dst))

    # Run-level records.
    for rel in (
        "artifacts/summary.json", "artifacts/SUMMARY.md",
        "artifacts/VALIDATION.json", "artifacts/ACCEPTANCE.json",
        "artifacts/RUN_METADATA.json", "artifacts/BUILD_METADATA.json",
        "artifacts/host-environment.json",
        "artifacts/reproduce-all-host-environment.json",
        "logs/stage-exit-codes.txt", "logs/stage-timings.tsv",
        "logs/source-status.txt", "logs/binaries.sha256",
        "logs/klee-binaries.sha256", "logs/toolchain-versions.txt",
        "logs/image-id.txt", "logs/image-platform.txt",
        "requirements-linux.lock", "requirements-linux.txt",
    ):
        copy(rel)
    # Full host-entry transcripts for this run (stage output is also preserved
    # in the project's own logs/ directory).
    for log in sorted((root / "logs").glob("reproduce-*.log")):
        copy(str(log.relative_to(root)))
    for log in sorted((root / "logs").glob("run-history-*.log")):
        copy(str(log.relative_to(root)))

    # A-D case-level and candidate-level evidence.
    for case_dir in sorted((root / "artifacts").glob("[A-D]_*")):
        base = case_dir.name
        for name in ("summary.json", "README.txt", "backlog.c", "backlog.bc",
                     "warnings.json", "warnings.parsed.json", "warnings.absent.txt",
                     "confirm_result.json", "confirm_result.export-build.json",
                     "confirm_result.absent.txt"):
            copy(f"artifacts/{base}/{name}")
        for cand in sorted((case_dir / "candidates").glob("candidate-*")):
            cbase = f"artifacts/{base}/candidates/{cand.name}"
            for name in ("result.json", "warning-context.json", "warning.json",
                         "command.json", "command.sh"):
                copy(f"{cbase}/{name}")
            for sub in ("klee-original", "klee-smt-export"):
                for name in ("confirm_result.json", "query.smt2",
                             "z3-replay.json", "z3-replay.log", "command.json",
                             "command.sh", "klee.log"):
                    copy(f"{cbase}/{sub}/{name}")

    # Historical evidence.
    if hist_run:
        hbase = f"history/ahci_xgene/runs/{hist_run}"
        for name in ("summary.json", "README.md", "host-environment.json"):
            copy(f"{hbase}/{name}")
        for version in ("h1", "h2"):
            for name in ("summary.json", "confirm_result.json",
                         "confirm_result.absent.txt", "warnings.json",
                         "warnings.parsed.json", "compile.log", "bbtag.log",
                         "stage1.log"):
                copy(f"{hbase}/{version}/{name}")
            for cand in sorted((root / hbase / version / "candidates").glob("candidate-*")):
                cbase = f"{hbase}/{version}/candidates/{cand.name}"
                for name in ("result.json", "raw-warning.json", "klee-warning.json",
                             "bridge.json", "klee-bridge.diff"):
                    copy(f"{cbase}/{name}")
                for sub in ("klee-original", "klee-smt-export"):
                    for name in ("confirm_result.json", "query.smt2",
                                 "z3-replay.json", "z3-replay.log", "klee.log"):
                        copy(f"{cbase}/{sub}/{name}")

    # Historical provenance and harness mapping (small text/JSON only).
    for rel in ("history/ahci_xgene/HARNESS_MAPPING.md",
                "history/ahci_xgene/KLEE_BRIDGE.md",
                "history/ahci_xgene/provenance/commit.json",
                "history/ahci_xgene/provenance/SOURCE_LOCK.json",
                "history/ahci_xgene/provenance/official-fix.patch"):
        copy(rel)

    # Demo verification, if this run included the stepwise demo.
    for rel in ("demo/verification.json", "demo/container.json"):
        copy(rel)

    # Write environment and result summaries.
    combined_env = {
        "collected_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "project": str(root),
        "run_id": run_id,
        "history_run": hist_run,
        "host_environment": host_env,
        "container_run_metadata": metadata,
        "validation": validation,
        "acceptance_ok": (acceptance or {}).get("ok"),
    }
    (out / "ENVIRONMENT.json").write_text(
        json.dumps(combined_env, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = ["# Acceptance evidence", "",
             f"- Project: `{root}`",
             f"- A-D run ID: `{run_id or 'unknown'}`",
             f"- History run ID: `{hist_run or 'unknown'}`",
             f"- Structure validation: `{'PASS' if (validation or {}).get('ok') else 'FAIL'}`",
             f"- Expected-result check: `{'PASS' if (acceptance or {}).get('ok') else 'FAIL'}`",
             f"- Collected at (UTC): {combined_env['collected_at_utc']}", "",
             "## A-D summary", ""]
    if summary:
        for c in summary.get("cases", []):
            lines.append(
                f"- **{c['case']}** `{c['title']}`: candidates={c['candidate_count']} "
                f"({c['candidate_lines']}), confirmed original="
                f"{c['confirmed_lines_default_reporting']}, export="
                f"{c['confirmed_lines_smt_export_build']}; note: {c['config_note']}")
    lines += ["", "## Historical summary", ""]
    hsum = load(root / f"history/ahci_xgene/runs/{hist_run}/summary.json") if hist_run else None
    if hsum:
        lines.append(f"- Upstream fix commit: `{hsum.get('upstream_commit')}` "
                     f"(parent `{hsum.get('parent_commit')}`)")
        for h in hsum.get("histories", []):
            lines.append(
                f"- **{h['version']}**: candidates={h['candidate_count']}, "
                f"target objects={h['target_warning_count']}, "
                f"confirmed target objects={h['target_confirmed_count']}, "
                f"confirmed use points={h['target_confirmed_lines']}")
    lines += ["", "## Key files", "",
              "- `evidence/artifacts/ACCEPTANCE.json` — all expected-result checks",
              "- `evidence/artifacts/A_original_default_dedup/candidates/candidate-01-line-25/"
              "klee-smt-export/query.smt2` — real exported query for A line 25",
              "- `evidence/artifacts/A_original_default_dedup/candidates/candidate-01-line-25/"
              "klee-smt-export/z3-replay.json` — Z3 replay result/model",
              "- `evidence/history/ahci_xgene/runs/.../h1/.../query.smt2` — H1 queries",
              "- `evidence/ENVIRONMENT.json` — host, image, toolchain, exit codes",
              "- `SHA256SUMS` — checksums of every collected file", ""]
    (out / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")

    command_lines = [
        "# Commands used for this acceptance run", "",
        "```bash",
        "cd <extracted-project>",
        f"UBITECT_IMAGE={os.environ.get('UBITECT_IMAGE', 'ubitect-repro-delivery:base')} \\",
        f"UBITECT_RUN_ID={run_id or '<RUN-ID>'} \\",
        f"UBITECT_HISTORY_RUN_ID={hist_run or '<HIST-ID>'} \\",
        "./REPRODUCE_ALL.sh",
        "```", "",
        "The script's own stage log is preserved in the project at `logs/` and",
        "the selected stage records are copied into `evidence/logs/`.", "",
        "Per-stage exit codes are in `evidence/logs/stage-exit-codes.txt`;",
        "the image ID and platform are in `evidence/logs/image-id.txt` and",
        "`evidence/logs/image-platform.txt`.", ""]
    (out / "COMMANDS.md").write_text("\n".join(command_lines), encoding="utf-8")

    manifest = []
    for _, dst in sorted(copied, key=lambda x: str(x[1])):
        rel = dst.relative_to(out)
        manifest.append(f"{sha256(dst)}  {rel}")
    for name in ("ENVIRONMENT.json", "RESULTS.md", "COMMANDS.md"):
        p = out / name
        manifest.append(f"{sha256(p)}  {name}")
    (out / "SHA256SUMS").write_text("\n".join(manifest) + "\n", encoding="utf-8")

    print(f"verification: {out}")
    print(f"files: {len(manifest)}")
    print(f"RESULTS: {out / 'RESULTS.md'}")
    print(f"SHA256SUMS: {out / 'SHA256SUMS'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
