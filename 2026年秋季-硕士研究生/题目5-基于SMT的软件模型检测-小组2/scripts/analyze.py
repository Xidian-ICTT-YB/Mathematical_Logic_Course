#!/usr/bin/env python3
"""Merge measured runs with the paper's reported results and summarize."""
import csv, json, os, statistics, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALGOS = ["bmc", "k-induction", "predicate", "impact"]
NORM = {
    "TRUE": "safe", "FALSE": "unsafe", "UNKNOWN": "unknown",
    "KILLED": "timeout", "OUT_OF_MEMORY": "memout", "ERROR": "error",
}
PAPER = {"true": "safe", "false(reach)": "unsafe", "TIMEOUT": "timeout",
         "OUT OF MEMORY": "memout", "OUT OF JAVA MEMORY": "memout",
         "unknown": "unknown", "EXCEPTION": "error", "SEGMENTATION FAULT": "error"}


def paper_norm(s):
    if s in PAPER: return PAPER[s]
    if s.startswith("ERROR"): return "error"
    if s.startswith("TIMEOUT"): return "timeout"
    return s


def load():
    m = json.load(open(os.path.join(ROOT, "manifest.json")))
    runs = {}
    path = os.path.join(ROOT, "results/runs.jsonl")
    if os.path.exists(path):
        for line in open(path):
            try:
                r = json.loads(line)
            except Exception:
                continue
            # last record wins (targeted re-runs)
            runs[(r["task"], r["algo"])] = r
    return m, runs


def effective(r):
    """Map a run to safe/unsafe/timeout/memout/unknown/error using the log."""
    v = NORM.get(r["verdict"], r["verdict"])
    if v in ("unknown", "error"):
        log = os.path.join(ROOT, r.get("log", ""))
        txt = open(log, errors="replace").read() if os.path.exists(log) else ""
        if ("CPU-time limit" in txt or "time limit" in txt.lower()
                or "Shutting down" in txt):
            return "timeout"
    return v


def main():
    m, runs = load()
    rows = []
    for x in m:
        row = dict(task=x["task"], bucket=x["bucket"], truth=x["truth"])
        for i, a in enumerate(ALGOS):
            pst = paper_norm(x["status"][i])
            row[f"paper_{a}"] = pst
            row[f"paper_ct_{a}"] = x["ct"][i]
            r = runs.get((x["task"], a))
            if r:
                row[f"run_{a}"] = effective(r)
                row[f"wall_{a}"] = r["wall"]
                row[f"cpu_{a}"] = r["cpu_s"]
                row[f"k_{a}"] = r["k"]
            else:
                row[f"run_{a}"] = ""
                row[f"wall_{a}"] = None
                row[f"cpu_{a}"] = None
                row[f"k_{a}"] = None
        rows.append(row)

    out = os.path.join(ROOT, "results/matrix.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print("wrote", out)

    print("\n=== measured verdict counts (n=%d tasks) ===" % len(m))
    print(f"{'algo':12s} " + " ".join(f"{k:>8s}" for k in ["safe", "unsafe", "timeout", "memout", "unknown", "error", "done"]))
    for a in ALGOS:
        c = collections.Counter(r[f"run_{a}"] for r in rows if r[f"run_{a}"])
        done = sum(v for k, v in c.items() if k in ("safe", "unsafe"))
        print(f"{a:12s} " + " ".join(f"{c.get(k,0):8d}" for k in ["safe", "unsafe", "timeout", "memout", "unknown", "error"]) + f" {done:8d}")

    print("\n=== runtime among conclusive runs (CPAchecker CPU seconds) ===")
    for a in ALGOS:
        xs = [r[f"cpu_{a}"] for r in rows if r[f"run_{a}"] in ("safe", "unsafe") and r[f"cpu_{a}"]]
        if xs:
            print(f"{a:12s} n={len(xs):2d} min={min(xs):7.1f} median={statistics.median(xs):7.1f} mean={statistics.mean(xs):7.1f} max={max(xs):7.1f}")

    print("\n=== disagreements / measured vs paper ===")
    for r in rows:
        mv = [r[f"run_{a}"] for a in ALGOS]
        pv = [r[f"paper_{a}"] for a in ALGOS]
        if len(set(v for v in mv if v)) > 1:
            print(f"{r['bucket']:20s} {r['task'].split('/')[-1][:70]}")
            print(f"   measured {mv}  paper {pv}")

    print("\n=== agreement of conclusive measured verdicts with filename truth ===")
    for a in ALGOS:
        ok = bad = 0
        for r in rows:
            v = r[f"run_{a}"]
            if v in ("safe", "unsafe"):
                exp = "safe" if r["truth"] == "true" else "unsafe"
                ok += (v == exp); bad += (v != exp)
        print(f"{a:12s} correct={ok} wrong={bad}")


if __name__ == "__main__":
    main()
