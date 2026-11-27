#!/usr/bin/env python3
"""Extract evidence lines from the four logs of one task."""
import glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(pattern):
    paths = glob.glob(os.path.join(ROOT, "results/logs", f"*{pattern}*.log"))
    for p in sorted(paths):
        algo = p.rsplit("__", 1)[-1][:-4]
        txt = open(p, errors="replace").read()
        print(f"\n===== {algo}: {os.path.basename(p)} =====")
        print("size", len(txt), "chars")
        for pat in [r"CPAchecker [0-9][^\n]*", r"Verification result:[^\n]*",
                    r"Total CPU time for CPAchecker:[^\n]*", r"Total time for CPAchecker:[^\n]*",
                    r"(?i)time limit[^\n]*", r"(?i)OutOfMemory[^\n]*",
                    r"(?i)value of k[^\n]*", r"(?i)\bk\s*=\s*\d+[^\n]*",
                    r"(?i)Refinements:[^\n]*", r"(?i)Number of refinements[^\n]*",
                    r"(?i)forced covering[^\n]*", r"(?i)Number of iterations[^\n]*"]:
            for m in re.finditer(pat, txt):
                line = m.group(0).strip()
                if line:
                    print("  ", line[:200])
    if not paths:
        print("no logs matching", pattern)


if __name__ == "__main__":
    main(sys.argv[1])
