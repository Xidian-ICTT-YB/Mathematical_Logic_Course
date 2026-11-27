#!/usr/bin/env python3
"""Generate Markdown summary tables from results/matrix.csv."""
import csv, json, os, statistics, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALGOS = [("bmc", "BMC"), ("k-induction", "k-induction"), ("predicate", "谓词抽象"), ("impact", "Impact")]
SHORT = {
    "A_agree_safe": "A 一致安全",
    "B_agree_unsafe": "B 一致错误",
    "C2_only_kind": "C2 BMC 失败/k-ind 成功",
    "C4_only_pred_impact": "C4 仅谓词/Impact",
    "C3_only_bmc_unsafe": "C3 仅 BMC",
}


def short_task(t):
    base = os.path.basename(t)
    # take the driver-ish middle part
    for key in ["drivers--", "module_get_put-", "drivers-"]:
        if key in base:
            s = base.split(key, 1)[1]
            s = s.split(".ko")[0]
            return s[:48]
    return base[:48]


def main():
    rows = list(csv.DictReader(open(os.path.join(ROOT, "results/matrix.csv"))))
    lines = []
    lines.append("### 表 1 四算法汇总（22 个任务）\n")
    lines.append("| 算法 | 安全 TRUE | 错误 FALSE | 超时 | 内存耗尽 | 其他不确定 | 正确结论 | 中位 CPU 时间* |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for a, name in ALGOS:
        c = collections.Counter(r[f"run_{a}"] for r in rows)
        conclusive = c["safe"] + c["unsafe"]
        xs = [float(r[f"cpu_{a}"]) for r in rows if r[f"run_{a}"] in ("safe", "unsafe") and r[f"cpu_{a}"]]
        med = f"{statistics.median(xs):.1f}s" if xs else "—"
        lines.append(f"| {name} | {c['safe']} | {c['unsafe']} | {c['timeout']} | {c['memout']} | "
                     f"{c['unknown'] + c['error']} | {conclusive}/22 | {med} |")
    lines.append("\n*CPAchecker 自报 `Total CPU time`，仅统计给出 TRUE/FALSE 的运行；不含容器与 JVM 启动开销。\n")

    lines.append("### 表 2 逐任务结果\n")
    lines.append("| 层 | 任务 | 真值 | BMC | k-ind | 谓词 | Impact |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in rows:
        def cell(a):
            v = r[f"run_{a}"] or "—"
            sym = {"safe": "✓TRUE", "unsafe": "✗FALSE", "timeout": "TO", "memout": "OOM",
                   "unknown": "?", "error": "ERR"}.get(v, v)
            return sym
        lines.append(f"| {SHORT.get(r['bucket'], r['bucket'])} | {short_task(r['task'])} | "
                     f"{'safe' if r['truth']=='true' else 'unsafe'} | {cell('bmc')} | {cell('k-induction')} | "
                     f"{cell('predicate')} | {cell('impact')} |")

    lines.append("\n### 表 3 实测与论文结论对照\n")
    agree = disagree = 0
    details = []
    for r in rows:
        for a, name in ALGOS:
            mv = r[f"run_{a}"]; pv = r[f"paper_{a}"]
            if mv in ("safe", "unsafe") and pv in ("safe", "unsafe"):
                if mv == pv:
                    agree += 1
                else:
                    disagree += 1
                    details.append((short_task(r['task']), name, mv, pv))
    lines.append(f"- 两方都给出结论的运行：{agree + disagree} 次；一致 {agree} 次，冲突 {disagree} 次。")
    for d in details:
        lines.append(f"- 冲突：{d[0]} / {d[1]}：实测 {d[2]}，论文 {d[3]}")
    lines.append("")

    out = os.path.join(ROOT, "results/tables.md")
    open(out, "w").write("\n".join(lines))
    print("\n".join(lines))
    print("\nwrote", out)


if __name__ == "__main__":
    main()
