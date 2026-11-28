#!/usr/bin/env python3
"""Validate the generated experiment evidence without hard-coding the observed
line numbers.  Structural properties are what make the artifacts trustworthy."""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path("/work")
ART = ROOT / "artifacts"

checks: list[dict] = []


def check(name: str, ok: bool, detail: str) -> None:
    checks.append({"check": name, "ok": bool(ok), "detail": detail})


def load(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    summary_path = ART / "summary.json"
    if not summary_path.is_file():
        print("FATAL: missing artifacts/summary.json", file=sys.stderr)
        return 2
    summary = load(summary_path)
    cases = {c["case"]: c for c in summary.get("cases", [])}
    check("four_cases_present", set(cases) == {"A", "B", "C", "D"}, str(sorted(cases)))

    for case_id in ("A", "B", "C", "D"):
        case = cases.get(case_id)
        if not case:
            continue
        case_dir = ART / f"{case_id}_{case['title']}"
        check(
            f"{case_id}_source_present",
            (case_dir / "backlog.c").is_file(),
            str(case_dir / "backlog.c"),
        )
        check(
            f"{case_id}_bitcode_present",
            (case_dir / "backlog.bc").is_file() and (case_dir / "backlog.llbc").is_file(),
            "backlog.bc + backlog.llbc",
        )
        check(
            f"{case_id}_ir_present",
            (case_dir / "backlog.ll" ).is_file(),
            str(case_dir / "backlog.ll"),
        )
        check(
            f"{case_id}_stage1_present",
            (case_dir / "stage1.log").is_file(),
            str(case_dir / "stage1.log"),
        )
        check(
            f"{case_id}_warnings_parsed",
            (case_dir / "warnings.parsed.json").is_file(),
            str(case_dir / "warnings.parsed.json"),
        )
        check(
            f"{case_id}_candidate_count_consistent",
            case["candidate_count"]
            == len(load(case_dir / "warnings.parsed.json")),
            f"{case['candidate_count']} candidates",
        )

        for cand in case["candidates"]:
            cand_dir = case_dir / "candidates" / f"candidate-{cand['index']:02d}-line-{cand['lineNo']}"
            check(
                f"{case_id}_c{cand['index']}_warning_raw",
                (cand_dir / "warning.json").is_file(),
                str(cand_dir / "warning.json"),
            )
            for variant in ("original", "export"):
                rec = cand[variant]
                check(
                    f"{case_id}_c{cand['index']}_{variant}_llvm_link_rc0",
                    rec["link"]["exit_code"] == 0 and not rec["link"]["timed_out"],
                    f"rc={rec['link']['exit_code']}",
                )
                check(
                    f"{case_id}_c{cand['index']}_{variant}_klee_rc0",
                    rec["exit_code"] == 0 and not rec["timed_out"],
                    f"rc={rec['exit_code']}",
                )
                check(
                    f"{case_id}_c{cand['index']}_{variant}_command_present",
                    (cand_dir / ("klee-original" if variant == "original" else "klee-smt-export") / "command.json").is_file(),
                    "real KLEE argv preserved",
                )
            check(
                f"{case_id}_c{cand['index']}_same_confirmation",
                cand["original"]["confirmed_lines"] == cand["export"]["confirmed_lines"],
                f"{cand['original']['confirmed_lines']} vs {cand['export']['confirmed_lines']}",
            )

        if case["candidate_count"]:
            if case["confirmed_count_default_reporting"]:
                check(
                    f"{case_id}_raw_confirm_present",
                    (case_dir / "confirm_result.json").is_file(),
                    "case-level concatenation of raw candidate files",
                )
            else:
                check(
                    f"{case_id}_confirm_absence_documented",
                    (case_dir / "confirm_result.absent.txt").is_file(),
                    "no fabricated confirm_result.json",
                )

    analysis = load(ART / "analysis" / "manifest.json")
    real = analysis.get("real_exports", [])
    check("real_smt_exports_present", len(real) >= 1, f"{len(real)} real exports")
    check(
        "real_smt_has_sat_model",
        any(x.get("result") == "sat" and x.get("model") for x in real),
        "at least one SAT replay with model",
    )
    independent = {x["label"]: x for x in analysis.get("independent", [])}
    a_formula = independent.get("a_zero_and_nonzero_32bit.smt2")
    check(
        "independent_a_zero_and_nonzero_unsat",
        bool(a_formula and a_formula.get("result") == "unsat"),
        "teaching reconstruction, clearly separate from KLEE exports",
    )
    check(
        "z3_version_pinned",
        analysis.get("z3_version") == "4.8.8",
        str(analysis.get("z3_version")),
    )
    check(
        "container_arch_x86_64",
        summary.get("container_arch") == "x86_64",
        str(summary.get("container_arch")),
    )
    check(
        "llvm_rtti_off",
        summary.get("llvm_has_rtti") == "NO",
        str(summary.get("llvm_has_rtti")),
    )
    check(
        "original_export_klee_differ",
        summary.get("klee_original_sha256") != summary.get("klee_export_build_sha256"),
        "the preserved no-export binary is a distinct build",
    )

    payload = {
        "ok": all(c["ok"] for c in checks),
        "checks": checks,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for c in checks:
        print(("PASS" if c["ok"] else "FAIL"), c["check"], "-", c["detail"])
    print("VALIDATION:", "PASS" if payload["ok"] else "FAIL")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
