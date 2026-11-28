#!/usr/bin/env python3
"""Replay an SMT-LIB query with the pinned Z3 Python API and record the model."""
import argparse
import json
import pathlib
import z3


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--json-out")
    args = ap.parse_args()

    query = pathlib.Path(args.query)
    solver = z3.Solver()
    solver.set("timeout", 60000)
    solver.add(z3.parse_smt2_file(str(query)))
    result = solver.check()
    model = solver.model() if result == z3.sat else None
    payload = {
        "query": str(query),
        "z3_version": z3.get_version_string(),
        "result": str(result),
        "model": str(model) if model is not None else None,
    }
    print(f"query: {query}")
    print(f"z3_version: {z3.get_version_string()}")
    print(f"result: {result}")
    if model is not None:
        print("model:")
        print(model)
    if args.json_out:
        pathlib.Path(args.json_out).write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return 0 if result != z3.unknown else 2


if __name__ == "__main__":
    raise SystemExit(main())
