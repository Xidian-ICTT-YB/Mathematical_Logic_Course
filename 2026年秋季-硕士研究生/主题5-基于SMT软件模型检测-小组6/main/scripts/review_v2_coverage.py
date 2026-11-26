"""Audit downloaded 200-run evidence against paper XML without modifying sources."""
import collections
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from v2_evidence import parse_log

ROOT = Path(__file__).resolve().parents[1]
ALGS = ['bmc', 'k-induction', 'predicateAnalysis', 'impact']


def normalize(status):
    # Coarse outcome classes only; preserve raw resource/diagnostic evidence.
    if status in ('true', 'SAFE'):
        return 'SAFE'
    if status.startswith('false') or status == 'UNSAFE':
        return 'UNSAFE'
    if status.startswith('TIMEOUT'):
        return 'TIMEOUT'
    if status in ('MEMORY_LIMIT', 'JAVA_MEMORY_ERROR', 'NATIVE_MEMORY_ERROR') or 'MEMORY' in status:
        return 'MEMORY_FAILURE'
    if status.upper() == 'UNKNOWN':
        return 'UNKNOWN'
    return 'ERROR'


def save_new(path, data):
    content = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    if path.exists():
        if path.read_text() != content:
            raise ValueError('Refusing overwrite: ' + str(path))
    else:
        with path.open('x') as f:
            f.write(content)


def main():
    batch = ROOT / 'experiment-v2/evidence/v2-20261113-125655-b19929'
    rows = json.loads((batch / 'results.json').read_text())
    schedule = json.loads((batch / 'schedule.json').read_text())
    assert (batch / 'COMPLETE').exists() and len(rows) == len(schedule) == 200
    assert [r['entry'] for r in rows] == schedule
    assert len({(e['task'], e['algorithm']) for e in schedule}) == 200
    assert len({e['task'] for e in schedule}) == 50
    original = {}
    for a in ALGS:
        path = ROOT / ('third_party/supplements-vstte/results/' + a + '.DeviceDriversLinux64.xml')
        for e in ET.parse(path).getroot().findall('run'):
            name = e.get('name', '')
            if '/ldv-' not in name:
                continue
            task = 'ldv-' + name.split('/ldv-', 1)[1]
            original[(task, a)] = {c.get('title'): c.get('value') for c in e.findall('column')}
    comparisons = []
    for i, r in enumerate(rows, 1):
        e = r['entry']
        result_file = batch / ('%03d' % i) / 'result.json'
        assert json.loads(result_file.read_text()) == r
        log = result_file.parent / Path(r['log']).parent.name / 'run.log'
        text = log.read_text(errors='replace')
        parsed = parse_log(text, r['exit_code'], r['runner_stop_reason'])
        paper = original[(e['task'], e['algorithm'])]
        evidence = [dict(line=n, text=l) for n, l in enumerate(text.splitlines(), 1)
                    if re.search(r'^Error:|Exception|Unsupported feature \(recursion\)|feasibility could not be verified|conflicting function declarations|OutOfMemory', l)]
        comparisons.append(dict(entry=e, expected=r['expected'], actual=r['status'],
            reparsed_status=parsed['status'], paper_status=paper['status'],
            actual_coarse=normalize(r['status']), paper_coarse=normalize(paper['status']),
            coarse_match=normalize(r['status']) == normalize(paper['status']),
            cpu_seconds=r['cpa_cpu_seconds'], paper_cpu=paper.get('cputime'),
            local_log=str(log.relative_to(ROOT)), diagnostics=evidence))
    out = ROOT / 'experiment-v2/review-coverage-20261114'
    out.mkdir(exist_ok=True)
    save_new(out / 'comparison200.json', comparisons)
    summary = dict(count=200, tasks=50, counts=dict(collections.Counter(r['status'] for r in rows)),
        coarse_matches=sum(c['coarse_match'] for c in comparisons),
        paper_solved=sum(c['paper_coarse'] in ('SAFE', 'UNSAFE') for c in comparisons),
        retained_paper_solved=sum(c['paper_coarse'] in ('SAFE', 'UNSAFE') and c['actual_coarse'] == c['paper_coarse'] for c in comparisons),
        new_solved=sum(c['actual_coarse'] in ('SAFE', 'UNSAFE') and c['paper_coarse'] not in ('SAFE', 'UNSAFE') for c in comparisons),
        contradict_expected=sum(r['wrong_result'] for r in rows),
        contradict_paper=sum(c['actual_coarse'] in ('SAFE', 'UNSAFE') and c['paper_coarse'] in ('SAFE', 'UNSAFE') and c['actual_coarse'] != c['paper_coarse'] for c in comparisons),
        wall_hours=sum(r['wall_seconds'] for r in rows)/3600,
        parser_disagreements=sum(c['actual'] != c['reparsed_status'] for c in comparisons))
    save_new(out / 'summary.json', summary)
    hashes = {str(p.relative_to(batch)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(batch.rglob('*')) if p.is_file()}
    save_new(out / 'local-evidence-sha256.json', hashes)
    lines = ['# 50任务软件模型检测实验结果', '',
             '本报告记录50个程序在四种配置下的200次正式实验。', '',
             '50个任务、四配置、200条记录唯一且顺序完整，逐次结果与汇总一致。', '',
             '|配置|SAFE|UNSAFE|TIMEOUT|RSS内存限制|Java堆错误|ERROR|UNKNOWN|',
             '|---|---:|---:|---:|---:|---:|---:|---:|']
    for a in ALGS:
        counts = collections.Counter(r['status'] for r in rows if r['entry']['algorithm'] == a)
        lines.append('|' + a + '|' + '|'.join(str(counts[k]) for k in ['SAFE','UNSAFE','TIMEOUT','MEMORY_LIMIT','JAVA_MEMORY_ERROR','ERROR','UNKNOWN']) + '|')
    lines += ['', '## 论文对照', '',
              '按粗分类比较，有%d/200条一致。该口径合并不同内存失败和不同工具错误，表示结果类别一致程度，不是成功求解率。' % summary['coarse_matches'],
              '论文在本子集上有%d条确定判定，本次保留其中%d条，另新增%d条确定判定。' % (summary['paper_solved'], summary['retained_paper_solved'], summary['new_solved']),
              '与预期标签矛盾%d条，与论文确定判定相反%d条。详细状态和证据见 comparison200.json。' % (summary['contradict_expected'], summary['contradict_paper']),
              '', '## 未完成结果的解释', '',
              '工具报错不等于被验证程序存在缺陷。日志中的递归、并行辅助分析异常及反例检查失败应逐项保留，不强行归为一个唯一根因。内存限制采用进程组RSS轮询，不与论文的资源测量严格等价。UNKNOWN候选反例未经确认，不能计为UNSAFE。',
              '', '## 结论边界', '',
              '四配置成功数量为7、11、15、15；不同程序的完成情况不能代替同任务耗时比较。每个程序—配置组合只运行一次，不支持统计显著性结论，也不能推断全部50个任务的重复运行稳定性。',
              '本文件以50个任务的200次正式记录为统计依据。目录说明和核验入口见[总README](../../README.md)，案例补充记录不计入本表。']
    report = out / '覆盖实验分析.md'
    content = '\n'.join(lines) + '\n'
    if report.exists():
        assert report.read_text() == content
    else:
        with report.open('x') as f:
            f.write(content)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print('Local evidence files:', len(hashes))
    print('Report:', report)
    for c in comparisons:
        if c['actual'] == 'ERROR' and not any('Unsupported feature (recursion)' in e['text'] for e in c['diagnostics']):
            print('OTHER_ERROR', c['entry'], c['diagnostics'][-3:])


if __name__ == '__main__':
    main()
