#!/usr/bin/env bash
# setup_esbmc.sh
# 根据 README 中的运行建议实现的自动化脚本：
# 1. 检查 ESBMC 是否可用，如缺失则尝试通过 apt 安装；
# 2. 确保 code/run_all.sh 可执行；
# 3. 执行 run_all.sh，输出日志到 logs/。

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_SCRIPT="${PROJECT_ROOT}/code/run_all.sh"

ensure_esbmc() {
  if [[ -n "${ESBMC:-}" && -x "${ESBMC}" ]]; then
    echo "[setup] ESBMC provided via \$ESBMC: ${ESBMC}"
    return
  fi

  if command -v esbmc >/dev/null 2>&1; then
    echo "[setup] ESBMC already available: $(command -v esbmc)"
    return
  fi

  echo "[setup] ESBMC not found, attempting to install via apt (requires network & sudo)."
  if command -v sudo >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y esbmc
  else
    apt-get update
    apt-get install -y esbmc
  fi

  if ! command -v esbmc >/dev/null 2>&1; then
    echo "[setup] ERROR: ESBMC installation failed or esbmc not on PATH."
    exit 1
  fi
  echo "[setup] ESBMC installed: $(command -v esbmc)"
}

run_all() {
  if [[ ! -x "${RUN_SCRIPT}" ]]; then
    echo "[setup] run_all.sh missing or not executable, fixing perms."
    chmod +x "${RUN_SCRIPT}"
  fi

  echo "[setup] Running ESBMC suite via ${RUN_SCRIPT}"
  bash "${RUN_SCRIPT}"
}

ensure_esbmc
run_all
