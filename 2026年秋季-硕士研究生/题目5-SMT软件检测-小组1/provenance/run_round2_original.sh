#!/usr/bin/env bash
# Execute after the round-2 resource smoke test passes.
set -euo pipefail
base="$HOME/smt-project"
exp="$base/experiment/round2-50-900s"
cd "$base/downloads/supplements-vstte/CPAchecker"
for algorithm in bmc k-induction predicate impact; do
  test -f "$exp/$algorithm-50.xml"
done
run_dir="$base/results/round2-50-900s-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$run_dir"
cp "$exp/tasks.csv" "$exp/round1-tasks.csv" "$exp/sampling.txt" "$exp/prepare_round2.py" "$run_dir/"
cp "$exp/"*-50.xml "$run_dir/"
cp "$0" "$run_dir/run_round2.sh"
{
  date -Is
  cat /etc/os-release
  uname -a
  java -version
  python3 --version
  benchexec --version
  free -h
  git -C "$base/benchmarks/sv-comp16" rev-parse HEAD
  sha256sum "$run_dir/"*.xml "$run_dir/tasks.csv"
} > "$run_dir/environment.txt" 2>&1
sudo swapoff /swapfile
trap 'sudo swapon /swapfile' EXIT
swapon --show > "$run_dir/swap-during.txt"
if test -s "$run_dir/swap-during.txt"; then
  echo 'Other swap devices are still enabled; stopping before experiments.'
  exit 1
fi
for algorithm in bmc k-induction predicate impact; do
  mkdir -p "$run_dir/$algorithm"
  set +e
  benchexec --no-container --numOfThreads 1 \
    --outputpath "$run_dir/$algorithm/" \
    "$run_dir/$algorithm-50.xml" \
    2>&1 | tee "$run_dir/$algorithm/console.log"
  code=${PIPESTATUS[0]}
  set -e
  if test "$code" -ne 0; then
    echo "BenchExec exited abnormally: $algorithm, code $code. Results: $run_dir"
    exit "$code"
  fi
done
echo "Round 2 complete. Results: $run_dir"
