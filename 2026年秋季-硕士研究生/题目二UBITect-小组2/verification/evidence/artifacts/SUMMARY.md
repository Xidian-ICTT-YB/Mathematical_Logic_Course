# Four-case result summary

| case | candidates (lines) | confirmed, original KLEE | confirmed, SMT-export build |
|---|---|---|---|
| A original_default_dedup | 1 ([25]) | 1 ([25]) | 1 ([25]) |
| B no_dedup_reporting | 2 ([25, 26]) | 2 ([25, 26]) | 2 ([25, 26]) |
| C null_initialization_fix | 0 ([]) | 0 ([]) | 0 ([]) |
| D short_circuit_control | 1 ([25]) | 0 ([]) | 0 ([]) |

`klee-original` means the preserved binary built before the SMT-dump patch.
`klee-smt-export` is the same analysis with an environment-gated dump immediately
before the real Z3 `check()`; confirmation line sets must match.
