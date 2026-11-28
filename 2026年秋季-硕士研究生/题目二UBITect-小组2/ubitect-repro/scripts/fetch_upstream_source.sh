#!/usr/bin/env bash
# Optional provenance check: fetch exactly the pinned upstream commit into a
# new directory and verify HEAD.  The delivery builds from the shipped
# snapshot; this script is for independently confirming its origin.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
PIN="fb97a1554f6fc3a5e8b35f680a8bfe2b82a79848"
URL="https://github.com/seclab-ucr/UBITect.git"
DEST="${1:-$ROOT/source/UBITect-upstream}"

command -v git >/dev/null 2>&1 || { echo "FATAL: git is required" >&2; exit 2; }
test ! -e "$DEST" || { echo "FATAL: destination already exists: $DEST" >&2; exit 3; }

mkdir -p "$DEST"
git -C "$DEST" init -q
git -C "$DEST" remote add origin "$URL"
echo "fetching $PIN from $URL"
git -C "$DEST" fetch --depth 1 origin "$PIN"
git -C "$DEST" checkout -q FETCH_HEAD

ACTUAL="$(git -C "$DEST" rev-parse HEAD)"
test "$ACTUAL" = "$PIN" || {
    echo "FATAL: fetched HEAD $ACTUAL, expected $PIN" >&2
    exit 4
}
echo "commit: $ACTUAL"
git -C "$DEST" log -1 --format='date: %ci%nsubject: %s'
echo "files: $(git -C "$DEST" ls-tree -r --name-only HEAD | wc -l | tr -d ' ')"
echo "fetched tree: $DEST"
echo "note: this checkout is not used by the tested build; the shipped snapshot is."
