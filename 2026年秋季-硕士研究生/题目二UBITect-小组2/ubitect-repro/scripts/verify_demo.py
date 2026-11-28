#!/usr/bin/env python3
"""Execute every documented DEMO.sh subcommand and record real exit status.

The v3 flow starts a persistent project container, reuses it for every
experiment step, stops it at the end, restarts it to prove reuse, and stops it
again.  Each invocation writes a timestamped log directory and a timestamped
JSON record, preserving earlier acceptance records instead of overwriting them.

Passing exit codes alone are not enough: the current run's evidence files must
also agree with the documented tutorial A/B/C/D and history H1/H2 scope, the
container ID must be stable, and the stopped container must leave all results
in place.
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
from typing import Optional

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEMO = ROOT / "DEMO.sh"
STATE = ROOT / "demo/state.json"
CONTAINER_RECORD = ROOT / "demo/container.json"
DEFAULT_RECORD = ROOT / "demo/verification.json"
HIST_RUNS = ROOT / "history/ahci_xgene/runs"
DOCKER = shutil.which("docker") or "/Applications/Docker.app/Contents/Resources/bin/docker"
CONTAINER = os.environ.get("UBITECT_CONTAINER", "ubitect-repro-delivery-demo")
COMMANDS = [
    ["start"],
    ["start"],
    ["status"],
    ["check"],
    ["source", "tutorial"],
    ["compile", "tutorial"],
    ["candidates", "tutorial"],
    ["verify", "tutorial"],
    ["constraints", "tutorial"],
    ["compare", "tutorial"],
    ["source", "history"],
    ["compile", "history"],
    ["candidates", "history"],
    ["verify", "history"],
    ["constraints", "history"],
    ["compare", "history"],
    ["resources"],
    ["summary"],
    ["stop"],
    ["status"],
    ["start"],
    ["status"],
    ["stop"],
]


def load(path: pathlib.Path):
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def docker_inspect(fmt: str) -> str:
    p = subprocess.run([DOCKER, "inspect", CONTAINER, "--format", fmt],
                       text=True, capture_output=True)
    return p.stdout.strip() if p.returncode == 0 else ""


def unique(path: pathlib.Path) -> pathlib.Path:
    if not path.exists():
        return path
    n = 2
    while True:
        candidate = path.with_name(f"{path.stem}-{n}{path.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def archive_previous() -> Optional[str]:
    """Keep the previous canonical record as a timestamped file."""
    if not DEFAULT_RECORD.is_file():
        return None
    old = load(DEFAULT_RECORD) or {}
    old_stamp = str(old.get("tested_at_utc", "previous"))
    old_stamp = re.sub(r"[^0-9A-Za-z]+", "", old_stamp)[:20] or "previous"
    dst = unique(ROOT / "demo" / f"verification-{old_stamp}.json")
    shutil.copy2(DEFAULT_RECORD, dst)
    return str(dst.relative_to(ROOT))


def current_run(state: dict, kind: str) -> Optional[pathlib.Path]:
    key = f"{kind}_run"
    value = state.get(key)
    return ROOT / "demo/runs" / value if value else None


def evidence_checks(logs: pathlib.Path) -> list[dict]:
    checks = []

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    state = load(STATE) or {}
    add("state", bool(state), f"demo/state.json={bool(state)}")
    t = current_run(state, "tutorial")
    h = current_run(state, "history")
    add("tutorial_naming", bool(t and t.name == "tutorial"),
        str(t.relative_to(ROOT)) if t else "missing")
    migration = state.get("naming_migration") or {}
    backup = ROOT / str(migration.get("backup", ""))
    if migration:
        add("naming_migration_recorded",
            bool(migration.get("version") and migration.get("chosen_run") and backup.is_file()),
            f"version={migration.get('version')} from={migration.get('chosen_from')} "
            f"run={migration.get('chosen_run')} backup={migration.get('backup')}")
    else:
        add("naming_migration_recorded", t is not None and t.name == "tutorial",
            "fresh delivery state: no v3 example_run to migrate; tutorial is authoritative")

    tcmp = load(t / "compare.json") if t else None
    if tcmp is None:
        add("tutorial_compare", False, "current tutorial compare.json missing")
    else:
        by = {x["case"]: x for x in tcmp}
        expected = {
            "A": (1, 1, [25]),
            "B": (2, 2, [25, 26]),
            "C": (0, 0, []),
            "D": (1, 0, []),
        }
        ok = set(by) == set(expected)
        detail = []
        for case, (nc, no, up) in expected.items():
            x = by.get(case, {})
            got = (x.get("candidates"), x.get("confirmed_objects"),
                   x.get("confirmed_use_points"))
            good = got == (nc, no, up)
            ok = ok and good
            detail.append(f"{case}={got}{'' if good else ' expected ' + str((nc, no, up))}")
        add("tutorial_compare", ok, "; ".join(detail))

    aq = t / "A/candidate-01/klee-smt-export/query.smt2" if t else None
    az = load(t / "A/candidate-01/klee-smt-export/z3-replay.json") if t else None
    add("tutorial_A_query", bool(aq and aq.is_file()),
        str(aq.relative_to(ROOT)) if aq and aq.is_file() else "missing")
    add("tutorial_A_sat", bool(az and az.get("result") == "sat"),
        f"z3={az.get('result') if az else None} model={az.get('model') if az else None}")
    replay_query = str((az or {}).get("query", ""))
    if replay_query.startswith("/work/"):
        replay_query = str(ROOT / replay_query[len("/work/"):])
    add("tutorial_same_query",
        bool(az and aq and pathlib.Path(replay_query) == aq),
        f"replay_query={az.get('query') if az else None}")

    hcmp = load(h / "compare.json") if h else None
    if hcmp is None:
        add("history_compare", False, "current history compare.json missing")
    else:
        h1, h2 = hcmp.get("h1", {}), hcmp.get("h2", {})
        ok = (h1.get("confirmed_objects") == h1.get("target_objects") == 2
              and h1.get("confirmed_use_points") == [825]
              and h1.get("queries") == 2
              and h1.get("z3_results") == ["sat", "sat"]
              and h2.get("confirmed_objects") == 0
              and h2.get("target_objects") == 2
              and h2.get("queries") == 0)
        add("history_compare", ok, f"h1={h1}; h2={h2}")
        h2_queries = list((h / "h2/candidates").glob("candidate-*/klee-smt-export/query.smt2")) if h else []
        add("history_H2_no_query", not h2_queries,
            f"h2 target queries={len(h2_queries)} (expected 0)")

    record = load(CONTAINER_RECORD) or {}
    live_id = docker_inspect("{{.Id}}")
    rec_id = record.get("id", "")
    add("container_record", bool(record), str(CONTAINER_RECORD.relative_to(ROOT)))
    add("container_identity",
        bool(rec_id and rec_id == live_id and record.get("name") == CONTAINER),
        f"record_id={rec_id} live_id={live_id} name={record.get('name')}")
    add("container_platform", record.get("platform") == "linux/amd64",
        f"platform={record.get('platform')}")
    add("container_mount",
        (record.get("mount") or {}).get("source") == str(ROOT)
        and (record.get("mount") or {}).get("destination") == "/work",
        f"mount={record.get('mount')}")

    ids = set()
    for log in logs.glob("*.log"):
        text = log.read_text(encoding="utf-8", errors="replace")
        ids.update(re.findall(r"container_id:\s*([0-9a-f]{64})", text))
    add("container_id_consistent", len(ids) == 1 and (not live_id or ids == {live_id}),
        f"unique_ids={len(ids)} live_id={live_id}")

    preserved = []
    if t:
        preserved += [
            t / "compare.json",
            t / "A/candidate-01/klee-smt-export/query.smt2",
            t / "A/candidate-01/klee-smt-export/z3-replay.json",
            t / "A/candidate-01/klee-smt-export/command.txt",
        ]
    if h:
        preserved += [
            h / "compare.json",
            h / "verify.json",
            h / "h2/confirm_result.absent.txt",
        ]
        preserved += [pathlib.Path(p) for p in
                      glob.glob(str(h / "h1/candidates/candidate-*/klee-smt-export/query.smt2"))]
    add("artifacts_preserved_after_stop", all(p.is_file() for p in preserved),
        f"{sum(p.is_file() for p in preserved)}/{len(preserved)} files present after stop")
    add("state_preserved_after_stop",
        bool(state.get("tutorial_run") and state.get("history_run")),
        f"tutorial_run={state.get('tutorial_run')} history_run={state.get('history_run')}")

    val = load(ROOT / "artifacts/VALIDATION.json") or {}
    formal_hist = None
    for p in HIST_RUNS.glob("*/summary.json"):
        d = load(p)
        if d and d.get("target_h1_confirmed") and not d.get("target_h2_confirmed"):
            if formal_hist is None or p.stat().st_mtime > formal_hist.stat().st_mtime:
                formal_hist = p
    add("formal_evidence_intact",
        bool(val.get("ok")) and formal_hist is not None,
        f"VALIDATION.ok={val.get('ok')} latest_formal_history={formal_hist.parent.name if formal_hist else 'missing'}")

    stopped = docker_inspect("{{.State.Running}}")
    add("container_stopped_at_end", stopped == "false", f"running={stopped or 'missing'}")
    return checks


def main() -> int:
    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    logs = ROOT / "logs" / f"demo-verification-{stamp}"
    logs.mkdir(parents=True, exist_ok=False)
    archived = archive_previous()
    results = []
    for i, args in enumerate(COMMANDS, 1):
        slug = "-".join(args)
        log = logs / f"{i:02d}-{slug}.log"
        with log.open("w", encoding="utf-8", errors="replace") as f:
            f.write("$ ./DEMO.sh " + " ".join(args) + "\n")
            f.flush()
            p = subprocess.run([str(DEMO), *args], cwd=ROOT, stdout=f,
                               stderr=subprocess.STDOUT, text=True)
        results.append({"command": ["./DEMO.sh", *args], "exit_code": p.returncode,
                        "log": str(log.relative_to(ROOT))})
        print(f"{'PASS' if p.returncode == 0 else 'FAIL'} "
              f"./DEMO.sh {' '.join(args)} rc={p.returncode}", flush=True)

    checks = evidence_checks(logs)
    commands_ok = all(x["exit_code"] == 0 for x in results)
    evidence_ok = all(x["pass"] for x in checks)
    state = load(STATE) or {}
    record = load(CONTAINER_RECORD) or {}
    payload = {
        "tested_at_utc": now.isoformat(),
        "run_stamp": stamp,
        "log_dir": str(logs.relative_to(ROOT)),
        "archived_previous_record": archived,
        "all_pass": commands_ok and evidence_ok,
        "commands_all_rc0": commands_ok,
        "evidence_all_pass": evidence_ok,
        "commands": results,
        "evidence": checks,
        "state": state,
        "container": record,
        "run_ids": {
            "tutorial": state.get("tutorial_run"),
            "history": state.get("history_run"),
        },
    }
    text = json.dumps(payload, indent=2) + "\n"
    DEFAULT_RECORD.write_text(text, encoding="utf-8")
    (ROOT / "demo" / f"verification-{stamp}.json").write_text(text, encoding="utf-8")
    for c in checks:
        print(f"{'PASS' if c['pass'] else 'FAIL'} {c['check']}: {c['detail']}")
    print(f"archived previous record: {archived or 'none'}")
    print(f"record: demo/verification-{stamp}.json")
    print(f"container: {record.get('name')} {record.get('id')}")
    print(f"tutorial run: {state.get('tutorial_run')}")
    print(f"history run: {state.get('history_run')}")
    print("DEMO VERIFICATION:", "PASS" if payload["all_pass"] else "FAIL")
    return 0 if payload["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
