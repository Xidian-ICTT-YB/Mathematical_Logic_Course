#!/usr/bin/env bash
# Create the container-only uv Python environment and record the toolchain.
# Runs *inside* the Linux/amd64 container with /work bind-mounted.
set -euo pipefail

ROOT="${ROOT:-/work}"
cd "$ROOT"

export HOME="$ROOT/.home-linux"
export UV_CACHE_DIR="$ROOT/.uv-cache-linux"
export UV_PYTHON_INSTALL_DIR="$ROOT/.uv-python-linux"
export UV_PYTHON_BIN_DIR="$ROOT/.uv-bin-linux"
export UV_TOOL_DIR="$ROOT/.uv-tools-linux"
export UV_TOOL_BIN_DIR="$ROOT/.uv-bin-linux"
mkdir -p "$HOME" "$UV_CACHE_DIR" "$UV_PYTHON_INSTALL_DIR" "$UV_PYTHON_BIN_DIR"

VENV="$ROOT/.venv-linux"
PYTHON="$VENV/bin/python"

test "$(uname -m)" = "x86_64" || {
    echo "FATAL: expected x86_64 container, got $(uname -m)" >&2
    exit 90
}
test "$(/opt/llvm7/bin/llvm-config --version)" = "7.0.0"
test "$(/opt/llvm7/bin/llvm-config --has-rtti)" = "NO"

if [[ ! -x "$PYTHON" ]]; then
    uv venv --python 3.12.16 "$VENV"
fi

REQUIREMENTS="$ROOT/requirements-linux.lock"
[ -f "$REQUIREMENTS" ] || REQUIREMENTS="$ROOT/requirements-linux.txt"
uv pip install --python "$PYTHON" -r "$REQUIREMENTS"

{
    echo "date=$(date -Is)"
    echo "uname=$(uname -a)"
    echo "arch=$(uname -m)"
    echo "os=$(. /etc/os-release; echo "$PRETTY_NAME")"
    echo "uv=$(uv --version)"
    echo "python=$("$PYTHON" --version 2>&1)"
    echo "python_path=$PYTHON"
    echo "venv=$VENV"
    echo "llvm_config=$(/opt/llvm7/bin/llvm-config --version)"
    echo "llvm_has_rtti=$(/opt/llvm7/bin/llvm-config --has-rtti)"
    echo "llvm_target=$(/opt/llvm7/bin/llvm-config --host-target)"
    echo "clang=$(/opt/llvm7/bin/clang --version | head -1)"
    echo "cmake=$("$VENV/bin/cmake" --version | head -1)"
    echo "cmake_path=$VENV/bin/cmake"
    echo "z3_include=$("$PYTHON" -c 'import z3, pathlib; print(pathlib.Path(z3.__file__).parent / "include")')"
    echo "z3_lib=$("$PYTHON" -c 'import z3, pathlib; print(pathlib.Path(z3.__file__).parent / "lib" / "libz3.so")')"
    echo "z3_version=$("$PYTHON" -c 'import z3; print(z3.get_version_string())')"
    echo "setuptools=$("$PYTHON" -c 'import setuptools; print(setuptools.__version__)')"
} | tee "$ROOT/logs/toolchain-versions.txt"

# Fail early if the pinned Z3 Python API cannot load its shared library.
LD_LIBRARY_PATH="$("$PYTHON" -c 'import z3, pathlib; print(pathlib.Path(z3.__file__).parent / "lib")')" \
    "$PYTHON" -c 'import z3; s=z3.Solver(); s.add(z3.Bool("a")); print(s.check())'
