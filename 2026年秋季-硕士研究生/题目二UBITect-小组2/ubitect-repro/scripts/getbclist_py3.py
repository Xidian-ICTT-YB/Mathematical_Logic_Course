#!/usr/bin/env python3
"""Python 3 replacement for the author's getbclist.py.

The original file has Python-2 mixed indentation.  This wrapper invokes the
same author pass (bbTaglib.so, option -bbtag) and produces the same two
artifacts: renamed .bc modules and bitcode.list.  It does not alter the
analysis or the pass.
"""
import argparse
import os
import pathlib
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--llvm-dir", default="/opt/llvm7")
    parser.add_argument(
        "--plugin",
        default="/work/build/bbtag/bbTaglib.so",
        help="author bbTaglib.so built from llvm/llvm.src/projects/BBTag",
    )
    parser.add_argument("--workdir", default=os.getcwd())
    args = parser.parse_args()

    workdir = pathlib.Path(args.workdir).resolve()
    opt = pathlib.Path(args.llvm_dir) / "bin" / "opt"
    plugin = pathlib.Path(args.plugin).resolve()
    if not opt.is_file():
        print(f"missing opt: {opt}", file=sys.stderr)
        return 2
    if not plugin.is_file():
        print(f"missing bbTaglib.so: {plugin}", file=sys.stderr)
        return 2

    llbc_files = sorted(workdir.rglob("*.llbc"))
    if not llbc_files:
        print(f"no .llbc files under {workdir}", file=sys.stderr)
        return 3

    for src in llbc_files:
        dst = src.with_suffix(".bc")
        if dst.exists():
            dst.unlink()
        # Pass paths relative to workdir.  LLVM's opt uses the input argument
        # as the module name, and bbTag embeds that name in every basic-block
        # label; relative names keep labels readable and independent of where
        # the project is mounted.
        src_arg = str(src.relative_to(workdir))
        dst_arg = str(dst.relative_to(workdir))
        cmd = [str(opt), "-load", str(plugin), "-bbtag", src_arg, "-o", dst_arg]
        print("+", " ".join(cmd), flush=True)
        proc = subprocess.run(cmd, cwd=workdir)
        if proc.returncode != 0:
            print(f"bbTag opt failed with exit {proc.returncode}", file=sys.stderr)
            return proc.returncode
        if not dst.is_file() or dst.stat().st_size == 0:
            print(f"bbTag produced no output: {dst}", file=sys.stderr)
            return 4

    bc_files = sorted(workdir.rglob("*.bc"))
    with (workdir / "bitcode.list").open("w", encoding="utf-8") as out:
        for path in bc_files:
            if "timeconst.bc" in str(path):
                continue
            out.write(str(path.resolve()) + "\n")

    if not (workdir / "bitcode.list").read_text().strip():
        print("bitcode.list is empty", file=sys.stderr)
        return 5
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
