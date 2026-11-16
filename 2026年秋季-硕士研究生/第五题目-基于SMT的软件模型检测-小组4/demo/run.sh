#!/usr/bin/env bash
# VSTTE 2016 四算法复现实验 —— 一键运行入口
#
# 用法（在任意目录下均可执行，路径自动定位）：
#   bash demo/run.sh check     环境自检
#   bash demo/run.sh setup     幂等准备（镜像 / 补充包 / 源码 / 任务清单）
#   bash demo/run.sh smoke     冒烟测试（8 次运行，写入 demo/smoke_results/，不碰正式结果）
#   bash demo/run.sh full      正式实验（112 次运行 + 统计 + 报告）
#   bash demo/run.sh report    仅重新生成统计表与报告（不跑 CPAchecker）
#
# 可调环境变量：
#   WORKERS=3  TIMELIMIT=90  HARD_TIMEOUT=400  MEMORY=1800  HEAP=1400
#   RERUN=1      全部重跑（默认跳过已有结果，保护现有交付物）
#   DRY_RUN=1    只打印将执行的命令，不真正运行
#
# 例：
#   WORKERS=2 MEMORY=2400 HEAP=1800 bash demo/run.sh full
#   RERUN=1 bash demo/run.sh full
#   DRY_RUN=1 bash demo/run.sh full
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
IMAGE="cpachecker-vstte:java8"
SUPP_URL="https://www.sosy-lab.org/research/k-ind-compare/supplements-vstte.tar.bz2"
SV16_URL="https://gitlab.com/sosy-lab/benchmarking/sv-benchmarks.git"

WORKERS="${WORKERS:-3}"
TIMELIMIT="${TIMELIMIT:-90}"
HARD_TIMEOUT="${HARD_TIMEOUT:-400}"
MEMORY="${MEMORY:-1800}"
HEAP="${HEAP:-1400}"
SMOKE_OUT="demo/smoke_results"
SMOKE_TASKS=(T02_bgrt T23_kernelcapi)

log() { printf '\n\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[WARN]\033[0m %s\n' "$*" >&2; }
die() {
	printf '\033[1;31m[ERROR]\033[0m %s\n' "$*" >&2
	exit 1
}

run() {
	printf '\033[0;36m$ %s\033[0m\n' "$*"
	if [ "${DRY_RUN:-0}" != "1" ]; then "$@"; fi
}

# ---------- setup ----------
do_setup() {
	log "检查 Docker"
	command -v docker >/dev/null 2>&1 || die "未找到 docker，请先安装并启动 Docker Desktop / OrbStack"
	docker info >/dev/null 2>&1 || die "Docker 守护进程未就绪，请先启动 Docker Desktop / OrbStack"
	command -v git >/dev/null 2>&1 || die "未找到 git"
	command -v "$PYTHON" >/dev/null 2>&1 || die "未找到 python3"

	if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
		log "构建 amd64 + OpenJDK 8 实验镜像"
		run docker build --platform linux/amd64 -t "$IMAGE" scripts/docker
	else
		log "镜像已存在：$IMAGE"
	fi

	if [ ! -d benchmarks/supplements-vstte/CPAchecker ]; then
		log "按需下载并解压论文官方补充材料（不保留压缩包）"
		if [ "${DRY_RUN:-0}" != "1" ]; then
			printf '\033[0;36m$ curl -L --fail --retry 2 %s | tar -xj -C benchmarks\033[0m\n' "$SUPP_URL"
			curl -L --fail --retry 2 "$SUPP_URL" | tar -xj -C benchmarks
		fi
	else
		log "补充材料已就绪"
	fi

	if [ ! -d benchmarks/sv-comp16/c ]; then
		log "稀疏检出 SV-COMP 2016 驱动源码（避免下载几十 GB）"
		run git clone --depth 1 --branch svcomp16 --filter=blob:none --sparse \
			"$SV16_URL" benchmarks/sv-comp16
		run git -C benchmarks/sv-comp16 sparse-checkout set --skip-checks \
			c/properties/unreach-call.prp c/ldv-linux-3.0 c/ldv-linux-3.4-simple c/ldv-commit-tester
	else
		log "sv-comp16 源码已就绪"
	fi

	if [ ! -f benchmarks/unreach-call.prp ]; then
		log "写入 unreach-call 规约"
		if [ "${DRY_RUN:-0}" != "1" ]; then
			printf 'CHECK( init(main()), LTL(G ! call(__VERIFIER_error())) )\n' >benchmarks/unreach-call.prp
		fi
	fi

	if [ ! -f benchmarks/tasks.csv ]; then
		log "生成 28 个任务清单"
		run "$PYTHON" scripts/select_tasks.py
	else
		log "任务清单已存在（$("$PYTHON" -c 'import csv;print(len(list(csv.DictReader(open("benchmarks/tasks.csv")))))') 个任务）"
	fi
}

# ---------- check ----------
do_check() {
	log "环境自检"
	local ok=1
	check_item() {
		if eval "$2" >/dev/null 2>&1; then
			printf '  [OK]   %s\n' "$1"
		else
			printf '  [MISS] %s\n' "$1"
			ok=0
		fi
	}
	check_item "Docker 守护进程" "docker info"
	check_item "镜像 $IMAGE" "docker image inspect $IMAGE"
	check_item "CPAchecker 1.6.8-vstte" "test -f benchmarks/supplements-vstte/CPAchecker/scripts/cpa.sh"
	check_item "MathSAT5 原生库" "test -f benchmarks/supplements-vstte/CPAchecker/lib/java/runtime/libmathsat5j.so"
	check_item "unreach-call 规约" "test -f benchmarks/unreach-call.prp"
	check_item "任务清单 tasks.csv" "test -f benchmarks/tasks.csv"
	check_item "sv-comp16 源码" "test -d benchmarks/sv-comp16/c/ldv-linux-3.4-simple"
	check_item "批处理脚本" "test -f scripts/run_experiments.py"
	[ "$ok" = "1" ] || die "自检未通过，请先执行：bash demo/run.sh setup"

	log "容器内平台核验"
	local arch
	arch="$(docker run --rm --platform linux/amd64 -v "$ROOT:/work" -w /work \
		ubuntu:20.04 uname -m 2>/dev/null)" || die "无法启动 linux/amd64 容器，请检查 Docker 是否支持多架构"
	printf '  uname -m = %s\n' "$arch"
	[ "$arch" = "x86_64" ] || die "容器架构为 $arch（应为 x86_64），MathSAT5 将无法加载"
	log "自检完成"
}

# ---------- smoke ----------
do_smoke() {
	do_setup
	log "冒烟测试：2 个任务 × 4 种算法 = 8 次运行，单次 CPU 时限 60s"
	log "输出目录：$SMOKE_OUT/ （与正式 results/ 完全隔离）"
	run "$PYTHON" scripts/run_experiments.py \
		--tasks "${SMOKE_TASKS[@]}" \
		--algos BMC kInduction Predicate Impact \
		--workers 2 --timelimit 60 --hard-timeout 240 \
		--memory 1400 --heap 1000 \
		--output-root "$SMOKE_OUT" --rerun

	[ "${DRY_RUN:-0}" = "1" ] && return 0

	log "冒烟结果摘要"
	"$PYTHON" - <<'PY'
from pathlib import Path
import re, sys
d = Path("demo/smoke_results")
verdicts = {}
cex = 0
for p in sorted(d.glob("T*/*/run.log")):
    t = p.read_text(errors="replace")
    m = re.search(r"^Verification result:\s*(TRUE|FALSE|UNKNOWN)", t, re.M)
    v = m.group(1) if m else "NO_LINE"
    if v == "UNKNOWN":
        v = "TIMEOUT" if "CPU-time limit" in t and "has elapsed" in t else "UNKNOWN"
    verdicts[f"{p.parent.parent.name}/{p.parent.name}"] = v
    cex += len(list(p.parent.glob("Counterexample.1.txt")))
for k, v in verdicts.items():
    print(f"  {k:28s} {v}")
got = set(verdicts.values())
print(f"\n  判定种类: {sorted(got)}  反例文件: {cex}")
expected = {"TRUE", "FALSE", "TIMEOUT"}
if not expected.issubset(got):
    print("  [WARN] 未同时观察到 TRUE / FALSE / TIMEOUT，请检查上方日志")
else:
    print("  [PASS] 环境可用：安全证明、缺陷反例、BMC 超时三类结果均已复现")
PY
	log "正式 results/ 未被改动（冒烟输出只在 $SMOKE_OUT/）"
}

# ---------- full ----------
do_full() {
	do_setup
	# 用分支而非空数组：macOS 自带 bash 3.2 在 set -u 下展开空数组会报错
	log "正式实验：28 任务 × 4 算法 = 112 次运行"
	log "参数：workers=$WORKERS timelimit=${TIMELIMIT}s hard_timeout=${HARD_TIMEOUT}s memory=${MEMORY}m heap=${HEAP}m"
	warn "预计 25–45 分钟；期间请勿关闭 Docker。可用 DRY_RUN=1 先看命令。"
	if [ "${RERUN:-0}" = "1" ]; then
		warn "RERUN=1：将重新运行全部 112 次，覆盖 results/ 下的 run.log 与 metadata.json"
		run "$PYTHON" scripts/run_experiments.py \
			--workers "$WORKERS" --timelimit "$TIMELIMIT" \
			--hard-timeout "$HARD_TIMEOUT" --memory "$MEMORY" --heap "$HEAP" \
			--output-root results --rerun
	else
		log "默认增量模式：已存在结果的运行会被跳过（保护现有交付物）"
		log "若要从头完整重跑，请使用：RERUN=1 bash demo/run.sh full"
		run "$PYTHON" scripts/run_experiments.py \
			--workers "$WORKERS" --timelimit "$TIMELIMIT" \
			--hard-timeout "$HARD_TIMEOUT" --memory "$MEMORY" --heap "$HEAP" \
			--output-root results
	fi

	[ "${DRY_RUN:-0}" = "1" ] && return 0
	do_report
}

# ---------- report ----------
do_report() {
	log "重新生成统计表 / 反例摘录 / 实验报告"
	run "$PYTHON" scripts/parse_results.py
	run "$PYTHON" scripts/make_trace_excerpt.py
	run "$PYTHON" scripts/build_report.py
	[ "${DRY_RUN:-0}" = "1" ] && return 0

	"$PYTHON" - <<'PY'
import json
from pathlib import Path
p = Path("results/summary_detail.json")
if not p.exists():
    print("  [WARN] 尚无 results/summary_detail.json")
else:
    rows = {(r["task_id"], r["algorithm"]): r for r in json.loads(p.read_text())}
    cases = [("T02_bgrt", "kInduction", "TRUE"), ("T23_kernelcapi", "Predicate", "FALSE")]
    for t, a, want in cases:
        got = rows.get((t, a), {}).get("verdict")
        flag = "OK" if got == want else "WARN"
        print(f"  [{flag}] 报告案例 {t}/{a}: {got} (期望 {want})")
        if got != want:
            print("        报告中该案例的叙述基于原始结果，请用 --tasks 单独复跑该任务或检查日志")
PY
	log "交付物：results/summary.csv, results/summary.md, report/实验复现报告.md"
}

# ---------- main ----------
case "${1:-}" in
check) do_check ;;
setup) do_setup ;;
smoke) do_smoke ;;
full) do_full ;;
report) do_report ;;
*)
	cat <<'USAGE'
用法: bash demo/run.sh <check|setup|smoke|full|report>

  check   环境自检（Docker / 镜像 / 补充包 / 源码 / amd64 平台）
  setup   幂等准备环境，已存在的步骤自动跳过
  smoke   冒烟测试：2 任务 × 4 算法，写入 demo/smoke_results/，约 2 分钟
  full    正式实验：112 次运行 + 统计 + 报告，约 25–45 分钟
  report  只重新生成统计表与报告，不运行 CPAchecker

常用：
  bash demo/run.sh check
  bash demo/run.sh smoke
  RERUN=1 bash demo/run.sh full
  WORKERS=2 MEMORY=2400 HEAP=1800 bash demo/run.sh full
  DRY_RUN=1 bash demo/run.sh full     # 只打印命令
USAGE
	exit 1
	;;
esac
