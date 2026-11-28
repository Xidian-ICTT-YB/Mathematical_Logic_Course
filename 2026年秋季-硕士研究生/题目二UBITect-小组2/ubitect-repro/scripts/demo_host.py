#!/usr/bin/env python3
"""Host-side demo checks, resource display, and final summary.

The summary deliberately separates four things that must not be conflated:
this DEMO run, the archived formal history run, the earlier metrics run, and
a one-shot sample of the current Docker environment.
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
from typing import Optional

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCKER = shutil.which("docker") or "/Applications/Docker.app/Contents/Resources/bin/docker"
STATE = ROOT / "demo/state.json"
RUNS = ROOT / "demo/runs"
HIST_RUNS = ROOT / "history/ahci_xgene/runs"
METRICS = ROOT / "reference/metrics/summary.json"
CONTAINER = os.environ.get("UBITECT_CONTAINER", "ubitect-repro-delivery-demo")
IMAGE = os.environ.get("UBITECT_IMAGE", "ubitect-repro-delivery:base")


def run(argv: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(argv, text=True, capture_output=True)


def inspect(fmt: str, ref: str = CONTAINER) -> str:
    p = run([DOCKER, "inspect", ref, "--format", fmt])
    return p.stdout.strip() if p.returncode == 0 else ""


def image_inspect(fmt: str) -> str:
    p = run([DOCKER, "image", "inspect", IMAGE, "--format", fmt])
    return p.stdout.strip() if p.returncode == 0 else ""


def container_exec(script: str) -> subprocess.CompletedProcess:
    return run([DOCKER, "exec", "-w", "/work", CONTAINER, "bash", "-lc", script])


def docker_stats() -> str:
    p = run([DOCKER, "stats", "--no-stream", "--format",
             "{{.Name}} {{.MemUsage}} {{.CPUPerc}}", CONTAINER])
    return p.stdout.strip() if p.returncode == 0 else ""


def load(path: pathlib.Path):
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def ensure_migrated() -> None:
    """Apply the one-time v3 -> tutorial state migration on the host."""
    path = ROOT / "scripts/demo_state_migration.py"
    if not path.is_file():
        return
    import importlib.util
    spec = importlib.util.spec_from_file_location("demo_state_migration", path)
    if spec is None or spec.loader is None:
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.migrate(ROOT, quiet=True)


def docker_settings() -> dict:
    sock = pathlib.Path.home() / "Library/Containers/com.docker.docker/Data/backend.sock"
    p = run(["curl", "-sS", "--unix-socket", str(sock),
             "http://localhost/app/settings/gui"])
    if p.returncode != 0:
        return {"error": p.stderr.strip()}
    try:
        s = json.loads(p.stdout)["settings"]
        return {k: s.get(k) for k in (
            "vm.resources.dataFolder", "vm.resources.cpus",
            "vm.resources.memoryMiB", "vm.resources.diskSizeMiB")}
    except Exception as exc:
        return {"error": str(exc)}


def check() -> int:
    print("[check]")
    print("host:", run(["uname", "-m"]).stdout.strip(),
          run(["sw_vers", "-productVersion"]).stdout.strip())
    dv = run([DOCKER, "version", "--format", "{{.Server.Version}} {{.Server.Arch}}"])
    print("docker:", dv.stdout.strip() if dv.returncode == 0 else "UNAVAILABLE")
    print("vm_settings:", json.dumps(docker_settings(), sort_keys=True))
    print("container_name:", CONTAINER)
    running = inspect("{{.State.Running}}") == "true"
    print("container_running:", str(running).lower())
    print("container_id:", inspect("{{.Id}}") or "MISSING")
    print("container_image:", inspect("{{.Config.Image}}") or "MISSING")
    print("container_image_id:", inspect("{{.Image}}") or "MISSING")
    print("container_platform:", f"{image_inspect('{{.Os}}')}/{image_inspect('{{.Architecture}}')}")
    print("container_workdir:", inspect("{{.Config.WorkingDir}}") or "MISSING")
    mount = inspect('{{range .Mounts}}{{if eq .Destination "/work"}}{{.Source}}{{end}}{{end}}')
    print("container_mount:", f"{mount or 'MISSING'} -> /work")
    script = ("set -euo pipefail; source /work/scripts/container_env.sh; "
              "echo \"target_os: $(uname -s) $(uname -m)\"; "
              "echo \"kernel: $(uname -r)\"; "
              "echo \"os_release: $(grep -E '^PRETTY_NAME=' /etc/os-release | cut -d= -f2- | tr -d '\\\"')\"; "
              "echo \"workdir: $(pwd)\"; "
              "echo \"work_mount: $(test -d /work && echo present || echo missing)\"; "
              "echo \"clang: $(/opt/llvm7/bin/clang --version | head -n1)\"; "
              "echo \"z3: $(\"$PYTHON\" -c 'import z3; print(z3.get_version_string())')\"; "
              "echo \"klee: $(/work/build/klee-original/bin/klee --version 2>&1 | head -n1)\"; "
              "echo \"ubitect: $(/work/build/ubitect-original/ubitect --version 2>&1 | head -n2 | tail -n1 | sed 's/^ *//')\"")
    x = container_exec(script)
    if x.returncode == 0:
        for line in x.stdout.strip().splitlines():
            print(line)
    else:
        print("container_exec: FAILED")
        if x.stderr.strip():
            print(x.stderr.strip())
    img = run([DOCKER, "image", "inspect", IMAGE, "--format", "{{.Id}}"])
    print("image:", img.stdout.strip() if img.returncode == 0 else "MISSING")
    v = ROOT / "artifacts/VALIDATION.json"
    d = load(v)
    if d is None:
        print("A-D validation: MISSING", v)
    else:
        print("A-D validation:", "PASS" if d.get("ok") else "FAIL",
              f"({v.relative_to(ROOT)})")
    ok = (dv.returncode == 0 and running and x.returncode == 0
          and img.returncode == 0 and d is not None and d.get("ok"))
    return 0 if ok else 1


def metrics_scope(m: dict) -> str:
    csv = ROOT / "reference/metrics/candidate_timings.csv"
    return ("stage repeats for klee_history_h1/h2 use candidate-01-line-825 / "
            "candidate-01-line-824; the archived functional table covers both "
            f"target objects. Per-candidate timings: {csv.relative_to(ROOT)}")


def metrics_path() -> pathlib.Path:
    if METRICS.is_file():
        return METRICS
    return ROOT / "metrics/summary.json"


def resources() -> int:
    print("[resources]")
    mp = metrics_path()
    m = load(mp)
    if m is None:
        print(f"MISSING: {mp.relative_to(ROOT)} (no archived measurement)")
        return 1
    print("source:", mp.relative_to(ROOT))
    print(f"measurement_id: {m.get('run_id')}")
    print("status: ARCHIVED MEASUREMENT (not a live measurement of this demo)")
    functional = m.get("functional", [])
    if functional:
        print("functional scope (archived):")
        for x in functional:
            print(f"  {x['case']}: objects={x['warning_objects']} "
                  f"use_points={x['independent_use_points']} "
                  f"confirmed_objects={x['target_confirmed_objects']} "
                  f"confirmed_use_points={x['target_confirmed_use_points']} "
                  f"solver={x['solver_status']}")
    r = m.get("resources", {})
    print("stages (n=3 per stage; wall median/range, per-process peak RSS):")
    for stage, x in r.get("stage_summary", {}).items():
        w = x["wall_s"]
        rss = x["max_rss_kb"]
        print(f"  {stage:28s} n={x['n']} "
              f"median={w['median']:.4f}s range={w['min']:.4f}..{w['max']:.4f}s "
              f"rss_median={rss['median']}KiB exit={x['exit_codes']} "
              f"timeouts={x['timeouts']}")
    print("scope:", metrics_scope(m))
    cg = r.get("cgroup", {})
    print("cgroup_start:", cg.get("start"),
          "(container lifetime/current, not per-stage peak)")
    print("cgroup_end:", cg.get("end"),
          "(container lifetime/current, not per-stage peak)")
    print("vm_config:", r.get("vm_config"),
          "(Docker Desktop quota, not measured usage)")
    print("cold_build:", r.get("build_first_time"),
          "(unavailable is not zero)")
    print("measurement_note:", r.get("measurement_note"))
    print("container_now:", f"{CONTAINER} id={inspect('{{.Id}}') or 'MISSING'} "
          f"state={inspect('{{.State.Status}}') or 'MISSING'}")
    print("docker_stats_now:", docker_stats() or "unavailable",
          "(one-shot current sample, not part of the archived measurement)")
    return 0


def find_archive() -> Optional[pathlib.Path]:
    candidates = []
    for p in HIST_RUNS.glob("*/summary.json"):
        d = load(p)
        if d and d.get("target_h1_confirmed") and not d.get("target_h2_confirmed"):
            candidates.append(p)
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


def demo_section() -> tuple[list[str], bool]:
    lines = ["== 本次 DEMO 运行（demo/state.json）=="]
    s = load(STATE)
    if not s:
        lines.append("MISSING: no demo/state.json; no current demo run")
        return lines, False
    ok = True
    tutorial = s.get("tutorial_run")
    if tutorial:
        lines.append(f"tutorial_run: {tutorial}")
    else:
        lines.append("tutorial_run: MISSING")
    migration = s.get("naming_migration") or {}
    if migration:
        lines.append(f"  naming_migration: v{migration.get('version')} "
                     f"from {migration.get('chosen_from')} -> "
                     f"{migration.get('chosen_run')}; "
                     f"backup {migration.get('backup')}")
    t = RUNS / tutorial if tutorial else None
    compare = load(t / "compare.json") if t else None
    if compare is None:
        lines.append("  INCOMPLETE: tutorial compare.json missing")
        ok = False
    else:
        for x in compare:
            lines.append(f"  {x['case']}: candidates={x['candidates']} "
                         f"confirmed_objects={x['confirmed_objects']} "
                         f"confirmed_use_points={x['confirmed_use_points']}")
        aq = t / "A/candidate-01/klee-smt-export/query.smt2"
        az = load(t / "A/candidate-01/klee-smt-export/z3-replay.json")
        if not aq.is_file() or not az:
            lines.append("  INCOMPLETE: current A query/z3 replay missing")
            ok = False
        else:
            lines.append(f"  A query: {aq.relative_to(ROOT)}")
            lines.append(f"  A z3: {az.get('result')} model={az.get('model')}")

    lines.append(f"history_run: {s.get('history_run')}")
    h = RUNS / s["history_run"] if s.get("history_run") else None
    hc = load(h / "compare.json") if h else None
    if hc is None:
        lines.append("  INCOMPLETE: history compare.json missing")
        ok = False
    else:
        for v in ("h1", "h2"):
            x = hc[v]
            lines.append(f"  {v}: {x['confirmed_objects']}/{x['target_objects']} "
                         f"target objects confirmed; use_points="
                         f"{x['confirmed_use_points']}; queries={x['queries']}; "
                         f"z3={x['z3_results']}")
        lines.append(f"  scope: {hc.get('scope')}")
        lines.append("  boundary: failure-only function model; input_0=0 is the "
                     "entry selector (H1), not attacker input; H2 has no target query")
    return lines, ok


def archive_section() -> tuple[list[str], bool]:
    lines = ["== 历史归档结果（正式实验材料，不是本次 DEMO）=="]
    p = find_archive()
    if p is None:
        lines.append("MISSING: no passing archived HIST-* summary")
        return lines, False
    d = load(p)
    lines.append(f"archive_run: {p.parent.name}")
    lines.append(f"source: {p.relative_to(ROOT)}")
    for h in d.get("histories", []):
        lines.append(f"  {h['version']}: candidates={h['candidate_count']} "
                     f"target={h['target_warning_count']} "
                     f"confirmed_objects={h['target_confirmed_count']} "
                     f"confirmed_use_points={h['target_confirmed_lines']}")
    lines.append(f"  note: {d.get('note')}")
    return lines, True


def metrics_section() -> tuple[list[str], bool]:
    lines = ["== 先前测量数据（存档，不是本次实时测量）=="]
    mp = metrics_path()
    m = load(mp)
    if m is None:
        lines.append(f"MISSING: {mp.relative_to(ROOT)}")
        return lines, False
    r = m.get("resources", {})
    stages = r.get("stage_summary", {})
    ok = bool(m.get("run_id")) and bool(stages)
    bad = []
    for stage, x in stages.items():
        if x.get("n") != 3 or x.get("timeouts") != 0 or any(
                rc != 0 for rc in x.get("exit_codes", [])):
            bad.append(stage)
    lines.append(f"measurement_id: {m.get('run_id')}")
    lines.append(f"stages: {len(stages)}; n=3 per stage; "
                 f"all_rc0_timeouts0={not bad}")
    if bad:
        lines.append(f"  ANOMALY stages: {bad}")
        ok = False
    lines.append("  " + metrics_scope(m))
    lines.append("  caveat: RSS is per-process GNU time peak; cgroup is "
                 "container lifetime/current; VM values are configuration, not usage")
    return lines, ok


def env_section() -> list[str]:
    lines = ["== 当前环境采样（本次命令，不是性能测量）=="]
    un = run(["uname", "-m"])
    dv = run([DOCKER, "version", "--format", "{{.Server.Version}} {{.Server.Arch}}"])
    lines.append(f"host_arch: {un.stdout.strip() or 'unavailable'}")
    lines.append(f"docker: {dv.stdout.strip() if dv.returncode == 0 else 'unavailable'}")
    lines.append(f"container: {CONTAINER} id={inspect('{{.Id}}') or 'MISSING'} "
                 f"state={inspect('{{.State.Status}}') or 'MISSING'}")
    mount = inspect('{{range .Mounts}}{{if eq .Destination "/work"}}{{.Source}}{{end}}{{end}}')
    lines.append(f"container_mount: {mount or 'MISSING'} -> /work")
    lines.append(f"vm_settings_now: {json.dumps(docker_settings(), sort_keys=True)}")
    lines.append(f"docker_stats_now: {docker_stats() or 'unavailable'}")
    return lines


def summary() -> int:
    print("[summary]")
    demo, demo_ok = demo_section()
    archive, archive_ok = archive_section()
    metrics, metrics_ok = metrics_section()
    env = env_section()
    for lines in (demo, archive, metrics, env):
        print("\n".join(lines))
        print()
    ap = ROOT / "artifacts/SUMMARY.md"
    print("== 历史归档 A–D 摘要（正式材料，不是本次 DEMO）==")
    if ap.is_file():
        print(ap.read_text(encoding="utf-8").rstrip())
    else:
        print(f"MISSING: {ap.relative_to(ROOT)}")
    print()
    ok = demo_ok and archive_ok and metrics_ok and ap.is_file()
    print(f"STATUS: {'COMPLETE' if ok else 'INCOMPLETE OR MISSING EVIDENCE'}")
    return 0 if ok else 1


def main() -> int:
    ensure_migrated()
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    fn = {"check": check, "resources": resources, "summary": summary}.get(cmd)
    if fn is None:
        print("usage: demo_host.py check|resources|summary", file=sys.stderr)
        return 2
    return fn()


if __name__ == "__main__":
    raise SystemExit(main())
