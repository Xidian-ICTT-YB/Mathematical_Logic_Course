# Source this inside the Linux/amd64 container.  All interpreter, cache and
# native-library paths are derived from the mounted project, never hard-coded
# to another machine.
export HOME="/work/.home-linux"
export UV_CACHE_DIR="/work/.uv-cache-linux"
export UV_PYTHON_INSTALL_DIR="/work/.uv-python-linux"
export UV_PYTHON_BIN_DIR="/work/.uv-bin-linux"
export UV_TOOL_DIR="/work/.uv-tools-linux"
export UV_TOOL_BIN_DIR="/work/.uv-bin-linux"

export VENV="/work/.venv-linux"
export PYTHON="$VENV/bin/python"
export Z3_DIR="$("$PYTHON" -c 'import z3, pathlib; print(pathlib.Path(z3.__file__).parent)')"
export Z3_INCLUDE_DIRS="$Z3_DIR/include"
export Z3_LIBRARIES="$Z3_DIR/lib/libz3.so"
export LD_LIBRARY_PATH="$Z3_DIR/lib:/opt/llvm7/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PATH="$VENV/bin:/opt/llvm7/bin:$PATH"
