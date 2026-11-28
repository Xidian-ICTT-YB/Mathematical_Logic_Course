#!/usr/bin/env bash
# Verify the pinned UBITect source snapshot and apply the documented patches
# idempotently.  Runs inside the linux/amd64 container (or any Linux host).
#
# The delivery ships a source snapshot (no .git).  The upstream commit is
# recorded in source/UBITect/UPSTREAM_COMMIT and every shipped file is listed
# in source/UBITect/SOURCE_MANIFEST.sha256.  A user who fetched the upstream
# repository with scripts/fetch_upstream_source.sh can instead point
# UBITECT_SOURCE at that checkout; in that case HEAD is checked as well.
set -euo pipefail

ROOT="${ROOT:-/work}"
SRC="${UBITECT_SOURCE:-$ROOT/source/UBITect}"
PIN="fb97a1554f6fc3a5e8b35f680a8bfe2b82a79848"
PATCHES=(
    "$ROOT/patches/0001-cmake-object-shared-target.patch"
    "$ROOT/patches/0002-no-dedup-reporting.patch"
    "$ROOT/patches/0003-smt-export-before-check.patch"
)

test -d "$SRC" || { echo "FATAL: source directory missing: $SRC" >&2; exit 2; }

if [ -d "$SRC/.git" ]; then
    actual="$(git -C "$SRC" rev-parse HEAD)"
    test "$actual" = "$PIN" || {
        echo "FATAL: UBITect HEAD is $actual, expected $PIN" >&2
        exit 3
    }
    echo "upstream checkout HEAD: $actual"
else
    test -f "$SRC/UPSTREAM_COMMIT" || {
        echo "FATAL: $SRC is neither a git checkout nor a marked snapshot" >&2
        exit 2
    }
    actual="$(tr -d '[:space:]' < "$SRC/UPSTREAM_COMMIT")"
    test "$actual" = "$PIN" || {
        echo "FATAL: snapshot commit is $actual, expected $PIN" >&2
        exit 3
    }
    echo "upstream snapshot commit: $actual"
fi

# Decide whether the tree is pristine or already patched before touching it.
# A pristine tree is verified against the full snapshot manifest.  If every
# patch is already applied, the manifest intentionally no longer matches the
# three patched files; do not fail a rerun.  A partially patched tree is not
# accepted silently: the per-patch check below will stop it.
ALL_APPLIED=1
NONE_APPLIED=1
for patch in "${PATCHES[@]}"; do
    test -f "$patch" || { echo "FATAL: missing $patch" >&2; exit 4; }
    if ! patch -p1 -d "$SRC" --reverse --dry-run --silent < "$patch" >/dev/null 2>&1; then
        ALL_APPLIED=0
    fi
    if ! patch -p1 -d "$SRC" --forward --dry-run --silent < "$patch" >/dev/null 2>&1; then
        NONE_APPLIED=0
    fi
done

if [ "$NONE_APPLIED" = "1" ] && [ -f "$SRC/SOURCE_MANIFEST.sha256" ]; then
    echo "verifying full pristine source snapshot manifest"
    if command -v sha256sum >/dev/null 2>&1; then
        ( cd "$SRC" && sha256sum -c "$SRC/SOURCE_MANIFEST.sha256" )
    else
        ( cd "$SRC" && shasum -a 256 -c "$SRC/SOURCE_MANIFEST.sha256" )
    fi
elif [ "$ALL_APPLIED" = "0" ] && [ -f "$SRC/SOURCE_MANIFEST.sha256" ]; then
    echo "WARNING: source tree is partially patched; skipping full manifest check" >&2
fi

for patch in "${PATCHES[@]}"; do
    if patch -p1 -d "$SRC" --reverse --dry-run --silent < "$patch" >/dev/null 2>&1; then
        echo "already applied: $(basename "$patch")"
    elif patch -p1 -d "$SRC" --forward --dry-run --silent < "$patch" >/dev/null 2>&1; then
        patch -p1 -d "$SRC" --forward --silent < "$patch"
        echo "applied: $(basename "$patch")"
    else
        echo "FATAL: neither applies nor is already applied: $patch" >&2
        echo "The source tree is in an unexpected state; compare it with SOURCE_MANIFEST.sha256." >&2
        exit 5
    fi
done

{
    echo "source=$SRC"
    echo "commit=$PIN"
    for patch in "${PATCHES[@]}"; do
        if command -v sha256sum >/dev/null 2>&1; then
            ps="$(sha256sum "$patch" | awk '{print $1}')"
        else
            ps="$(shasum -a 256 "$patch" | awk '{print $1}')"
        fi
        printf 'patch_sha256=%s  %s\n' "$ps" "$(basename "$patch")"
    done
    echo "prepared_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} | tee "$ROOT/logs/source-status.txt"
