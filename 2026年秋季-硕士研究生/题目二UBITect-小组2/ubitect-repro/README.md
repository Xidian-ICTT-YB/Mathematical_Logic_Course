# UBITect backlog.c reproduction (A–D) and historical ahci_xgene case (H1/H2)

This project is a self-contained, source-runnable reproduction of the UBITect
two-stage uninitialized-use analysis on the author's `example/backlog.c`, plus
a function-level historical case from Linux `ahci_xgene.c`.

## What is reproduced

| Case | Source | Expected candidates | Expected confirmed |
|---|---|---|---|
| A | upstream `backlog.c` (default report dedup) | 1 (line 25) | 1 (line 25) |
| B | same source, teaching build `-DUBITECT_NO_DEDUP` | 2 (lines 25, 26) | 2 (lines 25, 26) |
| C | source control: `backlog = NULL` | 0 | 0 |
| D | source control: `if(a && backlog)` | 1 (line 25) | 0 (no target query) |
| H1 | `ahci_xgene.c` before the official fix | 2 target objects | 2 target objects, use point line 825 |
| H2 | same function after the official fix | 2 target objects | 0 target objects, 0 target queries |

A/B/C/D are generated from scratch by the build in this directory.  H1/H2 use
the documented function excerpt and kernel-interface stubs; this is a
function-level under-constrained model, not a kernel build or hardware run.

## Main entry points

| Entry | Purpose |
|---|---|
| `./REPRODUCE_ALL.sh` | Full main flow: A–D from source, then H1/H2, then expected-result checks |
| `./REPRODUCE.sh` | A–D only (also builds the image and toolchain on first use) |
| `./RUN_HISTORY.sh` | H1/H2 only; builds missing tools without touching A–D evidence |
| `./DEMO.sh ...` | Stepwise live demo in one persistent project container |

Run these scripts from this directory. The full reproduction command is
`./REPRODUCE_ALL.sh`. It requires Docker with `linux/amd64` support and
Python 3.9 or later on the host. The saved acceptance results are in
[../verification/RESULTS.md](../verification/RESULTS.md).

## Provenance

- UBITect upstream: <https://github.com/seclab-ucr/UBITect.git>, commit
  `fb97a1554f6fc3a5e8b35f680a8bfe2b82a79848`, shipped as a snapshot under
  `source/UBITect/` with `UPSTREAM_COMMIT`, `UPSTREAM_SNAPSHOT.md` and
  `SOURCE_MANIFEST.sha256`.
- LLVM/Clang 7.0.0 and uv 0.13.6 are fetched by `scripts/fetch_dependencies.sh`
  and pinned by SHA-256.
- The three reproduction patches are in `patches/`; their provenance and scope
  are documented in `patches/README.md`.
- Historical case provenance is in `history/ahci_xgene/provenance/`.

## Generated, not shipped

`build/`, `.venv-linux/`, `.uv-*-linux/`, `downloads/`, `logs/`, `artifacts/`,
`history/ahci_xgene/runs/`, and `demo/` are generated when the scripts run and
are not included in this submission.
