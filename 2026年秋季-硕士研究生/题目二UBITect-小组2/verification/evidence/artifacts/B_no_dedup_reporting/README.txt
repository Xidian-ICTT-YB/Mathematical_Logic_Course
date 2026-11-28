Case B: no_dedup_reporting
Config: teaching build with -DUBITECT_NO_DEDUP; reporting granularity only
Authoritative confirmation run: candidates/*/klee-original (unmodified KLEE binary).
Diagnostic comparison: candidates/*/klee-smt-export (same source plus an
environment-gated dump immediately before the real Z3 check()).
Each candidate directory preserves its own raw confirm_result.json.
The case-level confirm_result.json is the same raw-line concatenation the
author's parallel path_verify.py performs; it is not a rewritten object.
