#!/usr/bin/env bash
# Build the author's pass, both analyzer modes, and the KLEE pair.
# Intended to run inside the linux/amd64 container.
set -euo pipefail

ROOT="${ROOT:-/work}"
SRC="${UBITECT_SOURCE:-$ROOT/source/UBITect}"
cd "$ROOT"
source "$ROOT/scripts/container_env.sh"
FORCE="${FORCE_BUILD:-0}"
mkdir -p "$ROOT/logs" "$ROOT/build/bbtag" "$ROOT/build/ubitect-original" \
    "$ROOT/build/ubitect-nodedup" "$ROOT/build/klee-original"

log() { printf '\n[build_all] %s\n' "$*"; }

# 1. Author's basic-block renaming pass, compiled against prebuilt LLVM 7.
BBTAG_SRC="$SRC/llvm/llvm.src/projects/BBTag/bbTag/bbTag.cpp"
BBTAG_OUT="$ROOT/build/bbtag/bbTaglib.so"
if [[ "$FORCE" == 1 || ! -f "$BBTAG_OUT" || "$BBTAG_SRC" -nt "$BBTAG_OUT" ]]; then
    log "building bbTaglib.so"
    /opt/llvm7/bin/clang++ -std=c++14 -fno-rtti -fPIC -shared \
        $(llvm-config --cxxflags) "$BBTAG_SRC" -o "$BBTAG_OUT"
else
    log "bbTaglib.so up to date"
fi
/opt/llvm7/bin/opt -load "$BBTAG_OUT" -help >/dev/null 2>&1

# 2. UBITect, original report dedup and explicit no-dedup teaching build.
COMMON_CMAKE=(
    -S "$SRC/src"
    -DCMAKE_BUILD_TYPE=Release
    -DLLVM_DIR=/opt/llvm7/lib/cmake/llvm
    -DCMAKE_C_COMPILER=/opt/llvm7/bin/clang
    -DCMAKE_CXX_COMPILER=/opt/llvm7/bin/clang++
    -DCMAKE_C_FLAGS_RELEASE=-O2
    -DCMAKE_EXE_LINKER_FLAGS=-L/opt/llvm7/lib
)
log "building original UBITect"
cmake "${COMMON_CMAKE[@]}" \
    -B "$ROOT/build/ubitect-original" \
    -DCMAKE_CXX_FLAGS_RELEASE="-std=c++14 -fno-rtti -fPIC -O2 -D__builtin_is_constant_evaluated=__is_constant_evaluated"
cmake --build "$ROOT/build/ubitect-original" --parallel 2

log "building no-dedup teaching UBITect"
cmake "${COMMON_CMAKE[@]}" \
    -B "$ROOT/build/ubitect-nodedup" \
    -DCMAKE_CXX_FLAGS_RELEASE="-std=c++14 -fno-rtti -fPIC -O2 -DUBITECT_NO_DEDUP -D__builtin_is_constant_evaluated=__is_constant_evaluated"
cmake --build "$ROOT/build/ubitect-nodedup" --parallel 2

# 3. KLEE pair.  The no-export binary must be built from the pristine encoder.
KLEE_ORIG="$ROOT/build/klee-original/bin/klee.noexport"
KLEE_EXPORT="$ROOT/build/klee-original/bin/klee"
ENC="$SRC/KLEE/klee/lib/Encode/Encode.cpp"
PRISTINE_ENC="$ROOT/patches/Encode.cpp.pristine"

configure_klee() {
    if [[ ! -f "$ROOT/build/klee-original/CMakeCache.txt" ]]; then
        cmake -S "$SRC/KLEE/klee" -B "$ROOT/build/klee-original" \
            -DCMAKE_BUILD_TYPE=Release \
            -DCMAKE_C_COMPILER=/opt/llvm7/bin/clang \
            -DCMAKE_CXX_COMPILER=/opt/llvm7/bin/clang++ \
            -DCMAKE_C_FLAGS="-D__builtin_is_constant_evaluated=__is_constant_evaluated" \
            -DCMAKE_CXX_FLAGS="-D__builtin_is_constant_evaluated=__is_constant_evaluated" \
            -DLLVM_CONFIG_BINARY=/opt/llvm7/bin/llvm-config \
            -DLLVMCC=/opt/llvm7/bin/clang \
            -DLLVMCXX=/opt/llvm7/bin/clang++ \
            -DENABLE_SOLVER_Z3=ON \
            -DENABLE_SOLVER_STP=OFF \
            -DENABLE_TCMALLOC=OFF \
            -DENABLE_UNIT_TESTS=OFF \
            -DENABLE_SYSTEM_TESTS=OFF \
            -DENABLE_DOCS=OFF \
            -DHAVE_Z3_GET_ERROR_MSG_NEEDS_CONTEXT=ON \
            -DZ3_INCLUDE_DIRS="$Z3_INCLUDE_DIRS" \
            -DZ3_LIBRARIES="$Z3_LIBRARIES" \
            -DENABLE_POSIX_RUNTIME=OFF \
            -DENABLE_KLEE_UCLIBC=OFF
    fi
}

build_klee_pair() {
    local backup="$ROOT/build/Encode.with-smt.cpp"
    if [[ "$FORCE" != 1 && -f "$KLEE_ORIG" && -f "$KLEE_EXPORT" ]]; then
        log "KLEE pair up to date (set FORCE_BUILD=1 to rebuild)"
        return 0
    fi
    test -f "$PRISTINE_ENC" || {
        log "FATAL: missing pristine encoder $PRISTINE_ENC"
        return 4
    }

    # The delivered source tree has patch 0003 applied.  Save that encoder,
    # build the preserved no-export binary from the shipped pristine copy, then
    # restore the patched encoder and build the export binary.  No git working
    # tree is required.
    cp "$ENC" "$backup"
    cp "$PRISTINE_ENC" "$ENC"
    cleanup() {
        if [ -f "$backup" ]; then
            cp "$backup" "$ENC"
            touch "$ENC"
        fi
    }
    trap cleanup EXIT

    log "configuring/building pristine KLEE (no SMT dump)"
    configure_klee
    cmake --build "$ROOT/build/klee-original" --parallel 2
    cp "$KLEE_EXPORT" "$KLEE_ORIG"
    chmod 0755 "$KLEE_ORIG"

    cleanup
    trap - EXIT

    log "rebuilding KLEE with environment-gated SMT dump"
    cmake --build "$ROOT/build/klee-original" --parallel 2
    test -f "$KLEE_EXPORT"

    sha256sum "$KLEE_ORIG" "$KLEE_EXPORT" | tee "$ROOT/logs/klee-binaries.sha256"
}
build_klee_pair

log "built binaries"
sha256sum "$BBTAG_OUT" \
    "$ROOT/build/ubitect-original/ubitect" \
    "$ROOT/build/ubitect-nodedup/ubitect" \
    "$KLEE_ORIG" "$KLEE_EXPORT" | tee "$ROOT/logs/binaries.sha256"
