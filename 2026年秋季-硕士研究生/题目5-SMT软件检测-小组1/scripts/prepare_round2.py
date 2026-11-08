#!/usr/bin/env python3
"""Run on the user's Ubuntu VM. Preserve round 1 and prepare round 2 only."""
# Path用于文件路径操作。
from pathlib import Path
# csv读写任务清单；以下glob匹配文件，hashlib校验源码，random抽样，shutil复制，ET处理XML。
import csv
import glob
import hashlib
import random
import shutil
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

# 项目根目录：以Ubuntu当前用户主目录为起点。
base = Path.home() / 'smt-project'
# 固定svcomp16的c目录；数据版本应核对标签及提交号。
data = base / 'benchmarks/sv-comp16/c'
# 历史输入依赖：读取已有30任务清单及四份-30.xml，不读取此前验证成绩。
old = base / 'results/formal-20261012-145215'
# 记录工具路径；此变量在本准备脚本后续未使用，保留原样。
cpa = base / 'downloads/supplements-vstte/CPAchecker'
# 固定配置输出目录；已有目录不会覆盖。
out = base / 'experiment/round2-50-900s'
# 重复执行会停止：原脚本就是此行为，不要为录屏删除原目录。
if out.exists():
    raise SystemExit('Output directory already exists; nothing overwritten: ' + str(out))
# 读取原30任务清单，保留字段顺序；新环境必须提供这些前置输入。
with (old / 'tasks.csv').open(newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    rows = list(reader)
# 检查30任务数量、20安全10不安全和无重复。assert在python -O模式下失效。
assert len(rows) == 30
assert Counter(r['expected'] for r in rows) == {'TRUE': 20, 'FALSE': 10}
assert len({r['program'] for r in rows}) == 30
# 核对已有任务源码、SHA256和属性文件，确保输入一致。
for row in rows:
    p = data / row['program']
    assert p.is_file(), p
    assert hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256'], p
    assert (data / row['specification']).is_file(), row['specification']

# 保存已有程序路径，抽样时排除重复。
used = {r['program'] for r in rows}
# 候选集合去重；下面从类别set定义收集实际文件。
candidates = set()
# 读取类别规则，每行可含文件通配符。
for line in (data / 'DeviceDriversLinux64.set').read_text().splitlines():
    pattern = line.strip()
    if pattern and not pattern.startswith('#'):
        candidates.update(Path(n) for n in glob.glob(str(data / pattern)) if Path(n).is_file())
# 独立伪随机生成器，固定种子20261013；相同抽样还要求相同数据及代码。
rng = random.Random(20261013)
# 按安全/不安全文件名标记抽取指定数量，按目录分组后轮流取。
def pick(marker, count):
    # 每个来源目录一个候选列表。
    groups = defaultdict(list)
    # 先排序，再按标签筛选并排除旧任务。
    for p in sorted(candidates):
        if marker in p.name and p.relative_to(data).as_posix() not in used:
            groups[p.parent.name].append(p)
    # 确保候选足够。
    assert sum(map(len, groups.values())) >= count
    # 打乱各目录内部顺序。
    for ps in groups.values():
        rng.shuffle(ps)
    # 准备保存本次新增选中的任务。
    selected = []
    # 每轮从仍有候选的目录各取一个，直到达到数量。
    while len(selected) < count:
        # 先排序目录名，再随机打乱目录轮次顺序。
        names = sorted(n for n, ps in groups.items() if ps)
        rng.shuffle(names)
        for n in names:
            # pop取出并移除候选，避免组内重复。
            selected.append(groups[n].pop())
            if len(selected) == count:
                break
    return selected

# 增加15个安全任务和5个不安全任务，与原30个合为35安全15不安全。
added = [(p, 'TRUE') for p in pick('_true-unreach-call', 15)]
added += [(p, 'FALSE') for p in pick('_false-unreach-call', 5)]
# 为新增任务记录编号、相对路径、标签、大小和SHA256。
for p, expected in added:
    spec = p.parent / 'ALL.prp'
    assert spec.is_file(), spec
    # T%02d生成T31等编号；这里是多行字典构造。
    rows.append(dict(task_id='T%02d' % (len(rows) + 1),
                     program=p.relative_to(data).as_posix(),
                     specification=spec.relative_to(data).as_posix(),
                     expected=expected, source_group=p.parent.name,
                     size_bytes=str(p.stat().st_size),
                     sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
# 检查最终数量和程序唯一性，不根据验证结果筛选。
assert len(rows) == 50 and len({r['program'] for r in rows}) == 50
assert Counter(r['expected'] for r in rows) == {'TRUE': 35, 'FALSE': 15}
# 四种算法名称，也对应XML文件名前缀。
names = ['bmc', 'k-induction', 'predicate', 'impact']
# 暂存修改后的四份XML。
trees = {}
# 从历史配置继承算法参数，再统一设置本次资源预算。
for name in names:
    root = ET.parse(old / (name + '-30.xml')).getroot()
    # CPU软限制900秒，硬限制1000秒，总内存5000MB，每任务2核。
    root.set('timelimit', '900 s')
    root.set('hardtimelimit', '1000 s')
    root.set('memlimit', '5000 MB')
    root.set('cpuCores', '2')
    # 查找且要求唯一的-heap选项；设为3000M，堆不等于任务总内存。
    heap_options = [n for n in root.findall('option') if n.get('name') == '-heap']
    assert len(heap_options) == 1
    heap_options[0].text = '3000M'
    # 遍历副本以安全移除旧tasks节点，不改算法选项。
    for node in list(root):
        if node.tag == 'tasks': root.remove(node)
    # BenchExec使用每个输入程序目录里的ALL.prp。
    root.find('propertyfile').text = '${inputfile_path}/ALL.prp'
    # 新建固定50任务集合，添加-64机器模型和各任务绝对路径。
    group = ET.SubElement(root, 'tasks', {'name': 'drivers50'})
    ET.SubElement(group, 'option', {'name': '-64'})
    # 核对已有任务源码、SHA256和属性文件，确保输入一致。
    for row in rows:
        ET.SubElement(group, 'include').text = str(data / row['program'])
    trees[name] = root

# Validate a pre-existing smoke task; do not select it based on round-2 results.
# 读取既有单任务试跑路径，不用本轮运行成绩选择试跑任务。
smoke_program = Path((base / 'results/driver-smoke/program.txt').read_text().strip())
assert smoke_program.is_file() and (smoke_program.parent / 'ALL.prp').is_file()
# 复制BMC配置作为试跑配置，避免修改正式BMC配置。
smoke = ET.fromstring(ET.tostring(trees['bmc']))
# 试跑CPU软限制60秒，硬限制100秒；内存设置继承本次正式配置。
smoke.set('timelimit', '60 s')
smoke.set('hardtimelimit', '100 s')
# 把试跑任务集合替换为单个既有任务。
group = smoke.find('tasks')
group.set('name', 'smoke')
for node in list(group):
    if node.tag == 'include': group.remove(node)
ET.SubElement(group, 'include').text = str(smoke_program)

# 全部准备检查通过后才创建目录。
out.mkdir(parents=True)
# 输出最终50任务CSV，保留原表头。
with (out / 'tasks.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
# 保存原30任务输入清单，属于抽样溯源，不是第一次结果统计。
shutil.copy2(old / 'tasks.csv', out / 'round1-tasks.csv')
# 写入抽样与资源说明；字符串中的\n表示换行。
(out / 'sampling.txt').write_text(
    'Round 2: retain T01-T30 exactly; append T31-T45 safe and T46-T50 unsafe.\n'
    'Addition seed=20261013; directory-round-robin; no selection by runtime.\n'
    'Expected verdicts are historical filename labels, not measured results.\n'
    '50 tasks; CPU soft=900s; hard=1000s; total memory=5000MB; Java heap=3000M; cores=2.\n',
    encoding='utf-8')
# 保存四份正式算法-50.xml。
for name, root in trees.items():
    ET.ElementTree(root).write(out / (name + '-50.xml'), encoding='utf-8', xml_declaration=True)
# 另存bmc-smoke.xml：这里只生成配置，不执行试跑。
ET.ElementTree(smoke).write(out / 'bmc-smoke.xml', encoding='utf-8', xml_declaration=True)
# 把当前准备脚本复制到输出目录归档。
shutil.copy2(Path(__file__), out / 'prepare_round2.py')
# 打印准备完成、任务标签数量和来源统计；没有启动验证器。
print('Prepared:', out)
print('Expected verdicts:', dict(Counter(r['expected'] for r in rows)))
print('Source directories:', dict(Counter(r['source_group'] for r in rows)))
print('T01-T30 preserved; checksums verified. No experiments started.')
