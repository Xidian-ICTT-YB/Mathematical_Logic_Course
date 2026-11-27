#!/usr/bin/env python3
"""Select a stratified task sample from the VSTTE 2016 DeviceDriversLinux64 results
and download the corresponding SV-COMP 2016 sources (tag svcomp16).

Downloaded data is treated as untrusted: only written to disk, never executed.
"""
import csv, json, os, re, sys, time
import urllib.request
import concurrent.futures as cf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, "supplements/supplements-vstte/results/algorithms.DeviceDriversLinux64.table.csv")
BENCH = os.path.join(ROOT, "benchmarks")
RAW = "https://raw.githubusercontent.com/sosy-lab/sv-benchmarks/svcomp16/c/"
PROXY = "http://127.0.0.1:7897"

os.environ.setdefault("https_proxy", PROXY)
os.environ.setdefault("http_proxy", PROXY)


def load():
    rows = list(csv.reader(open(CSV, encoding="utf-8"), delimiter="\t"))
    data = [r for r in rows[3:] if len(r) > 1 and r[0].strip()]
    recs = []
    for r in data:
        t = r[0]
        truth = "false" if "_false-unreach-call" in t else ("true" if "_true-unreach-call" in t else "?")
        def f(i):
            try: return float(r[i])
            except Exception: return None
        recs.append(dict(task=t, truth=truth,
                         status=[r[1], r[10], r[22], r[37]],
                         ct=[f(2), f(11), f(23), f(38)],
                         k=[r[6], r[15], None, None]))
    return recs


def driver_key(task):
    base = os.path.basename(task)
    return re.sub(r"^(m\d+_|32_\d+_cilled_|43_\d+_cilled_|main\d+_)+", "", base)[:70]


def pick(recs):
    chosen = []

    def add(x):
        if x["task"] not in {c["task"] for c in chosen}:
            chosen.append(x)

    def dedupe(xs):
        seen, out = set(), []
        for x in xs:
            key = driver_key(x["task"])
            if key not in seen:
                seen.add(key)
                out.append(x)
        return out

    # A: all four agree safe, fast
    a = [x for x in recs if x["truth"] == "true" and x["status"] == ["true"] * 4
         and max(c for c in x["ct"] if c) <= 8]
    a.sort(key=lambda x: max(x["ct"]))
    for x in dedupe(a)[:9]:
        add(x); x["bucket"] = "A_agree_safe"

    # B: all four agree unsafe, moderate
    b = [x for x in recs if x["truth"] == "false" and all(s.startswith("false") for s in x["status"])
         and max(c for c in x["ct"] if c) <= 70]
    b.sort(key=lambda x: max(x["ct"]))
    for x in dedupe(b)[:5]:
        add(x); x["bucket"] = "B_agree_unsafe"

    # C2: BMC incomplete, k-induction proves safe
    c2 = [x for x in recs if x["truth"] == "true" and x["status"][0] == "TIMEOUT"
          and x["status"][1] == "true" and x["ct"][1] and x["ct"][1] <= 25]
    c2.sort(key=lambda x: x["ct"][1])
    for x in dedupe(c2)[:5]:
        add(x); x["bucket"] = "C2_only_kind"

    # C4: BMC and k-induction incomplete, predicate/impact prove safe
    c4 = [x for x in recs if x["truth"] == "true" and x["status"][0] == "TIMEOUT"
          and x["status"][1] == "TIMEOUT" and x["status"][2] == "true" and x["status"][3] == "true"
          and x["ct"][2] and x["ct"][2] <= 90]
    c4.sort(key=lambda x: x["ct"][2])
    for x in dedupe(c4)[:5]:
        add(x); x["bucket"] = "C4_only_pred_impact"

    # C3: only BMC finds the bug fast
    c3 = [x for x in recs if x["truth"] == "false" and x["status"][0].startswith("false")
          and not any(s.startswith("false") for s in x["status"][1:]) and x["ct"][0] and x["ct"][0] <= 90]
    c3.sort(key=lambda x: x["ct"][0])
    for x in dedupe(c3)[:3]:
        add(x); x["bucket"] = "C3_only_bmc_unsafe"

    return chosen


def fetch_one(task, dest):
    url = RAW + urllib.parse.quote(task)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                data = r.read()
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(data)
            return task, len(data), None
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
            time.sleep(2 + attempt * 3)
    return task, 0, err


def main():
    recs = load()
    chosen = pick(recs)
    os.makedirs(BENCH, exist_ok=True)
    jobs = []
    for x in chosen:
        dest = os.path.join(BENCH, "c", x["task"])
        jobs.append((x["task"], dest))
    prefixes = sorted({t.split("/")[0] for t in (j[0] for j in jobs)})
    for p in prefixes:
        jobs.append((p + "/ALL.prp", os.path.join(BENCH, "c", p, "ALL.prp")))

    results = []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(fetch_one, t, d) for t, d in jobs]
        for fu in cf.as_completed(futs):
            results.append(fu.result())

    bad = [r for r in results if r[2]]
    sizes = {r[0]: r[1] for r in results}
    for x in chosen:
        x["bytes"] = sizes.get(x["task"], 0)
    manifest = os.path.join(ROOT, "manifest.json")
    json.dump(chosen, open(manifest, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"selected {len(chosen)} tasks, downloaded {len(results)-len(bad)}/{len(results)} files")
    for b in bad:
        print("FAILED", b)
    from collections import Counter
    print(Counter(x["bucket"] for x in chosen))
    for x in chosen:
        print(f"{x['bucket']:24s} {x['truth']:5s} {x['bytes']:9d}  {x['task']}")
    print("total MB", sum(x["bytes"] for x in chosen) / 1e6)


if __name__ == "__main__":
    import urllib.parse
    main()
