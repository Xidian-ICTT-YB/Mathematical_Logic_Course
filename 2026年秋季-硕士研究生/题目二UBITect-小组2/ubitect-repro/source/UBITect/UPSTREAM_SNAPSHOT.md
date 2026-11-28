# UBITect source snapshot provenance

- Upstream repository: <https://github.com/seclab-ucr/UBITect.git>
- Pinned commit: `fb97a1554f6fc3a5e8b35f680a8bfe2b82a79848`
- Commit date: 2022-10-25 21:42:00 -0700
- Commit subject: `Update FuncProcess.cpp`
- Snapshot created: 2026-11-12 (from a local clone whose `origin` is the URL above)
- Snapshot method: `git archive HEAD | tar -x` of the pinned commit, followed by
  the two normalizations listed below.  The snapshot contains no `.git`
  history.
- Verification: `SOURCE_MANIFEST.sha256` lists every shipped regular file
  except itself.  `scripts/verify_source_snapshot.sh` checks the commit marker
  and the complete manifest; `scripts/prepare_source.sh` performs the same
  check on first use before applying any patch.

## Snapshot normalizations

1. **Case-insensitive filename collision.**  The upstream tree contains both
   `KLEE/klee/README.md` and `KLEE/klee/Readme.md`.  A default macOS
   filesystem cannot store both names.  The snapshot keeps both contents under
   distinct names:
   - `KLEE/klee/README.upstream-KLEE.md` — upstream `README.md`
   - `KLEE/klee/Readme.author.md` — upstream `Readme.md` (author note)

   Neither file participates in the build.  A case-sensitive extraction of the
   upstream commit can compare their hashes with the manifest.
2. **Pristine encoder copy.**  `patches/Encode.cpp.pristine` is a byte-for-byte
   copy of `KLEE/klee/lib/Encode/Encode.cpp` at the pinned commit before patch
   `0003-smt-export-before-check.patch`.  `build_all.sh` uses it to build the
   no-export KLEE binary without requiring a git checkout.

## Patches applied at build time

| Patch | Scope |
|---|---|
| `patches/0001-cmake-object-shared-target.patch` | CMake object/shared target compatibility for the pinned LLVM 7 build |
| `patches/0002-no-dedup-reporting.patch` | Adds the `UBITECT_NO_DEDUP` teaching build; no change to the default path |
| `patches/0003-smt-export-before-check.patch` | Environment-gated SMT dump immediately before KLEE's real `z3_solverr.check()` |

The patches live outside this directory and are applied with `patch -p1`.
`scripts/prepare_source.sh` is idempotent: a fully patched tree is detected by
reverse dry-run and left unchanged.

## Optional upstream fetch

`scripts/fetch_upstream_source.sh [DEST]` performs a shallow fetch of exactly
the pinned commit into a new directory and verifies `HEAD`.  This is an
independent provenance check; the shipped snapshot is the tested build input.
