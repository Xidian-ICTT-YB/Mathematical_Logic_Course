"""Read downloaded repeat evidence; write a separate report and a 200-run plan."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import statistics

ROOT = Path(__file__).resolve().parents[1]
ALGORITHMS = ['bmc', 'k-induction', 'predicateAnalysis', 'impact']


def write_new_or_equal(path, content):
    if path.exists():
        if path.read_text() != content:
            raise ValueError('Refusing to overwrite changed file: ' + str(path))
    else:
        with path.open('x') as f:
            f.write(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', type=Path, default=ROOT / 'experiment-v2/evidence/v2-20261112-165952-5a0340')
    args = parser.parse_args()
    batch = args.batch.resolve()
    rows = json.loads((batch / 'results.json').read_text())
    schedule = json.loads((batch / 'schedule.json').read_text())
    assert (batch / 'COMPLETE').exists() and len(rows) == len(schedule) == 48
    assert [r['entry'] for r in rows] == schedule
    assert len({(e['task'], e['algorithm'], e['repeat']) for e in schedule}) == 48
    groups = collections.defaultdict(list)
    hashes = {}
    metrics = {}
    patterns = {'abstractions': r'^Number of abstractions:\s+(\d+)',
                'predicates': r'^Number of predicates discovered:\s+(\d+)',
                'refinements': r'^Number of successful refinements:\s+(\d+)',
                'forced_cover_attempts': r'^Attempted forced coverings:\s+(\d+)',
                'abstraction_seconds': r'^\s*Time for abstraction:\s+([\d.]+)s'}
    for i, row in enumerate(rows, 1):
        entry = row['entry']
        groups[(entry['task'], entry['algorithm'])].append(row)
        stored = json.loads((batch / ('%03d' % i) / 'result.json').read_text())
        assert stored == row
        logs = list((batch / ('%03d' % i)).glob('attempt-*/run.log'))
        # Use the exact completed attempt, not an interrupted attempt's log.
        attempt_name = Path(row['log']).parent.name
        log = next(p for p in logs if p.parent.name == attempt_name)
        text = log.read_text(errors='replace')
        metrics[str(i)] = {key: re.findall(pattern, text, re.M) for key, pattern in patterns.items()}
    for p in sorted(batch.rglob('*')):
        if p.is_file():
            hashes[str(p.relative_to(batch))] = hashlib.sha256(p.read_bytes()).hexdigest()
    summaries = []
    for (task, a), rs in groups.items():
        assert sorted(r['entry']['repeat'] for r in rs) == [1, 2, 3, 4]
        values = [r['cpa_cpu_seconds'] for r in rs]
        successful = all(r['status'] in ('SAFE', 'UNSAFE') for r in rs)
        summary = dict(task=task, algorithm=a, statuses=[r['status'] for r in rs],
                       stable=len({r['status'] for r in rs}) == 1,
                       cpu_seconds=values)
        if successful and all(v is not None for v in values):
            summary.update(cpu_median=statistics.median(values), cpu_min=min(values), cpu_max=max(values))
        summaries.append(summary)
    counts = collections.Counter(r['status'] for r in rows)
    assert len(groups) == 12
    report = ['# 算法差异案例补充分析', '',
              '本文件保存案例分析使用的补充重复记录，三例四配置各四次，共48次；这些记录不计入50个任务的200次正式统计。', '',
              '48条记录和逐次结果一致，12个任务—配置组合均恰好四次重复。',
              '状态总计：' + '，'.join('%s %d' % item for item in sorted(counts.items())) + '。',
              '四轮判定稳定的组合：%d/12；与标签矛盾的确定判定：%d。' % (sum(s['stable'] for s in summaries), sum(r['wrong_result'] for r in rows)), '',
              '|任务|配置|四轮状态|成功CPU中位数（秒）|成功CPU范围（秒）|',
              '|---|---|---|---:|---|']
    for s in summaries:
        task = 'pcd' if '--paride--pcd.' in s['task'] else 'pata_marvell' if 'pata_marvell' in s['task'] else 'vhost'
        median = '%.3f' % s['cpu_median'] if 'cpu_median' in s else '不适用'
        interval = '%.3f–%.3f' % (s['cpu_min'], s['cpu_max']) if 'cpu_min' in s else '未完成，不作成功耗时比较'
        report.append('|%s|%s|%s|%s|%s|' % (task, s['algorithm'], '/'.join(s['statuses']), median, interval))
    report += ['', '## pcd 内部统计', '',
               '|配置|轮次|抽象次数|谓词数|成功精化|强制覆盖尝试|抽象计时（秒）|',
               '|---|---:|---|---|---|---|---|']
    for i, row in enumerate(rows, 1):
        e = row['entry']
        if '--paride--pcd.' in e['task'] and e['algorithm'] in ('predicateAnalysis', 'impact'):
            m = metrics[str(i)]
            cells = [', '.join(m[k]) or '未报告' for k in patterns]
            report.append('|%s|%d|%s|' % (e['algorithm'], e['repeat'], '|'.join(cells)))
    report += ['', '两种抽象配置均为9700次抽象、8个谓词、1次成功精化，IMPACT强制覆盖尝试为0。IMPACT与谓词抽象的成功CPU中位数比值约1.94。该差异在四轮中持续存在，但不是总体性能排名或统计显著性结论。',
               '', '相同计数不等于相同公式内容和单次操作成本。上述统计反映抽象调用数；进一步的缓存命中与实际布尔抽象次数见[pcd案例分析](../case-analysis.json)。这些证据支持定位耗时差异，但仍不能将全部差距归因于单一配置项，也不能套用其他任务“减少抽象次数所以更快”的解释。',
               '', 'vhost的其他三配置触及15GB进程组RSS监控阈值，不代表服务器物理内存耗尽。RSS轮询、共享页重复计算及CPU计时范围限制保持不变；缺失CPU不填零。',
               '', '本地原始证据见[重复实验批次](../evidence/v2-20261112-165952-5a0340)，JSON里的服务器原路径保持不变。所有原始记录均未改写。']
    out = ROOT / 'experiment-v2/review-repeat-20261113'
    out.mkdir(exist_ok=True)
    for name, obj in [('summary.json', summaries), ('metric-evidence.json', metrics), ('local-evidence-sha256.json', hashes)]:
        write_new_or_equal(out / name, json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    write_new_or_equal(out / '重复实验分析.md', '\n'.join(report) + '\n')
    design = ROOT / 'experiment-v2/design-20261111'
    tasks = json.loads((design / 'tasks50-frozen.json').read_text())
    assert len(tasks) == 50 and len({t['path'] for t in tasks}) == 50
    plan = []
    for i, task in enumerate(tasks):
        shift = i % 4
        for a in ALGORITHMS[shift:] + ALGORITHMS[:shift]:
            plan.append(dict(repeat=1, task=task['path'], algorithm=a))
    assert len(plan) == len({(e['task'], e['algorithm']) for e in plan}) == 200
    write_new_or_equal(design / 'coverage200-schedule.json', json.dumps(plan, indent=2) + '\n')
    print('Validated 48 records and', len(hashes), 'local evidence files.')
    print('Report:', out / '重复实验分析.md')
    print('Prepared independent 200-run schedule; no experiments started.')


if __name__ == '__main__':
    main()
