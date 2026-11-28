# ahci_xgene provenance

Official Linux history for the UBITect paper Table 2 row `8134233`:

- fix commit: `8134233e8d346aaa1c929dc510e75482ae318bce`
- parent/vulnerable: `8ba559fd09bcf4e87faad3efa465dacf04c076c9`
- subject: `ata: ahci_xgene: dereferencing uninitialized pointer in probe`
- fix patch: `official-fix.patch`
- source files: `../source/ahci_xgene.*.c` (original GPL-2.0-or-later header retained)
- paper: `source/UBITect/UBITect-FullVersion.pdf`, Table 2 on page 9 of 15;
  row `8134233 inter-procedural Yes`
- exact hashes, URLs and retrieval time: `SOURCE_LOCK.json`

The vulnerable parent contains `if (info->valid & ...)` after the
`acpi_get_object_info()` failure branch.  The fix changes the second test to
`} else if (info->valid & ...) {` and moves the closing brace.  The experiment
does not infer the bug merely from the patch: H1 is compiled, analyzed, KLEE-run
and SMT-replayed; H2 is run with the same stubs, settings and input range.
