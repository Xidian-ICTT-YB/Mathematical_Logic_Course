# Acceptance evidence

- Original acceptance project (historical path): `/Users/kotoriminami/kfc/ubitect-acceptance2-20261112/UBITect_REPRO_DELIVERY/ubitect-repro`
- A-D run ID: `RUN-20261112T075709Z`
- History run ID: `HIST-20261112T075709Z`
- Structure validation: `PASS`
- Expected-result check: `PASS`
- Collected at (UTC): 2026-11-12T08:03:53.363853+00:00

## A-D summary

- **A** `original_default_dedup`: candidates=1 ([25]), confirmed original=[25], export=[25]; note: upstream warningReported() default; unmodified KLEE
- **B** `no_dedup_reporting`: candidates=2 ([25, 26]), confirmed original=[25, 26], export=[25, 26]; note: teaching build with -DUBITECT_NO_DEDUP; reporting granularity only
- **C** `null_initialization_fix`: candidates=0 ([]), confirmed original=[], export=[]; note: source-level control: backlog initialized to NULL
- **D** `short_circuit_control`: candidates=1 ([25]), confirmed original=[], export=[]; note: source-level control: if(a && backlog)

## Historical summary

- Upstream fix commit: `8134233e8d346aaa1c929dc510e75482ae318bce` (parent `8ba559fd09bcf4e87faad3efa465dacf04c076c9`)
- **h1**: candidates=2, target objects=2, confirmed target objects=2, confirmed use points=[825]
- **h2**: candidates=2, target objects=2, confirmed target objects=0, confirmed use points=[]

## Key files

- [ACCEPTANCE.json](./evidence/artifacts/ACCEPTANCE.json) — all expected-result checks
- [A line 25 query.smt2](./evidence/artifacts/A_original_default_dedup/candidates/candidate-01-line-25/klee-smt-export/query.smt2) — real exported query
- [A line 25 z3-replay.json](./evidence/artifacts/A_original_default_dedup/candidates/candidate-01-line-25/klee-smt-export/z3-replay.json) — Z3 replay result/model
- [H1 candidate 1 query.smt2](./evidence/history/ahci_xgene/runs/HIST-20261112T075709Z/h1/candidates/candidate-01-line-825/klee-smt-export/query.smt2) · [H1 candidate 2 query.smt2](./evidence/history/ahci_xgene/runs/HIST-20261112T075709Z/h1/candidates/candidate-02-line-825/klee-smt-export/query.smt2) — H1 queries
- [ENVIRONMENT.json](./ENVIRONMENT.json) — host, image, toolchain, exit codes
- [SHA256SUMS](./SHA256SUMS) — checksums of every collected file
