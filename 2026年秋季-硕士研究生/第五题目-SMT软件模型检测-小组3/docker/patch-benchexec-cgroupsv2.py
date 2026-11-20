import importlib.metadata
from pathlib import Path
import benchexec.cgroupsv2 as cgroupsv2

version = importlib.metadata.version("benchexec")

if version != "3.26":
    raise SystemExit("Unexpected BenchExec version: " + version)

path = Path(cgroupsv2.__file__)
source = path.read_text(encoding="utf-8")

old = (
    '                if parent_limit != "max":\n'
    '                    limit = min(limit, int(parent_limit))\n'
)

new = (
    '                if parent_limit != "max":\n'
    '                    parent_limit = int(parent_limit)\n'
    '                    limit = parent_limit if limit is None else min(limit, parent_limit)\n'
)

if source.count(old) != 1:
    raise SystemExit(
        "Expected original code exactly once; found "
        + str(source.count(old))
    )

patched = source.replace(old, new, 1)
path.write_text(patched, encoding="utf-8")

verified = path.read_text(encoding="utf-8")

if verified.count(new) != 1 or old in verified:
    raise SystemExit("Patch verification failed")

print("PATCH_APPLIED")
print("BENCH_EXEC_VERSION:", version)
print("PATCHED_SOURCE:", path)
print("NONE_HANDLING: VERIFIED")