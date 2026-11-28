# Historical harness mapping: `xgene_ahci_probe`

## Scope

This is a **function-level historical reproduction**, not a full-kernel build and
not a hardware run.  The complete body of `xgene_ahci_probe()` is copied
byte-for-byte from the two upstream driver files:

- vulnerable parent: `8ba559fd09bcf4e87faad3efa465dacf04c076c9`
- official fix: `8134233e8d346aaa1c929dc510e75482ae318bce`

The copies under `source/` retain the original GPL-2.0-or-later header.  The
generated files in `harness/` use `#line 750 "drivers/ata/ahci_xgene.c"` so the
target line numbers remain 825 (H1) and 824 (H2), exactly as in the upstream
driver.

The build selects only the real historical function and supplies the kernel
interfaces it calls.  No uninitialized read is added by the harness.  The only
driver-level change between H1 and H2 is the official two-line `else if` patch.

## Target source

H1, vulnerable parent:

```c
struct acpi_device_info *info;
...
status = acpi_get_object_info(ACPI_HANDLE(&pdev->dev), &info);
if (ACPI_FAILURE(status)) {
        ...
        version = XGENE_AHCI_V1;
}
if (info->valid & ACPI_VALID_CID)   /* line 825 */
        version = XGENE_AHCI_V2;
```

H2, official fix:

```c
} else if (info->valid & ACPI_VALID_CID) {  /* line 824 */
        version = XGENE_AHCI_V2;
}
```

On `ACPI_FAILURE`, the official fix skips the `info->valid` test.  The kernel
commit message states the interface behavior: if `acpi_get_object_info()` fails,
`info` has not been initialized.  The failure branch is therefore the target
path; the harness does not claim that a successful call leaves `info`
uninitialized.

## Stub table

| Kernel/API item | Harness model | Why / evidence |
|---|---|---|
| `struct platform_device`, `struct device` | Small addressable structs; `pdev->dev` address is passed | The driver only needs the `&pdev->dev` address for the ACPI path |
| `ahci_platform_get_resources` | Returns one static `ahci_host_priv` | Models a successful resource lookup; target is not resource failure |
| `devm_kzalloc` | Returns one static `xgene_ahci_context` | Models successful allocation |
| `platform_get_resource` | Returns a static resource for indices 1–3; NULL for optional index 4 | Mirrors “three required + optional mux absent” |
| `devm_ioremap_resource` | Returns a non-error pointer | Resource error paths are not the target |
| `of_match_device` | Returns NULL | Forces the ACPI branch that contains the historical bug |
| `acpi_match_device` | Returns an ACPI ID with `driver_data == XGENE_AHCI_V2` | The `else if (acpi_id->driver_data)` branch must execute |
| `acpi_get_object_info` | In the target build: returns `AE_ERROR` and does not write `*out`.  In the non-target model branch: success writes `global_info`, failure does not | The kernel commit message explicitly identifies failure as leaving `info` uninitialized; the official patch guards the read |
| `ACPI_HANDLE` | Reads the harness's ACPI-handle selector | The real driver passes an ACPI handle; the harness reduces it to a scalar input |
| `ACPI_FAILURE` | `status != 0` | ACPI status convention used by the source |
| `xgene_ahci_mux_select` | Returns 0 | SATA mux success is not the target |
| `xgene_ahci_is_memram_inited` | Returns 1 | Takes the documented `skip_clk_phy` path; not the target |
| clock/resource/host helpers | Return success or no-op | Avoid unrelated failure paths and extra UBI candidates |
| `dev_*` logging | No-op variadic stub | Logging is irrelevant to the target |
| `struct acpi_device_info` | `{ unsigned int valid; unsigned int reserved; }` | Only `valid` is read.  The second field prevents LLVM from merging this named struct with an unrelated one-field stub |

## Explicit target input range

The historical reproduction run compiles with `-DHISTORY_ACPI_FAILURE_ONLY`.
In that build, `acpi_get_object_info()` returns `AE_ERROR` and does **not**
write `*out`.  This selects the already-known failure input range; it does not
add a read or an initialization.  The success/failure implementation is kept in
the source under the non-target branch and in the mapping above, so the output
parameter semantics remain visible.

A full success/failure variant was also built and executed as a diagnostic.  It
showed that a join-block warning can be confirmed on the success path even when
`info` is initialized; that confirmation is **not** treated as evidence for the
historical UBI.  The target run therefore uses the failure range.

## KLEE entry point

The warning-producing function remains the real `xgene_ahci_probe`.  KLEE needs
an entry point that supplies the ACPI-failure input, so the candidate guidance
copy sets only:

```text
"function": "history_entry_failure"
```

`history_entry_failure()` sets the failure selector and calls the real probe.
The real `use` block, blacklist and whitelist are unchanged.  The raw warning
JSON remains beside the copy.

## Not claimed

- No Linux kernel was booted or built.
- No X-Gene SATA hardware, ACPI firmware, scheduler, or interrupt path was run.
- The successful and failing ACPI API behavior is an interface model, backed by
  the upstream commit message and the source control flow, not a full kernel
  implementation.
- A SAT model is a model of this harness, not proof of a real-world crash or
  exploit.
