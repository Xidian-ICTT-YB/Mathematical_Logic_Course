#!/usr/bin/env python3
"""Run on the user's Ubuntu VM. Preserve round 1 and prepare round 2 only."""
from pathlib import Path
import csv
import glob
import hashlib
import random
import shutil
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

base = Path.home() / 'smt-project'
data = base / 'benchmarks/sv-comp16/c'
old = base / 'results/formal-20261012-145215'
cpa = base / 'downloads/supplements-vstte/CPAchecker'
out = base / 'experiment/round2-50-900s'
if out.exists():
    raise SystemExit('Output directory already exists; nothing overwritten: ' + str(out))
with (old / 'tasks.csv').open(newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    rows = list(reader)
assert len(rows) == 30
assert Counter(r['expected'] for r in rows) == {'TRUE': 20, 'FALSE': 10}
assert len({r['program'] for r in rows}) == 30
for row in rows:
    p = data / row['program']
    assert p.is_file(), p
    assert hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256'], p
    assert (data / row['specification']).is_file(), row['specification']

used = {r['program'] for r in rows}
candidates = set()
for line in (data / 'DeviceDriversLinux64.set').read_text().splitlines():
    pattern = line.strip()
    if pattern and not pattern.startswith('#'):
        candidates.update(Path(n) for n in glob.glob(str(data / pattern)) if Path(n).is_file())
rng = random.Random(20261013)
def pick(marker, count):
    groups = defaultdict(list)
    for p in sorted(candidates):
        if marker in p.name and p.relative_to(data).as_posix() not in used:
            groups[p.parent.name].append(p)
    assert sum(map(len, groups.values())) >= count
    for ps in groups.values():
        rng.shuffle(ps)
    selected = []
    while len(selected) < count:
        names = sorted(n for n, ps in groups.items() if ps)
        rng.shuffle(names)
        for n in names:
            selected.append(groups[n].pop())
            if len(selected) == count:
                break
    return selected

added = [(p, 'TRUE') for p in pick('_true-unreach-call', 15)]
added += [(p, 'FALSE') for p in pick('_false-unreach-call', 5)]
for p, expected in added:
    spec = p.parent / 'ALL.prp'
    assert spec.is_file(), spec
    rows.append(dict(task_id='T%02d' % (len(rows) + 1),
                     program=p.relative_to(data).as_posix(),
                     specification=spec.relative_to(data).as_posix(),
                     expected=expected, source_group=p.parent.name,
                     size_bytes=str(p.stat().st_size),
                     sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
assert len(rows) == 50 and len({r['program'] for r in rows}) == 50
assert Counter(r['expected'] for r in rows) == {'TRUE': 35, 'FALSE': 15}
names = ['bmc', 'k-induction', 'predicate', 'impact']
trees = {}
for name in names:
    root = ET.parse(old / (name + '-30.xml')).getroot()
    root.set('timelimit', '900 s')
    root.set('hardtimelimit', '1000 s')
    root.set('memlimit', '5000 MB')
    root.set('cpuCores', '2')
    heap_options = [n for n in root.findall('option') if n.get('name') == '-heap']
    assert len(heap_options) == 1
    heap_options[0].text = '3000M'
    for node in list(root):
        if node.tag == 'tasks': root.remove(node)
    root.find('propertyfile').text = '${inputfile_path}/ALL.prp'
    group = ET.SubElement(root, 'tasks', {'name': 'drivers50'})
    ET.SubElement(group, 'option', {'name': '-64'})
    for row in rows:
        ET.SubElement(group, 'include').text = str(data / row['program'])
    trees[name] = root

# Validate a pre-existing smoke task; do not select it based on round-2 results.
smoke_program = Path((base / 'results/driver-smoke/program.txt').read_text().strip())
assert smoke_program.is_file() and (smoke_program.parent / 'ALL.prp').is_file()
smoke = ET.fromstring(ET.tostring(trees['bmc']))
smoke.set('timelimit', '60 s')
smoke.set('hardtimelimit', '100 s')
group = smoke.find('tasks')
group.set('name', 'smoke')
for node in list(group):
    if node.tag == 'include': group.remove(node)
ET.SubElement(group, 'include').text = str(smoke_program)

out.mkdir(parents=True)
with (out / 'tasks.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
shutil.copy2(old / 'tasks.csv', out / 'round1-tasks.csv')
(out / 'sampling.txt').write_text(
    'Round 2: retain T01-T30 exactly; append T31-T45 safe and T46-T50 unsafe.\n'
    'Addition seed=20261013; directory-round-robin; no selection by runtime.\n'
    'Expected verdicts are historical filename labels, not measured results.\n'
    '50 tasks; CPU soft=900s; hard=1000s; total memory=5000MB; Java heap=3000M; cores=2.\n',
    encoding='utf-8')
for name, root in trees.items():
    ET.ElementTree(root).write(out / (name + '-50.xml'), encoding='utf-8', xml_declaration=True)
ET.ElementTree(smoke).write(out / 'bmc-smoke.xml', encoding='utf-8', xml_declaration=True)
shutil.copy2(Path(__file__), out / 'prepare_round2.py')
print('Prepared:', out)
print('Expected verdicts:', dict(Counter(r['expected'] for r in rows)))
print('Source directories:', dict(Counter(r['source_group'] for r in rows)))
print('T01-T30 preserved; checksums verified. No experiments started.')