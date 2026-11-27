#!/usr/bin/env python3
"""Run the four VSTTE-2016 algorithms on selected DeviceDriversLinux64 tasks.

Uses the paper's own CPAchecker 1.6.1-svn bundle inside a linux/amd64 container
(the bundle ships only a Linux MathSAT5 native library).
"""
import argparse, hashlib, json, os, re, subprocess, sys, time
import concurrent.futures as cf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CPA = os.path.join(ROOT, "supplements/supplements-vstte/CPAchecker")
BENCH = os.path.join(ROOT, "benchmarks")
LOGS = os.path.join(ROOT, "results/logs")
RESULTS = os.path.join(ROOT, "results/runs.jsonl")
IMAGE = "eclipse-temurin:8-jre"

COMMON = ["-heap", "{heap}M", "-noout", "-64", "-timelimit", "{tl}s", "-stats"]

CONFIGS = {
    "bmc": [
        "-bmc",
        "-setprop", "solver.solver=MATHSAT5",
        "-setprop", "cpa.predicate.encodeBitvectorAs=BITVECTOR",
        "-setprop", "cpa.predicate.encodeFloatAs=FLOAT",
        "-setprop", "analysis.checkCounterexamples=true",
        "-setprop", "counterexample.checker=CBMC",
        "-setprop", "cpa.bounds.maxLoopIterationsUpperBound=0",
        "-setprop", "cpa.bounds.maxLoopIterations=1",
        "-setprop", "cpa.bounds.maxLoopIterationAdjusterFactory=INCREMENT",
    ],
    "k-induction": ["-sv-comp16--k-induction"],
    "predicate": [
        "-predicateAnalysis-PredAbsRefiner-ABEl-bitprecise",
        "-setprop", "cpa.predicate.encodeFloatAs=FLOAT",
        "-setprop", "analysis.checkCounterexamples=true",
        "-setprop", "counterexample.checker=CBMC",
    ],
    "impact": [
        "-predicateAnalysis-ImpactRefiner-ABEl-bitprecise",
        "-setprop", "cpa.predicate.encodeFloatAs=FLOAT",
        "-setprop", "analysis.checkCounterexamples=true",
        "-setprop", "counterexample.checker=CBMC",
        "-setprop", "cpa.forcedCovering=cpa.predicate.PredicateForcedCovering",
    ],
}


def slug(task):
    h = hashlib.sha1(task.encode()).hexdigest()[:10]
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", os.path.basename(task))[-80:]
    return f"{h}_{base}"


def run_one(task, algo, timeout, heap, mem):
    log_path = os.path.join(LOGS, f"{slug(task)}__{algo}.log")
    if os.path.exists(log_path) and os.path.getsize(log_path) > 0:
        # reuse only if a completed result marker is present
        with open(log_path, "r", errors="replace") as f:
            txt = f.read()
        if "Verification result:" in txt or "TIMEOUT" in txt or "OutOfMemoryError" in txt:
            return parse(task, algo, txt, 0.0, None, "cached")

    spec = os.path.join("/bench", "c", task.split("/")[0], "ALL.prp")
    src = os.path.join("/bench", "c", task)
    tl = max(1, int(timeout) - 10)
    args = []
    for a in COMMON:
        args.append(a.format(heap=heap, tl=tl))
    args += CONFIGS[algo]
    args += ["-spec", spec, src]

    cmd = ["docker", "run", "--rm", "--platform", "linux/amd64",
           "--memory", f"{mem}m", "--memory-swap", f"{mem}m",
           "-v", f"{CPA}:/cpa:ro", "-v", f"{BENCH}:/bench:ro",
           "-w", "/cpa", IMAGE, "bash", "/cpa/scripts/cpa.sh"] + args

    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out, err, code = p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        err = (e.stderr or b"").decode("utf-8", "replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
        code = 124
    wall = time.time() - t0
    txt = out + "\n" + err
    if code == 124:
        txt += "\nEXTERNAL_TIMEOUT\n"
    elif code == 137:
        txt += "\nOOM_KILLED_BY_CGROUP\n"
    with open(log_path, "w") as f:
        f.write(txt)
    return parse(task, algo, txt, wall, code, "run")


def num(pat, txt):
    m = re.search(pat, txt)
    return float(m.group(1)) if m else None


def parse(task, algo, txt, wall, code, source):
    verdict = None
    if re.search(r"Verification result:\s*TRUE", txt):
        verdict = "TRUE"
    elif re.search(r"Verification result:\s*FALSE", txt):
        verdict = "FALSE"
    elif re.search(r"Verification result:\s*UNKNOWN", txt):
        verdict = "UNKNOWN"
    if verdict is None:
        if code == 137 or "OOM_KILLED_BY_CGROUP" in txt:
            verdict = "OUT_OF_MEMORY"
        elif code == 124 or "EXTERNAL_TIMEOUT" in txt:
            verdict = "KILLED"
        elif "OutOfMemoryError" in txt:
            verdict = "OUT_OF_MEMORY"
        else:
            verdict = "ERROR"
    cpu = num(r"Total CPU time for CPAchecker:\s*([0-9.]+)", txt)
    total = num(r"Total time for CPAchecker:\s*([0-9.]+)", txt)
    k = num(r"value of k:\s*(\d+)", txt) or num(r"k\s*=\s*(\d+)", txt)
    return dict(task=task, algo=algo, verdict=verdict, wall=round(wall, 3),
                exit_code=code, cpu_s=cpu, total_s=total, k=k,
                external_timeout=("EXTERNAL_TIMEOUT" in txt),
                oom=("OutOfMemoryError" in txt or code == 137),
                log=os.path.join("results/logs", f"{slug(task)}__{algo}.log"),
                source=source, ts=time.strftime("%Y-%m-%dT%H:%M:%S"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--heap", type=int, default=2600)
    ap.add_argument("--mem", type=int, default=3200)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--algos", default="bmc,k-induction,predicate,impact")
    args = ap.parse_args()

    os.makedirs(LOGS, exist_ok=True)
    tasks = json.load(open(os.path.join(ROOT, "manifest.json")))
    if args.pilot:
        # one representative per bucket
        seen, pilot = set(), []
        for t in tasks:
            if t["bucket"] not in seen:
                seen.add(t["bucket"])
                pilot.append(t)
        tasks = pilot
    if args.only:
        tasks = [t for t in tasks if args.only in t["task"]]
    algos = args.algos.split(",")
    jobs = [(t, a) for t in tasks for a in algos]

    done = set()
    if os.path.exists(RESULTS):
        for line in open(RESULTS):
            try:
                r = json.loads(line)
                # failed startup runs are retried
                if r.get("verdict") not in ("ERROR",):
                    done.add((r["task"], r["algo"]))
            except Exception:
                pass
    if not args.force:
        jobs = [j for j in jobs if (j[0]["task"], j[1]) not in done]

    print(f"{len(jobs)} runs queued, timeout={args.timeout}s heap={args.heap}M mem={args.mem}M workers={args.workers}")
    t0 = time.time()
    n = 0
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(run_one, t["task"], a, args.timeout, args.heap, args.mem): (t, a) for t, a in jobs}
        for fu in cf.as_completed(futs):
            r = fu.result()
            n += 1
            with open(RESULTS, "a") as f:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
            print(f"[{n}/{len(jobs)}] {r['algo']:12s} {r['verdict']:14s} "
                  f"wall={r['wall']:7.1f}s cpu={r['cpu_s']} {r['task'].split('/')[-1][:70]}", flush=True)
    print(f"done in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
