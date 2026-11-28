#!/usr/bin/env bash
# Fetch the two pinned binary dependencies into ./downloads and verify their
# SHA-256 values before Docker is allowed to use them.
#
# UBITECT_DOWNLOAD_CACHE can point at a directory containing already verified
# copies; it is used only when the file's SHA-256 matches the pin.
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
DEST="${UBITECT_DOWNLOAD_DIR:-$ROOT/downloads}"
CACHE="${UBITECT_DOWNLOAD_CACHE:-}"

LLVM_FILE="clang+llvm-7.0.0-x86_64-linux-gnu-ubuntu-16.04.tar.xz"
LLVM_SHA="69b85c833cd28ea04ce34002464f10a6ad9656dd2bba0f7133536a9927c660d2"
LLVM_URL="https://releases.llvm.org/7.0.0/$LLVM_FILE"

# GitHub's release asset name does not contain the version; the local name
# does, so the Dockerfile and the provenance record stay unambiguous.
UV_FILE="uv-x86_64-unknown-linux-gnu-0.13.6.tar.gz"
UV_ASSET="uv-x86_64-unknown-linux-gnu.tar.gz"
UV_SHA="f29c3e94ffabd7e6f3ba521dba169a9b7ec12100bf3257087f0f24f6123f3645"
UV_URL="https://github.com/astral-sh/uv/releases/download/0.13.6/$UV_ASSET"

sha_of() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}

fetch_one() {
    local url="$1" name="$2" sha="$3"
    local dest="$DEST/$name"
    mkdir -p "$DEST"

    if [ -n "$CACHE" ] && [ -f "$CACHE/$name" ]; then
        if [ "$(sha_of "$CACHE/$name")" = "$sha" ]; then
            if [ ! -f "$dest" ] || [ "$(sha_of "$dest")" != "$sha" ]; then
                cp -p "$CACHE/$name" "$dest"
            fi
            echo "$sha  $dest" | (command -v sha256sum >/dev/null 2>&1 && sha256sum -c - || shasum -a 256 -c -)
            echo "from cache: $dest"
            return 0
        fi
        echo "cache entry ignored (sha256 mismatch): $CACHE/$name" >&2
    fi

    if [ -f "$dest" ] && [ "$(sha_of "$dest")" = "$sha" ]; then
        echo "$sha  $dest" | (command -v sha256sum >/dev/null 2>&1 && sha256sum -c - || shasum -a 256 -c -)
        echo "already present: $dest"
        return 0
    fi

    echo "downloading $url"
    rm -f "$dest.part"
    if command -v curl >/dev/null 2>&1; then
        curl -4 -fL --retry 8 --retry-all-errors --connect-timeout 30 \
            --speed-time 120 --speed-limit 1024 -o "$dest.part" "$url"
    elif command -v wget >/dev/null 2>&1; then
        wget -O "$dest.part" "$url"
    else
        echo "FATAL: neither curl nor wget is available" >&2
        return 2
    fi
    if [ "$(sha_of "$dest.part")" != "$sha" ]; then
        echo "FATAL: SHA-256 mismatch for $url" >&2
        echo "  expected $sha" >&2
        echo "  got      $(sha_of "$dest.part")" >&2
        echo "  partial file kept at $dest.part" >&2
        return 3
    fi
    mv "$dest.part" "$dest"
    echo "$sha  $dest" | (command -v sha256sum >/dev/null 2>&1 && sha256sum -c - || shasum -a 256 -c -)
}

fetch_one "$LLVM_URL" "$LLVM_FILE" "$LLVM_SHA"
fetch_one "$UV_URL" "$UV_FILE" "$UV_SHA"
