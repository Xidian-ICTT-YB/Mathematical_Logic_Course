#!/usr/bin/env bash
# Print the real execution environment inside the project container.
set -euo pipefail
source /work/scripts/container_env.sh
echo "container_uname: $(uname -srm)"
echo "container_arch: $(uname -m)"
echo "os_release:"
grep -E "^(PRETTY_NAME|VERSION_ID)=" /etc/os-release
echo "workdir: $(pwd)"
test -d /work && echo "work_mount: present"
echo "clang: $(/opt/llvm7/bin/clang --version | head -n1)"
echo "z3: $("$PYTHON" -c "import z3; print(z3.get_version_string())")"
echo "klee: $(/work/build/klee-original/bin/klee --version 2>&1 | head -n1)"
echo "ubitect: $(/work/build/ubitect-original/ubitect --version 2>&1 | head -n2 | tail -n1 | sed 's/^ *//')"
