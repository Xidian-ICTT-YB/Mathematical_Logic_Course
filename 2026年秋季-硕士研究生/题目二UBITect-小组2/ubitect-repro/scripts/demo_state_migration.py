#!/usr/bin/env python3
"""One-time migration from the v3 ``example`` state keys to ``tutorial``.

Old v3 state can contain both a recent ``example_run`` and a much older legacy
``tutorial_run``.  The migration therefore follows the run that was actually
current under v3 (``example_run``) instead of blindly preferring the tutorial
key.  The chosen physical path is preserved verbatim; a run under
``.../example`` is not renamed or rewritten.  After this migration
``tutorial_run`` / ``tutorial_step`` are authoritative and ``example_run`` is
retained only as historical metadata.

The migration is idempotent: ``naming_migration.version`` records that it has
already run.  The original state file is copied to
``demo/state.pre-tutorial-migration-<UTC>.json`` before any change.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import shutil
import sys

VERSION = 1


def _valid_run(root: pathlib.Path, value) -> bool:
    return bool(value) and (root / "demo/runs" / str(value)).is_dir()


def migrate(root: pathlib.Path, quiet: bool = False) -> dict:
    """Apply the one-time migration under *root*; return a summary dict."""
    root = pathlib.Path(root)
    state_path = root / "demo/state.json"
    if not state_path.is_file():
        return {"action": "no-state", "state": str(state_path)}

    try:
        s = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"DEMO FAILED: invalid JSON in {state_path}: {exc}")
    if not isinstance(s, dict):
        raise SystemExit(f"DEMO FAILED: {state_path} must contain a JSON object")

    marker = s.get("naming_migration")
    if isinstance(marker, dict) and int(marker.get("version", 0)) >= VERSION:
        return {"action": "already-migrated", "marker": marker}

    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    backup = state_path.parent / f"state.pre-tutorial-migration-{stamp}.json"
    n = 2
    while backup.exists():
        backup = state_path.parent / f"state.pre-tutorial-migration-{stamp}-{n}.json"
        n += 1
    shutil.copy2(state_path, backup)

    example_run = s.get("example_run")
    example_step = s.get("example_step")
    old_tutorial_run = s.get("tutorial_run")
    old_tutorial_step = s.get("tutorial_step")
    example_valid = _valid_run(root, example_run)
    tutorial_valid = _valid_run(root, old_tutorial_run)

    # v3 made example_run authoritative.  Only prefer the old tutorial key when
    # example_run is absent or its directory no longer exists but the old
    # tutorial directory does.
    if example_run and (example_valid or not tutorial_valid):
        chosen_from = "example_run"
        chosen_run = example_run
        chosen_step = example_step
    elif old_tutorial_run:
        chosen_from = "tutorial_run"
        chosen_run = old_tutorial_run
        chosen_step = old_tutorial_step
    else:
        chosen_from = "none"
        chosen_run = None
        chosen_step = None

    if chosen_run:
        s["tutorial_run"] = chosen_run
        s["tutorial_step"] = chosen_step
    elif not old_tutorial_run:
        s.pop("tutorial_run", None)
        s.pop("tutorial_step", None)

    s["naming_migration"] = {
        "version": VERSION,
        "applied_at_utc": now.isoformat(),
        "backup": str(backup.relative_to(root)),
        "chosen_from": chosen_from,
        "chosen_run": chosen_run,
        "chosen_step": chosen_step,
        "previous_example_run": example_run,
        "previous_example_step": example_step,
        "previous_tutorial_run": old_tutorial_run,
        "previous_tutorial_step": old_tutorial_step,
        "example_run_exists": example_valid,
        "old_tutorial_run_exists": tutorial_valid,
        "physical_path_preserved": True,
        "note": ("tutorial_run is authoritative after this migration; "
                 "example_run remains historical metadata and is not read "
                 "for the current run."),
    }
    state_path.write_text(json.dumps(s, indent=2, sort_keys=True) + "\n",
                          encoding="utf-8")

    result = {
        "action": "migrated",
        "chosen_from": chosen_from,
        "chosen_run": chosen_run,
        "chosen_step": chosen_step,
        "backup": str(backup.relative_to(root)),
        "example_run_exists": example_valid,
        "old_tutorial_run_exists": tutorial_valid,
    }
    if not quiet:
        print(f"state migration: v{VERSION} {chosen_from} -> "
              f"tutorial_run={chosen_run or 'none'} "
              f"(backup {backup.relative_to(root)})")
    return result


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    verbose = "--verbose" in sys.argv[1:]
    root = pathlib.Path(args[0]) if args else pathlib.Path("/work")
    result = migrate(root)
    if result.get("action") == "already-migrated":
        if verbose:
            marker = result.get("marker", {})
            print(f"state migration: already applied (v{marker.get('version')}, "
                  f"tutorial_run={marker.get('chosen_run')})")
    elif result.get("action") == "no-state":
        if verbose:
            print("state migration: demo/state.json absent; nothing to migrate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
