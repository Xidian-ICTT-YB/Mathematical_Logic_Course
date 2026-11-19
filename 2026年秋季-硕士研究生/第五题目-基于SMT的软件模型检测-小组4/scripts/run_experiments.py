#!/usr/bin/env python3
"""Run the four VSTTE 2016 CPAchecker configurations in amd64 Docker containers."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "cpachecker-vstte:java8"
CPA_DIR = "/work/benchmarks/supplements-vstte/CPAchecker"
SPEC = "/work/benchmarks/unreach-call.prp"
ALGOS = ("BMC", "kInduction", "Predicate", "Impact")


def algorithm_options(algo: str) -> list[str]:
    common = [
        "-setprop",
        "solver.solver=MATHSAT5",
        "-setprop",
        "cpa.predicate.encodeBitvectorAs=BITVECTOR",
        "-setprop",
        "cpa.predicate.encodeFloatAs=FLOAT",
        "-setprop",
        "analysis.checkCounterexamples=true",
        "-setprop",
        "counterexample.checker=CBMC",
    ]
    if algo == "BMC":
        return [
            "-bmc",
            *common,
            "-setprop",
            "cpa.bounds.maxLoopIterationsUpperBound=0",
            "-setprop",
            "cpa.bounds.maxLoopIterations=1",
            "-setprop",
            "cpa.bounds.maxLoopIterationAdjusterFactory=INCREMENT",
        ]
    if algo == "kInduction":
        # The paper does not wrap the outer parallel algorithm in CBMC checking;
        # the nested no-AI configuration already enables bit-precise MathSAT5/CBMC.
        return [
            "-sv-comp16--k-induction",
            "-setprop",
            "solver.solver=MATHSAT5",
            "-setprop",
            "limits.time.cpu.thread=10000s",
        ]
    if algo == "Predicate":
        return ["-predicateAnalysis-PredAbsRefiner-ABEl-bitprecise", *common]
    if algo == "Impact":
        return [
            "-predicateAnalysis-ImpactRefiner-ABEl-bitprecise",
            *common,
            "-setprop",
            "cpa.forcedCovering=cpa.predicate.PredicateForcedCovering",
        ]
    raise ValueError(algo)


def run_one(
    task: dict[str, str],
    algo: str,
    timelimit: int,
    hard_timeout: int,
    memory_mb: int = 1400,
    heap_mb: int = 1000,
    skip_existing: bool = True,
    output_root: Path | None = None,
) -> dict[str, object]:
    task_id = task["task_id"]
    output_root = output_root or (ROOT / "results")
    output = output_root / task_id / algo
    container_output = "/work/" + output.relative_to(ROOT).as_posix()
    output.mkdir(parents=True, exist_ok=True)
    metadata_path = output / "metadata.json"
    log_path = output / "run.log"
    if skip_existing and metadata_path.exists() and log_path.exists():
        return json.loads(metadata_path.read_text(encoding="utf-8"))

    container_name = f"cpa-{task_id}-{algo}-{os.getpid()}".lower().replace("_", "-")
    source = "/work/" + task["source_file"]
    command = [
        "docker",
        "run",
        "--rm",
        "--platform",
        "linux/amd64",
        "--name",
        container_name,
        "--cpus",
        "2",
        "--memory",
        f"{memory_mb}m",
        "-v",
        f"{ROOT}:/work",
        "-w",
        CPA_DIR,
        IMAGE,
        "scripts/cpa.sh",
        "-heap",
        f"{heap_mb}M",
        "-stack",
        "2048k",
        *algorithm_options(algo),
        "-64",
        "-timelimit",
        f"{timelimit}s",
        "-stats",
        "-spec",
        SPEC,
        "-outputpath",
        container_output,
        source,
    ]
    start = time.monotonic()
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=hard_timeout,
        )
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = 124
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        subprocess.run(
            ["docker", "rm", "-f", container_name], capture_output=True, timeout=20
        )
    elapsed = time.monotonic() - start
    metadata: dict[str, object] = {
        "task_id": task_id,
        "short_name": task["short_name"],
        "algorithm": algo,
        "expected_verdict": task["expected_verdict"],
        "source_file": task["source_file"],
        "output_root": output_root.relative_to(ROOT).as_posix(),
        "docker_image": IMAGE,
        "docker_platform": "linux/amd64",
        "timelimit_seconds": timelimit,
        "hard_timeout_seconds": hard_timeout,
        "container_memory_mb": memory_mb,
        "java_heap_mb": heap_mb,
        "wall_seconds": round(elapsed, 3),
        "returncode": returncode,
        "outer_timeout": timed_out,
        "command": command,
    }
    log_path.write_text(
        "$ "
        + " ".join(command)
        + "\n\n"
        + stdout
        + "\n\n[stderr]\n"
        + stderr
        + f"\n\n[host] wall_seconds={elapsed:.3f} returncode={returncode} outer_timeout={timed_out}\n",
        encoding="utf-8",
    )
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", nargs="*", help="Task IDs; default: all")
    parser.add_argument("--algos", nargs="*", choices=ALGOS, default=list(ALGOS))
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--timelimit", type=int, default=90)
    parser.add_argument("--hard-timeout", type=int, default=300)
    parser.add_argument(
        "--memory", type=int, default=1400, help="Container memory in MB"
    )
    parser.add_argument("--heap", type=int, default=1000, help="Java -heap in MB")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete existing result markers before rerunning",
    )
    parser.add_argument(
        "--rerun",
        action="store_true",
        help="Overwrite existing results without deleting files (avoids bulk-delete hooks)",
    )
    parser.add_argument(
        "--output-root",
        default="results",
        help="Result directory relative to the project root (default: results). "
        "Use a separate directory for smoke tests so official results stay untouched.",
    )
    args = parser.parse_args()

    output_root = Path(args.output_root)
    if not output_root.is_absolute():
        output_root = ROOT / output_root
    output_root = output_root.resolve()
    try:
        output_root.relative_to(ROOT)
    except ValueError:
        raise SystemExit(f"--output-root must be inside {ROOT} (the Docker bind mount)")

    with (ROOT / "benchmarks" / "tasks.csv").open(encoding="utf-8") as handle:
        tasks = list(csv.DictReader(handle))
    if args.tasks:
        wanted = set(args.tasks)
        tasks = [task for task in tasks if task["task_id"] in wanted]
    if not tasks:
        raise SystemExit("No matching tasks")
    if args.force:
        for task in tasks:
            for algo in args.algos:
                for name in ("metadata.json", "run.log"):
                    path = output_root / task["task_id"] / algo / name
                    if path.exists():
                        path.unlink()

    jobs = [(task, algo) for task in tasks for algo in args.algos]
    print(
        f"Running {len(jobs)} jobs with {args.workers} workers; CPU limit={args.timelimit}s; "
        f"output={output_root.relative_to(ROOT).as_posix()}/",
        flush=True,
    )
    failures = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                run_one,
                task,
                algo,
                args.timelimit,
                args.hard_timeout,
                args.memory,
                args.heap,
                skip_existing=not (args.force or args.rerun),
                output_root=output_root,
            ): (task["task_id"], algo)
            for task, algo in jobs
        }
        done = 0
        for future in concurrent.futures.as_completed(futures):
            done += 1
            task_id, algo = futures[future]
            try:
                result = future.result()
                print(
                    f"[{done}/{len(jobs)}] {task_id} {algo}: rc={result['returncode']} wall={result['wall_seconds']}s",
                    flush=True,
                )
            except Exception as exc:
                failures += 1
                print(
                    f"[{done}/{len(jobs)}] {task_id} {algo}: HOST ERROR {exc!r}",
                    flush=True,
                )
    if failures:
        raise SystemExit(f"{failures} jobs failed at the host level")


if __name__ == "__main__":
    main()
