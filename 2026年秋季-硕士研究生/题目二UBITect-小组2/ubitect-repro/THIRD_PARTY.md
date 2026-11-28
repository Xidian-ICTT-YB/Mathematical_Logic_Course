# Third-party components and licenses

The delivery bundles or downloads the following components.  License texts are
included in the extracted project; paths below are relative to the project
root.

## Bundled source

| Component | Version / commit | License | License file |
|---|---|---|---|
| UBITect | `fb97a1554f6fc3a5e8b35f680a8bfe2b82a79848` | MIT | `source/UBITect/LICENSE.md` |
| KLEE (author's copy) | bundled in UBITect commit | University of Illinois/NCSA | `source/UBITect/KLEE/klee/LICENSE.TXT` |
| LLVM source tree | bundled in UBITect commit | University of Illinois/NCSA | `source/UBITect/llvm/llvm.src/LICENSE.TXT` |
| UBITect example `backlog.c` | UBITect commit | MIT (same repository) | `source/UBITect/LICENSE.md` |
| Linux `ahci_xgene.c` excerpt | commit `8134233e8d346aaa1c929dc510e75482ae318bce` and parent | GPL-2.0 | `history/ahci_xgene/provenance/official-fix.patch`; source excerpt retained for analysis |

## Downloaded binary dependencies

`scripts/fetch_dependencies.sh` downloads and verifies these files into
`downloads/`; they are not committed to the delivery.

| Component | Version | SHA-256 | License |
|---|---|---|---|
| LLVM/Clang prebuilt | 7.0.0, `x86_64-linux-gnu-ubuntu-16.04` | `69b85c833cd28ea04ce34002464f10a6ad9656dd2bba0f7133536a9927c660d2` | University of Illinois/NCSA |
| uv | 0.13.6, `x86_64-unknown-linux-gnu` | `f29c3e94ffabd7e6f3ba521dba169a9b7ec12100bf3257087f0f24f6123f3645` | Apache-2.0 / MIT |

## Container and Python packages

| Component | Version | License |
|---|---|---|
| Ubuntu base image | 24.04 (`linux/amd64`) | Ubuntu package licenses |
| cmake (PyPI wheel) | 3.31.10 | Apache-2.0 |
| z3-solver (PyPI wheel, includes Z3 4.8.8) | 4.8.8.0 | MIT |
| setuptools | 75.8.0 | MIT |
| Python (uv-managed) | 3.12.16 | PSF-2.0 |

The exact wheel hashes are pinned in `requirements-linux.lock`.  Python 3.12.16
is installed by uv into the project-local `.uv-python-linux/`; no system Python
packages are modified.

## Historical harness

`history/ahci_xgene/harness/` is a reduced function-level model of
`xgene_ahci_probe()` from the Linux kernel, with explicit stubs for kernel
interfaces.  It is analysis input, not a kernel build or a hardware driver.
Provenance and the official fix patch are under
`history/ahci_xgene/provenance/`.
