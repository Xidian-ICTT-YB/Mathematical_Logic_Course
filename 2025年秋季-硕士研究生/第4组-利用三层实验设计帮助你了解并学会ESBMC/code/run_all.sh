#!/usr/bin/env bash
# 一键运行所有 ESBMC 示例，按 Level 输出日志到 logs/ 目录。
# 用法：在仓库根目录执行 `bash code/run_all.sh`，需保证 esbmc 在 PATH 中。

set -u

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs"
ESBMC_BIN="${ESBMC:-esbmc}"

if ! command -v "${ESBMC_BIN}" >/dev/null 2>&1; then
  # 若未在 PATH 中，回退到本仓库内置的构建产物。
  if [[ -x "${PROJECT_ROOT}/esbmc/build/src/esbmc/esbmc" ]]; then
    ESBMC_BIN="${PROJECT_ROOT}/esbmc/build/src/esbmc/esbmc"
  else
    echo "ERROR: esbmc not found. Set ESBMC=/path/to/esbmc or add to PATH." >&2
    exit 127
  fi
fi

mkdir -p "${LOG_DIR}"

run_case() {
  local label="$1"
  shift
  local log_file="${LOG_DIR}/${label}.log"

  echo ">>> Running ${label}"
  (
    cd "${PROJECT_ROOT}"
    "${@}"
  ) &> "${log_file}"
  local status=$?
  if [[ ${status} -eq 0 ]]; then
    echo "    [PASS] see ${log_file}"
  else
    echo "    [FAIL] see ${log_file} (bug 示例失败属预期)"
  fi
}

echo "===== Level 1: 入门示例 ====="
run_case level1_array_bounds_bug \
  "${ESBMC_BIN}" code/level1/level1_array_bounds.c --unwind 5 \
  --no-unwinding-assertions
run_case level1_array_bounds_safe \
  "${ESBMC_BIN}" code/level1/level1_array_bounds.c --unwind 5 \
  --no-unwinding-assertions -DUSE_SAFE_VERSION

run_case level1_integer_overflow_bug \
  "${ESBMC_BIN}" code/level1/level1_integer_overflow.c --unwind 25 \
  --no-unwinding-assertions --overflow-check --timeout 10
run_case level1_integer_overflow_safe \
  "${ESBMC_BIN}" code/level1/level1_integer_overflow.c --unwind 25 \
  --no-unwinding-assertions --overflow-check --timeout 10 -DUSE_SAFE_VERSION

run_case level1_null_pointer_bug \
  "${ESBMC_BIN}" code/level1/level1_null_pointer.c
run_case level1_null_pointer_safe \
  "${ESBMC_BIN}" code/level1/level1_null_pointer.c -DUSE_SAFE_VERSION

echo "===== Level 2: 循环与动态内存 ====="
run_case level2_linked_list_bug \
  "${ESBMC_BIN}" code/level2/level2_linked_list_memory.c --memory-leak-check \
  --unwind 4 --no-unwinding-assertions
run_case level2_linked_list_safe \
  "${ESBMC_BIN}" code/level2/level2_linked_list_memory.c --memory-leak-check \
  --unwind 4 --no-unwinding-assertions -DUSE_SAFE_VERSION

run_case level2_loop_logic_bug \
  "${ESBMC_BIN}" code/level2/level2_loop_logic.c --unwind 10 \
  --no-unwinding-assertions
run_case level2_loop_logic_safe \
  "${ESBMC_BIN}" code/level2/level2_loop_logic.c --unwind 10 \
  --no-unwinding-assertions -DUSE_SAFE_VERSION

echo "===== Level 3: 并发与环境建模 ====="
run_case level3_concurrency_race_bug \
  "${ESBMC_BIN}" code/level3/level3_concurrency_race.c --context-bound 2 \
  --unwind 5 --no-unwinding-assertions
run_case level3_concurrency_race_safe \
  "${ESBMC_BIN}" code/level3/level3_concurrency_race.c --context-bound 2 \
  --unwind 5 --no-unwinding-assertions -DUSE_SAFE_VERSION

run_case level3_environment_model_bug \
  "${ESBMC_BIN}" code/level3/level3_environment_model.c --unwind 6 \
  --no-unwinding-assertions --k-step 1
run_case level3_environment_model_safe \
  "${ESBMC_BIN}" code/level3/level3_environment_model.c --unwind 6 \
  --no-unwinding-assertions --k-step 1 -DUSE_SAFE_VERSION

echo "===== 完成，查看 logs/ 下的 *.log 了解每个示例的 trace ====="
