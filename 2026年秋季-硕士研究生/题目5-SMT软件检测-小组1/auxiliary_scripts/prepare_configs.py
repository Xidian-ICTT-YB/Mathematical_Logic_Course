#!/usr/bin/env python3
# 文档字符串：说明本脚本准备固定50任务的本机配置。
"""Prepare the archived 50-task configurations on a new Ubuntu path."""
# Path用于组合、检查和规范化文件路径。
from pathlib import Path
# argparse接收参数；csv读取任务表；hashlib计算SHA256；ET处理XML。
import argparse,csv,hashlib,xml.etree.ElementTree as ET
# 创建命令行参数解析器。
parser=argparse.ArgumentParser()
# --data必填：svcomp16仓库的c目录，不是仓库最外层。
parser.add_argument('--data',required=True,help='svcomp16 c directory')
# --out必填：用于保存四份新XML的目录，要求尚不存在。
parser.add_argument('--out',required=True,help='new output configuration directory')
# 读取参数；expanduser展开~；resolve转为绝对路径；分号分隔多条语句。
args=parser.parse_args(); data=Path(args.data).expanduser().resolve();out=Path(args.out).expanduser().resolve()
# __file__为脚本路径；parents[1]为scripts的上一级，即材料根目录。
root=Path(__file__).resolve().parents[1]
# 读取data/tasks.csv；DictReader以表头为键；utf-8-sig兼容BOM；list保存全部行。
rows=list(csv.DictReader((root/'data/tasks.csv').open(encoding='utf-8-sig')))
# 断言任务恰好50个；请勿使用python3 -O，否则assert检查被跳过。
assert len(rows)==50
# 依次处理每个固定任务；本脚本不重新抽样。
for row in rows:
    # 拼接源码路径，检查为实际文件；检查失败显示路径并停止。
    p=data/row['program'];assert p.is_file(),p
    # 读取源码字节计算SHA256，与清单比较，防止用错数据版本或改动源码。
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],p
    # 检查对应属性文件存在；此处没有对属性文件计算SHA256。
    assert (data/row['specification']).is_file(),row['specification']
# 输出目录已存在就停止，避免覆盖；SystemExit结束程序。
if out.exists():raise SystemExit('Output already exists; no overwrite: '+str(out))
# 创建输出目录；parents=True会创建缺失的父目录。
out.mkdir(parents=True)
# 依次生成BMC、k归纳、谓词抽象、Impact配置。
for alg in ['bmc','k-induction','predicate','impact']:
    # 解析已有算法XML并取得根元素；保留原算法和资源参数。
    tree=ET.parse(root/'configs'/(alg+'.xml')); b=tree.getroot()
    # 复制根元素子节点列表后遍历，避免删除时影响遍历。
    for node in list(b):
        # 只移除旧tasks节点，稍后替换为本机任务路径。
        if node.tag=='tasks':b.remove(node)
    # BenchExec变量inputfile_path表示输入文件所在目录；使用同目录ALL.prp。
    b.find('propertyfile').text='${inputfile_path}/ALL.prp'
    # 在根节点下新建名为drivers50的tasks元素。
    ts=ET.SubElement(b,'tasks',{'name':'drivers50'})
    # 添加-64：按64位机器模型分析DeviceDriversLinux64任务。
    ET.SubElement(ts,'option',{'name':'-64'})
    # 为50个程序逐一添加include元素，使用本机绝对路径。
    for row in rows:ET.SubElement(ts,'include').text=str(data/row['program'])
    # 输出UTF-8 XML，带XML声明；文件名与算法名称对应。
    tree.write(out/(alg+'.xml'),encoding='utf-8',xml_declaration=True)
# 提示新配置输出位置。
print('Prepared configurations:',out)
