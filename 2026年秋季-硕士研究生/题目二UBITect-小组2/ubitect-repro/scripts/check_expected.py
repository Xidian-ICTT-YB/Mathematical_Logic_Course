#!/usr/bin/env python3
"""Check A-D and H1/H2 against the documented expected observations.

This is intentionally stricter than structural validation: it reads the real
warnings/confirm/query/replay files produced by the current run and writes a
machine-readable acceptance record.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import pathlib
import re
import sys


def project_root() -> pathlib.Path:
    p = pathlib.Path(os.environ.get("UBITECT_ROOT", "/work"))
    if (p / "artifacts").is_dir():
        return p
    return pathlib.Path(__file__).resolve().parent.parent


ROOT = project_root()
ART = ROOT / "artifacts"


def load(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_confirm_lines(path: pathlib.Path) -> list[int]:
    lines = []
    if not path.is_file():
        return lines
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        if obj.get("find") == "Yes" and "lineNo" in obj:
            lines.append(int(obj["lineNo"]))
    return sorted(set(lines))


def find_case(case_id: str) -> pathlib.Path:
    matches = sorted(ART.glob(f"{case_id}_*"))
    if len(matches) != 1:
        raise SystemExit(f"expected exactly one {case_id}_* artifact directory, got {matches}")
    return matches[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--history-run", default="")
    ap.add_argument("--run-id", default="")
    ap.add_argument("--out", default=str(ART / "ACCEPTANCE.json"))
    args = ap.parse_args()

    checks: list[dict] = []

    def check(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    summary_path = ART / "summary.json"
    if not summary_path.is_file():
        print("FATAL: missing artifacts/summary.json; run ./REPRODUCE.sh first",
              file=sys.stderr)
        return 2
    summary = load(summary_path)
    cases = {c["case"]: c for c in summary.get("cases", [])}
    check("four_cases_present", set(cases) == {"A", "B", "C", "D"}, str(sorted(cases)))

    expected = {
        "A": {"candidates": 1, "lines": [25], "queries": 1, "query_lines": [25]},
        "B": {"candidates": 2, "lines": [25, 26], "queries": 2, "query_lines": [25, 26]},
        "C": {"candidates": 0, "lines": [], "queries": 0, "query_lines": []},
        "D": {"candidates": 1, "lines": [], "queries": 0, "query_lines": []},
    }

    for case_id, exp in expected.items():
        case = cases.get(case_id)
        if not case:
            continue
        case_dir = find_case(case_id)
        check(f"{case_id}_candidates", case["candidate_count"] == exp["candidates"],
              f"candidates={case['candidate_count']} expected={exp['candidates']}")
        check(f"{case_id}_confirmed_original",
              case["confirmed_lines_default_reporting"] == exp["lines"],
              f"lines={case['confirmed_lines_default_reporting']} expected={exp['lines']}")
        check(f"{case_id}_confirmed_export",
              case["confirmed_lines_smt_export_build"] == exp["lines"],
              f"lines={case['confirmed_lines_smt_export_build']} expected={exp['lines']}")

        cand_dirs = sorted((case_dir / "candidates").glob("candidate-*"))
        check(f"{case_id}_candidate_dirs", len(cand_dirs) == exp["candidates"],
              f"dirs={len(cand_dirs)}")
        queries = sorted((case_dir / "candidates").glob("candidate-*/klee-smt-export/query.smt2"))
        check(f"{case_id}_query_count", len(queries) == exp["queries"],
              f"query.smt2 files={len(queries)} expected={exp['queries']}")

        if exp["queries"]:
            outputs = []
            query_lines = []
            for q in queries:
                rj = q.parent / "z3-replay.json"
                data = load(rj) if rj.is_file() else {}
                text = q.read_text(encoding="utf-8", errors="replace")
                query_lines.extend(int(m) for m in re.findall(
                    r"candidate lineNo=(\d+)", text))
                outputs.append({
                    "query": str(q.relative_to(ROOT)),
                    "result": data.get("result"),
                    "model": data.get("model"),
                    "z3_version": data.get("z3_version"),
                })
            check(f"{case_id}_queries_sat",
                  all(x["result"] == "sat" for x in outputs),
                  json.dumps(outputs, ensure_ascii=False))
            check(f"{case_id}_query_lines",
                  sorted(set(query_lines)) == sorted(set(exp["query_lines"])),
                  f"lines={sorted(set(query_lines))} expected {exp['query_lines']}")

        if case_id == "A":
            a_dir = case_dir / "candidates/candidate-01-line-25"
            orig = read_confirm_lines(a_dir / "klee-original/confirm_result.json")
            export = read_confirm_lines(a_dir / "klee-smt-export/confirm_result.json")
            check("A_line25_original_confirm", orig == [25], str(orig))
            check("A_line25_export_confirm", export == [25], str(export))
            q = a_dir / "klee-smt-export/query.smt2"
            check("A_real_query_present", q.is_file(), str(q))
            if q.is_file():
                text = q.read_text(encoding="utf-8", errors="replace")
                check("A_query_target_line25", "candidate lineNo=25" in text,
                      "query header")
                check("A_query_input0_64bit",
                      "(declare-fun input_0 () (_ BitVec 64))" in text,
                      "KLEE encoder declares input_0 as 64-bit")
                check("A_query_status_metadata",
                      "(set-info :status unknown)" in text,
                      "metadata only; not a solver result")
                data = load(a_dir / "klee-smt-export/z3-replay.json")
                check("A_z3_sat", data.get("result") == "sat", str(data.get("result")))
                check("A_z3_model_input0_zero",
                      "input_0 = 0" in str(data.get("model", "")),
                      str(data.get("model")))
                check("A_z3_version", data.get("z3_version") == "4.8.8",
                      str(data.get("z3_version")))
            # The A candidate's block/use evidence.
            warning = load(a_dir / "warning-context.json")
            check("A_use_block_line25",
                  warning["warning"].get("lineNo") == 25,
                  json.dumps(warning["warning"], ensure_ascii=False))

        if case_id == "B":
            check("B_no_dedup_build",
                  "UBITECT_NO_DEDUP" in (case_dir / "README.txt").read_text(encoding="utf-8")
                  and "UBITECT_NO_DEDUP" in case.get("config_note", ""),
                  case.get("config_note", ""))
            b25 = load(case_dir / "candidates/candidate-01-line-25/result.json")
            b26 = load(case_dir / "candidates/candidate-02-line-26/result.json")
            check("B_line25_confirm",
                  b25["original"]["confirmed_lines"] == [25]
                  and b25["export"]["confirmed_lines"] == [25],
                  f"{b25['original']['confirmed_lines']} / {b25['export']['confirmed_lines']}")
            check("B_line26_confirm",
                  b26["original"]["confirmed_lines"] == [26]
                  and b26["export"]["confirmed_lines"] == [26],
                  f"{b26['original']['confirmed_lines']} / {b26['export']['confirmed_lines']}")

        if case_id == "C":
            check("C_source_null_init",
                  "struct test_struct *backlog = NULL;" in
                  (case_dir / "backlog.c").read_text(encoding="utf-8"),
                  "backlog.c")
            check("C_no_warnings",
                  (case_dir / "warnings.absent.txt").is_file()
                  and not (case_dir / "warnings.json").is_file(),
                  "warnings.absent.txt")

        if case_id == "D":
            check("D_source_short_circuit",
                  "if(a && backlog){" in (case_dir / "backlog.c").read_text(encoding="utf-8"),
                  "backlog.c")
            check("D_no_confirmation",
                  (case_dir / "confirm_result.absent.txt").is_file()
                  and not (case_dir / "confirm_result.json").is_file(),
                  "confirm_result.absent.txt")
            check("D_no_target_query",
                  not (case_dir / "candidates/candidate-01-line-25/klee-smt-export/query.smt2").exists(),
                  "KLEE did not export a target query")

    # History
    hist_root = ROOT / "history/ahci_xgene/runs"
    hist_run = args.history_run
    if not hist_run:
        candidates = sorted(hist_root.glob("HIST-*"), key=lambda p: p.stat().st_mtime)
        hist_run = candidates[-1].name if candidates else ""
    check("history_run_present", bool(hist_run) and (hist_root / hist_run).is_dir(),
          hist_run or "missing")
    if hist_run and (hist_root / hist_run).is_dir():
        hsum = load(hist_root / hist_run / "summary.json")
        by = {h["version"]: h for h in hsum.get("histories", [])}
        h1, h2 = by.get("h1", {}), by.get("h2", {})
        check("H1_target_objects", h1.get("target_warning_count") == 2,
              str(h1.get("target_warning_count")))
        check("H1_confirmed_objects", h1.get("target_confirmed_count") == 2,
              str(h1.get("target_confirmed_count")))
        check("H1_use_points", h1.get("target_confirmed_lines") == [825],
              str(h1.get("target_confirmed_lines")))
        h1_queries = sorted((hist_root / hist_run / "h1/candidates").glob(
            "candidate-*/klee-smt-export/query.smt2"))
        h1_replays = [load(q.parent / "z3-replay.json")
                      for q in h1_queries if (q.parent / "z3-replay.json").is_file()]
        check("H1_query_count", len(h1_queries) == 2, str(len(h1_queries)))
        check("H1_query_sat", len(h1_replays) == 2
              and all(x.get("result") == "sat" for x in h1_replays),
              json.dumps([x.get("result") for x in h1_replays]))
        check("H1_query_model_input0_zero",
              all("input_0 = 0" in str(x.get("model", "")) for x in h1_replays),
              json.dumps([x.get("model") for x in h1_replays], ensure_ascii=False))
        check("H2_target_objects", h2.get("target_warning_count") == 2,
              str(h2.get("target_warning_count")))
        check("H2_confirmed_objects", h2.get("target_confirmed_count") == 0,
              str(h2.get("target_confirmed_count")))
        h2_queries = list((hist_root / hist_run / "h2/candidates").glob(
            "candidate-*/klee-smt-export/query.smt2"))
        check("H2_no_target_query", not h2_queries, f"{len(h2_queries)} queries")
        check("history_commits",
              hsum.get("upstream_commit") == "8134233e8d346aaa1c929dc510e75482ae318bce"
              and hsum.get("parent_commit") == "8ba559fd09bcf4e87faad3efa465dacf04c076c9",
              f"{hsum.get('upstream_commit')} / {hsum.get('parent_commit')}")

    payload = {
        "ok": all(c["ok"] for c in checks),
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "run_id": args.run_id or summary.get("run_id", ""),
        "history_run": hist_run,
        "checks": checks,
    }
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    for c in checks:
        print(("PASS" if c["ok"] else "FAIL"), c["check"], "-", c["detail"])
    print("EXPECTED-RESULT CHECK:", "PASS" if payload["ok"] else "FAIL")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
