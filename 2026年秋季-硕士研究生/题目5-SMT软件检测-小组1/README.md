# 基于SMT的软件模型检测四算法复现实验

本项目复现VSTTE 2016论文《SMT-based Software Model Checking: An Experimental Comparison of Four Algorithms》中的部分实验：固定DeviceDriversLinux64类别50个任务，运行BMC、k归纳、谓词抽象及Impact，共200次正式运行。

## 小组成员

| 姓名 | 学号 |
|---|---|
| 李健 | 26181214304 |
| 凌嘉日 | 26181214408 |
| 米佳硕 | 26181214244 |

## 工具主页与获取地址

| 工具或材料 | GitHub仓库或主页 | 本实验中的作用 |
|---|---|---|
| CPAchecker | [主页](https://cpachecker.sosy-lab.org/) · [GitHub](https://github.com/sosy-lab/cpachecker) | 提供四种验证算法的实现 |
| 论文历史补充材料 | [官方补充页](https://www.sosy-lab.org/research/k-ind-compare/index-vstte.html) | 获取本实验使用的历史工具、配置及论文结果；不直接用最新工具替换 |
| BenchExec | [GitHub](https://github.com/sosy-lab/benchexec) · [3.25安装说明](https://github.com/sosy-lab/benchexec/blob/3.25/doc/INSTALL.md) | 批量调度、资源限制和测量 |
| MathSAT5 | [官方主页](https://mathsat.fbk.eu/) | SMT约束求解；本实验沿用历史包附带版本 |
| CBMC | [GitHub](https://github.com/diffblue/cbmc) | 按相关配置检查候选反例；沿用历史材料中的工具 |
| sv-benchmarks | [svcomp16数据版本](https://github.com/dbeyer/sv-benchmarks/tree/svcomp16) | 提供Linux驱动验证任务 |

## 报告、演示和视频

- [实验报告](实验报告.docx)
- [汇报PPT](SMT_四算法比较.pptx)
- [操作讲解视频](操作讲解视频.mp4)

报告、PPT与视频共同介绍论文原理、搭建过程、实验结果及案例分析。

## 目录

- scripts/：prepare_round2.py和run_round2.sh的中文注释版，执行逻辑不变。
- selection_inputs/抽样所需原30任务清单和四份配置；仅为输入溯源，不含第一轮实验成绩或日志。
- auxiliary_scripts/：实验完成后整理的三个独立辅助脚本。
- data/：最终50任务清单、200次运行明细、汇总和配对表。
- configs/：实际正式实验的四份配置，保留当时路径作为证据。
- raw/：正式结果XML.bz2、逐任务日志ZIP、控制台和环境记录。
- cases/：T21错误轨迹、T31算法差异案例的源码及导出证据。
- paper_comparison/：与论文官方逐任务记录的对照。
- MANIFEST.sha256：本地原始文件校验清单。

## 环境与资源

Ubuntu20.04.6虚拟机，Java8，Python3.8.10，BenchExec3.25；官方历史补充包工具实际记录为CPAchecker1.6.1-svn23022、MathSAT5 5.3.12。每任务最多2核，CPU软限制900秒、硬限制1000秒、总内存5000MB、Java堆3000M；BenchExec任务并发1，正式运行关闭swap，使用--no-container。

论文原结果表CPAchecker修订号为22870，任务内存限制为15000MB，Java堆示例10000M，因此不是完全相同的工具与资源条件。

## 任务来源

数据版本为svcomp16标签，提交dbb9372541d3c068d970a2b76a92d8fa8f9a9d48。最终清单为35安全、15不安全，实际构造过程保留已有30任务，再按来源目录分组、组内打乱及目录轮流取的方式追加15安全5不安全，新增随机种子20261013；不根据正式运行成绩筛选。独立复现直接读取data/tasks.csv，不重新抽样。

## 推荐的独立复现入口

先从官方补充页获取历史工具，并准备上述数据、Java8和可用的BenchExec权限。数据与工具安装包未包含在本仓库。

在仓库根目录：

```bash
python3 auxiliary_scripts/prepare_configs.py \
  --data "$HOME/smt-project/benchmarks/sv-comp16/c" \
  --out "$HOME/smt-project/github-configs"
```

输出配置目录必须不存在；脚本检查全部源码SHA256并生成本机路径配置。不要直接运行configs中保留的旧绝对路径。

运行前按实际交换设备关闭swap；辅助运行脚本不会自动关闭或恢复。确认内存及资源权限后：

```bash
bash auxiliary_scripts/run_experiments.sh \
  "$HOME/smt-project/downloads/supplements-vstte/CPAchecker" \
  "$HOME/smt-project/github-configs" \
  "$HOME/smt-project/results/github-reproduction"
```

结果目录也必须是新目录。运行结束后恢复此前启用的交换空间。

仅核查本仓库已有结果，不需要启动验证器：

```bash
python3 auxiliary_scripts/recalculate.py
```

脚本读取raw/，输出recomputed/runs_200.csv。它不会自动读取新运行的结果目录；新旧批次应分开存放。

## 原始双脚本的用途及依赖

原始prepare_round2.py固定读取~/smt-project/results/formal-20261012-145215/下的任务表和四份-30.xml，还需要results/driver-smoke/program.txt指向既有试跑程序。此处附有前者的输入快照，但本包未提供原driver-smoke/program.txt，因此原脚本不能仅靠本仓库直接从零运行。原run_round2.sh固定读取experiment/round2-50-900s，并需要该目录内tasks.csv、round1-tasks.csv、sampling.txt、prepare_round2.py及四份-50.xml。

原脚本作为真实过程证据保留。其他机器请优先使用上述独立入口，而不是补造前期目录。原运行脚本会关闭/swapfile并在退出时尝试恢复，辅助脚本则只检查状态；两者不能混用说明。

## 正式结果

BMC、k归纳、谓词抽象、Impact分别正确解决4、10、13、13个任务。失败、超时、内存和递归支持限制均保留，不将未解决任务删除。所有确定结论与标签一致，不将基准模型结论扩大解释为真实内核漏洞证明。T21和T31案例补充运行用于解释行为，不替换正式运行耗时。

## 工具搭建与复现后的主要思考

###  1、四种算法使用相同的SMT求解基础，但组织分析的方式不同。 
BMC通过逐步展开寻找错误，k归纳结合基础检查、归纳步骤与辅助不变量证明安全；谓词抽象和Impact则利用抽象与插值减少需要探索的状态。因此，共用CPAchecker和MathSAT5并不意味着四种方法会得到相同的结果或耗时。

###  2、有限范围内未发现错误，不等于已经证明全局安全。 
BMC在当前展开深度没有找到反例，只能排除这一范围内的错误路径；只有满足充分展开等证明条件时才能给出安全结论。超时或UNKNOWN也不能解释为程序安全，应与明确的TRUE、FALSE结论区分。

###  3、候选反例需要检查，确认的反例也受到程序模型限制。 
抽象分析可能产生实际不可行的错误路径，需要通过可行性检查排除。T21展示了基准模型中违反锁状态要求的路径，但其中涉及环境模型和NULL相关访问，不能直接据此宣布真实Linux内核存在同样的漏洞。

###  4、Impact的优势取决于具体任务，不能仅凭单个案例进行总体排名。 
T31中，Impact的抽象计算次数更少，运行快于谓词抽象；但在全部共同成功任务上，谓词抽象的累计CPU时间更低。这说明局部提速不等于总体占优，应结合相同任务上的耗时与内部统计判断。

###  5、资源不足和工具不支持是不同的失败原因。 
T21在论文中的BMC和k归纳运行分别使用约6.34GB和10.31GB内存，超过本实验5GB上限，因此本次内存终止有明确的资源差异依据。递归支持错误则属于当前工具配置的功能限制，不能期待仅增加内存就能解决。


## 数据来源与第三方内容

- [论文官方补充页](https://www.sosy-lab.org/research/k-ind-compare/index-vstte.html)
- [sv-benchmarks](https://github.com/dbeyer/sv-benchmarks/tree/svcomp16)
- [CPAchecker](https://github.com/sosy-lab/cpachecker)

