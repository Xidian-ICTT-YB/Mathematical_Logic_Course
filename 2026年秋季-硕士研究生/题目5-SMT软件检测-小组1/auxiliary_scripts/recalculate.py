#!/usr/bin/env python3
# 说明：只用Python标准库重新解析200次正式结果。
"""Recompute the 200 formal results with Python standard library only."""
# Path用于定位材料、输入和输出路径。
from pathlib import Path
# Counter统计每个分类出现的次数。
from collections import Counter
# bz2读取压缩XML；csv处理表格；ET解析XML；statistics在当前脚本中未使用。
import bz2,csv,xml.etree.ElementTree as ET,statistics
# 找到scripts上一级材料根目录。
root=Path(__file__).resolve().parents[1]
# 读取固定50任务清单，按CSV表头转换为字典。
tasks=list(csv.DictReader((root/'data/tasks.csv').open(encoding='utf-8-sig')))
# 确认任务数量为50；请勿使用python3 -O。
assert len(tasks)==50
# 创建空列表，保存之后得到的逐次结果。
records=[]
# 定义分类函数：输入最终status和预期标签，返回独立统计类别。
def classify(status,expected):
    # 最终true：预期TRUE计正确证明，否则计错误安全证明。
    if status=='true':return 'correct_safe' if expected=='TRUE' else 'wrong_safe'
    # 最终false或false(unreach-call)：预期FALSE计正确报警，否则计误报；仅适用于本实验统一属性。
    if status in ['false','false(unreach-call)']:return 'correct_alarm' if expected=='FALSE' else 'false_alarm'
    # 按最终状态映射失败类别；未列出的状态归other_error；不在此处重新分析日志。
    return {'TIMEOUT':'timeout','OUT OF MEMORY':'total_memory','OUT OF JAVA MEMORY':'java_heap','OUT OF NATIVE MEMORY':'native_memory','ERROR (recursion)':'recursion','SEGMENTATION FAULT':'segmentation_fault','unknown':'unknown'}.get(status,'other_error')
# 依次读取四种算法的正式结果。
for alg in ['bmc','k-induction','predicate','impact']:
    # 要求每个raw/算法目录恰有一份匹配的压缩XML，避免混入重复批次。
    files=list((root/'raw'/alg).glob('*.results.*.xml.bz2'));assert len(files)==1
    # 二进制解压并解析XML；with确保关闭文件；tree实际保存根元素。
    with bz2.open(files[0],'rb') as f: tree=ET.parse(f).getroot()
    # 要求无实验级根error且有endtime；任务级超时或失败不等于实验级失败。
    assert not tree.get('error') and tree.get('endtime')
    # 集合保存已经处理的任务编号，用于检查重复。
    seen=set()
    # 遍历XML中的每次run运行。
    for run in tree.findall('run'):
        # 根据完整相对程序路径后缀匹配任务清单，要求唯一匹配。
        ts=[t for t in tasks if run.get('name').endswith('/'+t['program'])];assert len(ts)==1
        # 取匹配任务，检查未重复，再加入seen。
        t=ts[0];assert t['task_id'] not in seen;seen.add(t['task_id'])
        # 把column元素的title/value转为字典，如status、cputime、memory。
        cs={c.get('title'):c.get('value') for c in run.findall('column')}
        # 生成记录：保留原status/category；调用分类函数；时间去掉末尾s转小数；内存字段原样保存。
        records.append(dict(algorithm=alg,task_id=t['task_id'],expected=t['expected'],program=t['program'],status=cs['status'],classification=classify(cs['status'],t['expected']),cpu_s=float(cs['cputime'][:-1]),wall_s=float(cs['walltime'][:-1]),memory_bytes=cs.get('memory',''),category_raw=cs.get('category',''),termination=cs.get('terminationreason','')))
    # 确认本算法覆盖50个不同任务。
    assert len(seen)==50
# 确认四种配置共有200条记录。
assert len(records)==200
# 创建recomputed目录；已存在允许继续，但下面同名CSV会覆盖。
out=root/'recomputed';out.mkdir(exist_ok=True)
# 以UTF-8 BOM写CSV；newline空字符串避免额外空行；仅写新统计，不改原始raw。
with (out/'runs_200.csv').open('w',newline='',encoding='utf-8-sig') as f:
    # 根据首条记录字段写表头，再写全部200条。
    w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
# 逐算法输出简要统计。
for alg in ['bmc','k-induction','predicate','impact']:
    # 筛选当前算法的记录。
    rs=[r for r in records if r['algorithm']==alg]
    # Counter计数各独立类别，转换成普通字典后显示。
    print(alg,dict(Counter(r['classification'] for r in rs)))
    # 汇总全部运行CPU秒除3600；包括失败和超时，不是成功平均耗时。
    print('All CPU hours:',sum(r['cpu_s'] for r in rs)/3600)
# 显示核对完成及输出目录。
print('Verified 200 final records. Recomputed data:',out)
