# Patches

These patches are applied idempotently by `scripts/prepare_source.sh` to the
pinned checkout `fb97a1554f6fc3a5e8b35f680a8bfe2b82a79848`.

| Patch | Scope | Effect |
|---|---|---|
| `0001-cmake-object-shared-target.patch` | `src/lib/CMakeLists.txt` | Removes an unused object-only SHARED target that CMake 3.31 cannot generate a depend rule for. Analysis sources and the static library are unchanged. |
| `0002-no-dedup-reporting.patch` | `src/lib/ConstraintCollect.cpp` | Adds an `#ifdef UBITECT_NO_DEDUP` early return. Used only for the separate teaching binary; the default binary is unchanged. |
| `0003-smt-export-before-check.patch` | `KLEE/klee/lib/Encode/Encode.cpp` | Environment-gated dump of the existing Z3 assertions immediately before the real `check()`. It does not add constraints or alter the result. The original binary is preserved as `build/klee-original/bin/klee.noexport`. |

The upstream checkout also keeps an unrelated case-collision modification to
`KLEE/klee/README.md` caused by macOS's case-insensitive filesystem. It is not
part of these patches and is not used by the build.
