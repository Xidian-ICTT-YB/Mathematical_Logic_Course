#!/usr/bin/env python3
"""Select the original SV-COMP 2016 driver tasks used in this reproduction."""

from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SV16 = ROOT / "benchmarks" / "sv-comp16" / "c"
OUT = ROOT / "benchmarks" / "tasks.csv"

# (directory, unique filename fragment, short name, expected verdict)
SELECTIONS = [
    *[
        ("ldv-linux-3.4-simple", token, name, "true")
        for token, name in [
            ("apei--einj", "einj"),
            ("acpi--bgrt", "bgrt"),
            ("acpi--container", "container"),
            ("acpi--ec_sys", "ec_sys"),
            ("acpi--fan", "fan"),
            ("hwmon--gpio-fan", "gpio_fan"),
            ("paride--bpck", "bpck"),
            ("paride--epat", "epat"),
            ("paride--epia", "epia"),
            ("paride--kbic", "kbic"),
            ("arcnet--com20020_cs", "com20020_cs"),
            ("power--max8903_charger", "max8903"),
            ("touchscreen--touchright", "touchright"),
            ("video--vfb", "vfb"),
            ("masters--matrox_w1", "matrox_w1"),
            ("rtc--rtc-v3020", "rtc_v3020"),
        ]
    ],
    *[
        ("ldv-linux-3.0", token, name, "true")
        for token, name in [
            ("net-pppox", "pppox"),
            ("net-sis900", "sis900"),
            ("misc-c2port-core", "c2port"),
            ("tablet-kbtab", "kbtab"),
            ("video-msp3400", "msp3400"),
            ("serial-ir-usb", "ir_usb"),
            # The SV-COMP 2016 DeviceDriversLinux64.set uses *.i for this directory.
        ]
    ],
    ("ldv-linux-3.4-simple", "capi--kernelcapi", "kernelcapi", "false"),
    ("ldv-linux-3.4-simple", "p54--p54usb", "p54usb", "false"),
    ("ldv-linux-3.4-simple", "libfc--libfc", "libfc", "false"),
    ("ldv-linux-3.4-simple", "usb--storage--usb-storage", "usb_storage", "false"),
    ("ldv-linux-3.4-simple", "vhost--vhost_net", "vhost_net", "false"),
    (
        "ldv-commit-tester",
        "main0_false-unreach-call_drivers-media-video-tlg2300-poseidon",
        "poseidon",
        "false",
    ),
]


def choose_source(directory: str, token: str, expected: str) -> Path:
    # SV-COMP 2016 benchmark-definition file c/DeviceDriversLinux64.set lists
    # ldv-linux-3.0/*.i (preprocessed) but ldv-linux-3.4-simple/*.c and
    # ldv-commit-tester/*.c. Respect those extensions so every selected task
    # is literally a member of the DeviceDriversLinux64 set.
    suffix = ".i" if directory == "ldv-linux-3.0" else ".c"
    candidates = []
    for path in (SV16 / directory).glob(f"*{suffix}"):
        name = path.name
        if token not in name or f"{expected}-unreach-call" not in name:
            continue
        if (
            directory == "ldv-linux-3.4-simple"
            and expected == "true"
            and not name.startswith("32_1_")
        ):
            continue
        candidates.append(path)
    if len(candidates) != 1:
        raise RuntimeError(
            f"Expected one source for {directory}/{token}/{expected}, got {candidates}"
        )
    return candidates[0]


def main() -> None:
    rows = []
    for index, (directory, token, short_name, expected) in enumerate(SELECTIONS, 1):
        source = choose_source(directory, token, expected)
        task_id = f"T{index:02d}_{short_name}"
        text = source.read_text(encoding="utf-8", errors="replace")
        loop_count = len(re.findall(r"\b(?:while|for)\s*\(", text))
        rows.append(
            {
                "task_id": task_id,
                "short_name": short_name,
                "category": directory,
                "source_file": str(source.relative_to(ROOT)),
                "expected_verdict": expected,
                "loop_keywords": loop_count,
                "source_lines": text.count("\n") + 1,
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            }
        )
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} tasks to {OUT}")
    print(
        f"Safe: {sum(r['expected_verdict'] == 'true' for r in rows)}, bugs: {sum(r['expected_verdict'] == 'false' for r in rows)}"
    )
    for row in rows:
        print(
            f"{row['task_id']}: expected={row['expected_verdict']}, loops={row['loop_keywords']}, lines={row['source_lines']}"
        )


if __name__ == "__main__":
    main()
