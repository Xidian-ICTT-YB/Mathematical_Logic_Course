#!/usr/bin/env bash
# Verify the shipped UBITect snapshot against SOURCE_MANIFEST.sha256.
# Run this on a fresh extraction, before prepare_source.sh applies the patches.
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SRC="${UBITECT_SOURCE:-$ROOT/source/UBITect}"
PIN="fb97a1554f6fc3a5e8b35f680a8bfe2b82a79848"

test -d "$SRC" || { echo "FATAL: missing $SRC" >&2; exit 2; }
test -f "$SRC/SOURCE_MANIFEST.sha256" || {
    echo "FATAL: missing $SRC/SOURCE_MANIFEST.sha256" >&2
    exit 3
}
actual="$(tr -d '[:space:]' < "$SRC/UPSTREAM_COMMIT")"
test "$actual" = "$PIN" || {
    echo "FATAL: UPSTREAM_COMMIT=$actual, expected $PIN" >&2
    exit 4
}
echo "source: $SRC"
echo "upstream commit: $actual"
echo "manifest entries: $(wc -l < "$SRC/SOURCE_MANIFEST.sha256" | tr -d ' ')"
if command -v sha256sum >/dev/null 2>&1; then
    if ! ( cd "$SRC" && sha256sum -c --status SOURCE_MANIFEST.sha256 ); then
        ( cd "$SRC" && sha256sum -c SOURCE_MANIFEST.sha256 | grep -v ': OK$' || true )
        echo "FATAL: source manifest verification failed" >&2
        exit 5
    fi
else
    if ! ( cd "$SRC" && shasum -a 256 -c --status SOURCE_MANIFEST.sha256 ); then
        ( cd "$SRC" && shasum -a 256 -c SOURCE_MANIFEST.sha256 | grep -v ': OK$' || true )
        echo "FATAL: source manifest verification failed" >&2
        exit 5
    fi
fi
echo "SOURCE SNAPSHOT: PASS"
