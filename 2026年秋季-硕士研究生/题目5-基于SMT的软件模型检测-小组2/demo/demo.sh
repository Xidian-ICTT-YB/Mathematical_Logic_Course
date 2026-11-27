#!/usr/bin/env bash
# 工具演示脚本：按步骤运行，录屏时一步一步敲
#   bash demo/demo.sh 1   环境与冒烟测试
#   bash demo/demo.sh 2   s3c-hwmon：BMC 找到错误 + 错误轨迹
#   bash demo/demo.sh 3   npgtech：四种算法对比（BMC 演示时限 30s）
#   bash demo/demo.sh 4   批量实验结果汇总
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CPA="$ROOT/supplements/supplements-vstte/CPAchecker"
BENCH="$ROOT/benchmarks"
OUT="$ROOT/demo/out"
IMAGE="eclipse-temurin:8-jre"

S3C="ldv-commit-tester/m0_false-unreach-call_drivers-hwmon-s3c-hwmon-ko--130_7a--af3071a-1.c"
NPG="ldv-linux-3.4-simple/32_1_cilled_true-unreach-call_ok_nondet_linux-3.4-32_1-drivers--media--rc--keymaps--rc-npgtech.ko-ldv_main0_sequence_infinite_withcheck_stateful.cil.out.c"

BMC=(-bmc -setprop solver.solver=MATHSAT5
     -setprop cpa.predicate.encodeBitvectorAs=BITVECTOR -setprop cpa.predicate.encodeFloatAs=FLOAT
     -setprop analysis.checkCounterexamples=true -setprop counterexample.checker=CBMC
     -setprop cpa.bounds.maxLoopIterationsUpperBound=0 -setprop cpa.bounds.maxLoopIterations=1
     -setprop cpa.bounds.maxLoopIterationAdjusterFactory=INCREMENT)
KIND=(-sv-comp16--k-induction)
PRED=(-predicateAnalysis-PredAbsRefiner-ABEl-bitprecise -setprop cpa.predicate.encodeFloatAs=FLOAT
      -setprop analysis.checkCounterexamples=true -setprop counterexample.checker=CBMC)
IMPACT=(-predicateAnalysis-ImpactRefiner-ABEl-bitprecise -setprop cpa.predicate.encodeFloatAs=FLOAT
        -setprop analysis.checkCounterexamples=true -setprop counterexample.checker=CBMC
        -setprop cpa.forcedCovering=cpa.predicate.PredicateForcedCovering)

title() { printf '\n\033[1;36m==== %s ====\033[0m\n' "$*"; }
key()   { grep -E --color=always "$1" || true; }

# cpa <时限秒> <任务> <输出目录或空> <算法参数...>
cpa() {
  local tl="$1" task="$2" outdir="$3"; shift 3
  local vol=() outopt=(-noout)
  if [ -n "$outdir" ]; then
    mkdir -p "$outdir"; vol=(-v "$outdir:/work"); outopt=(-setprop output.disable=false -setprop output.path=/work/)
  fi
  local dir; dir="$(dirname "$task")"
  printf '\033[2m$ cpa.sh %s -timelimit %ss -spec ALL.prp %s\033[0m\n' "$1" "$tl" "$(basename "$task" | cut -c1-50)..." >&2
  docker run --rm --platform linux/amd64 --memory 6000m --memory-swap 6000m \
    -v "$CPA:/cpa:ro" -v "$BENCH:/bench:ro" ${vol[@]+"${vol[@]}"} -w /cpa "$IMAGE" \
    bash /cpa/scripts/cpa.sh -heap 5000M -64 -timelimit "${tl}s" -stats "${outopt[@]}" "$@" \
    -spec "/bench/c/$dir/ALL.prp" "/bench/c/$task" 2>&1
}

step1() {
  title "1. 运行环境"
  echo "宿主机: $(uname -sm)   Docker: $(docker version --format '{{.Server.Version}}' 2>/dev/null)"
  docker run --rm --platform linux/amd64 "$IMAGE" bash -c 'echo "容器: $(uname -sm)"; java -version 2>&1 | head -1'
  echo "CPAchecker 目录: ${CPA#$ROOT/}"
  echo "任务数: $(ls "$BENCH"/c/*/*.c "$BENCH"/c/*/*.i 2>/dev/null | wc -l | tr -d ' ') 个（benchmarks/c/）"
  title "冒烟测试：BMC + MathSAT5 验证 example-safe.c"
  docker run --rm --platform linux/amd64 -v "$CPA:/cpa:ro" -w /cpa "$IMAGE" \
    bash /cpa/scripts/cpa.sh -heap 2000M -noout "${BMC[@]}" -timelimit 60s -stats \
    -spec config/specification/ErrorLabel.spc test/programs/example-safe.c 2>&1 \
    | key 'CPAchecker [0-9]|MathSAT5 version|Total CPU time for CPAchecker|Verification result'
}

step2() {
  title "2. s3c-hwmon 驱动：BMC 找错误"
  rm -rf "$OUT/s3c"
  cpa 60 "$S3C" "$OUT/s3c" "${BMC[@]}" \
    | key 'Adjusting maxLoopIterations|confirmed by counterexample|Total CPU time for CPAchecker|Verification result'
  title "错误轨迹（Counterexample.1.txt 最后几步）"
  local cx="$OUT/s3c/Counterexample.1.txt"
  [ -f "$cx" ] || cx="$ROOT/results/evidence/Counterexample.1.txt"
  grep -E '^line (1213|1091|974|1278|1369|1371|1374|1297):' "$cx" \
    | sed -E 's/\tN[0-9]+ -\{/  /; s/\}-> N[0-9]+$//' \
    | grep -E --color=always 'ldv_count_[12]|ERROR|__VERIFIER_error|$'
  echo "  此时取值: ldv_count_1 == 0, ldv_count_2 == 1  →  0 >= 1 不成立" 
}

step3() {
  title "3. npgtech 驱动（安全）：四种算法对比"
  title "BMC（演示时限 30s；正式实验为 170s）"
  mkdir -p "$OUT"
  cpa 30 "$NPG" "" "${BMC[@]}" > "$OUT/npg_bmc.log"
  grep -E 'Adjusting maxLoopIterations' "$OUT/npg_bmc.log" | tail -3
  key 'CPU-time limit of 30s has elapsed|Total CPU time for CPAchecker|Verification result' < "$OUT/npg_bmc.log" | sort -u
  title "k-induction"
  cpa 170 "$NPG" "" "${KIND[@]}" | key 'finished successfully|Total CPU time for CPAchecker|Verification result'
  title "谓词抽象"
  cpa 170 "$NPG" "" "${PRED[@]}" | key 'Number of refinements|Total CPU time for CPAchecker|Verification result'
  title "Impact"
  cpa 170 "$NPG" "" "${IMPACT[@]}" | key 'Number of refinements|Total CPU time for CPAchecker|Verification result'
}

step4() {
  title "4. 批量实验：22 个任务 × 4 种算法 = 88 次"
  echo '$ python3 scripts/run_bench.py --timeout 180 --heap 5000 --mem 6000 --workers 1   # 全量约 42 分钟'
  echo "已完成运行记录: $(wc -l < "$ROOT/results/runs.jsonl" | tr -d ' ') 条；日志: $(ls "$ROOT/results/logs" | wc -l | tr -d ' ') 份"
  python3 - "$ROOT/results/matrix.csv" <<'EOF'
import csv, sys, collections
rows = list(csv.DictReader(open(sys.argv[1])))
A = [("bmc", "BMC"), ("k-induction", "k-induction"), ("predicate", "谓词抽象"), ("impact", "Impact")]
import unicodedata
def pad(t, w, right=False):
    n = sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in str(t))
    sp = " " * max(0, w - n)
    return sp + str(t) if right else str(t) + sp
print()
print(pad("算法", 14) + "".join(pad(h, 10, True) for h in ["TRUE", "FALSE", "超时", "内存不足", "正确"]))
for a, name in A:
    c = collections.Counter(r["run_" + a] for r in rows)
    ok = c["safe"] + c["unsafe"]
    print(pad(name, 14) + "".join(pad(v, 10, True) for v in [c["safe"], c["unsafe"], c["timeout"], c["memout"], f"{ok}/22"]))
same = sum(r["run_" + a] == r["paper_" + a] for r in rows for a, _ in A)
print(f"\n与论文结果类别一致: {same}/88")
EOF
}

case "${1:-}" in
  1) step1 ;; 2) step2 ;; 3) step3 ;; 4) step4 ;;
  *) echo "用法: bash demo/demo.sh 1|2|3|4"; exit 1 ;;
esac
