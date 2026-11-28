# KLEE guidance bridge for the historical harness

## Why a bridge is needed

The author's `Encode::isWarning()` compares the warning instruction text from
`warnings.json` with KLEE's current `Instruction::print()` output.  For the
historical function, KLEE links/loads the module and renumbers some SSA
temporaries; for example UBITect reports:

```text
%137 = load %struct.acpi_device_info*, %struct.acpi_device_info** %13
```

while KLEE's loaded module executes:

```text
%138 = load %struct.acpi_device_info*, %struct.acpi_device_info** %13
```

The path labels and the `use` basic block are unchanged.  The exact-string
comparison fails on the SSA number.  The bridge copies KLEE's logged instruction
spelling, which also carries a `!dbg` suffix; `isWarning()` truncates both sides
at `!`, so that suffix does not participate in matching.  The bridge is applied
to a **copy** of the candidate JSON:

1. preserve raw `warning.json` unchanged;
2. change `"function"` to the harness entry `history_entry_failure`;
3. change the instruction string in `"warning"` to the spelling that KLEE's
   instruction log shows at the same source line and block (SSA number and
   `!dbg` suffix), while preserving the path/use/list fields.

The bridge is calibrated from a real KLEE `-debug-print-instructions=all:file`
run.  It does not change `use`, `whitelist`, `blacklist`, path labels, solver
settings, or the real KLEE invocation.  The authoritative KLEE run still uses
the custom KLEE binary and the original candidate's `use` block.

## Evidence to inspect

- `raw-warning.json` — UBITect's original warning object.
- `klee-warning.json` — the guidance copy with the bridge.
- `klee-bridge.diff` — the exact two-field change.
- `calibration/instructions.txt` — KLEE's own executed-instruction log.
- `klee-original/command.sh` — the real command and warning JSON used.

If the target instruction never appears in calibration, the candidate is not
reached on the failure-only path; no bridge is fabricated for it.  This is why
the H2 candidate has no confirmation and no exported query.

## Important boundary

This bridge is a harness/loader compatibility measure, not the author's original
full-kernel guidance path.  It must be cited whenever this historical case is
discussed.  The result is still a real execution of the author's custom KLEE,
but the SSA-name adjustment is an adaptation to the extracted function module.
