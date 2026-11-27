# 基于 SMT 的软件模型检测：四种算法在 Linux 驱动上的比较

> 数理逻辑课程大作业 · 第五题目
> 复现论文：Dirk Beyer, Matthias Dangl. *SMT-based Software Model Checking: An Experimental Comparison of Four Algorithms*. VSTTE 2016.

在 CPAchecker + MathSAT5 上，用论文补充材料里的原版工具和原版命令，比较四种算法：有界模型检测（BMC）、k-induction、谓词抽象、基于插值的惰性抽象（Impact）。我们从 SV-COMP 2016 DeviceDriversLinux64 中分层选取 22 个任务，四种算法各跑一次，共 88 次运行，并分析了一条错误轨迹和几个算法结果不同的案例。

## 小组成员

| 姓名 | 学号 |
|---|---|
| 周贇杰 | 26181214302 |
| 李俊杰 | 26181214338 |
| 郑粤鑫 | 26181214469 |

## 工具主页与获取地址

| 工具 / 材料 | 地址 | 在本实验中的作用 |
|---|---|---|
| CPAchecker | [GitHub](https://github.com/sosy-lab/cpachecker) · [主页](https://cpachecker.sosy-lab.org/) | 四种验证算法的实现 |
| 论文补充材料 | [官方页面](https://www.sosy-lab.org/research/k-ind-compare/index-vstte.html) | 原版 CPAchecker 1.6.1-svn 23022、四条命令、论文逐任务结果 |
| MathSAT5 | [主页](https://mathsat.fbk.eu/) | SMT 求解器（补充包自带 5.3.12） |
| CBMC | [GitHub](https://github.com/diffblue/cbmc) | 复核反例是否真实可行（补充包自带） |
| sv-benchmarks | [svcomp16 标签](https://github.com/sosy-lab/sv-benchmarks/tree/svcomp16) | Linux 驱动验证任务 |
| 论文原文 | [PDF](https://www.sosy-lab.org/research/pub/2016-VSTTE.SMT-based_Software_Model_Checking_An_Experimental_Comparison_of_Four_Algorithms.pdf) | — |

## 文件说明

| 路径 | 内容 |
|---|---|
| `汇报PPT.pptx` | 课程汇报 PPT：四种算法的原理、实验设置、结果和三个案例 |
| `工具演示视频.mp4` | 工具运行讲解视频（约 8 分钟）：环境、找错误与错误轨迹、四种算法对比、批量结果、代码讲解 |
| `汇报讲解视频.mp4` | 汇报讲解视频（约 23 分钟）：按 PPT 逐页讲解算法原理、实验设置、结果和三个案例 |
| `实验报告.md` / `实验报告.pdf` | 完整实验报告 |
| `scripts/` | `select_tasks.py` 分层选任务并下载；`run_bench.py` 在容器中批量运行；`analyze.py` 汇总；`make_tables.py` 生成表格；`case_study.py` 抽取案例证据 |
| `demo/demo.sh` | 视频里用的演示脚本，分 4 步 |
| `benchmarks/c/` | 22 个任务的源码和属性文件 `ALL.prp` |
| `manifest.json` | 任务清单、分层类别和论文原始结果 |
| `results/` | `matrix.csv` 逐任务结果；`runs.jsonl` 88 条运行记录；`logs/` 88 份原始日志；`evidence/` 错误轨迹；`setup.txt` 环境与冒烟测试记录 |

## 运行环境

- 宿主机：MacBook Air（Apple Silicon），Docker Desktop 29.2.1
- 容器：`eclipse-temurin:8-jre`，`--platform linux/amd64`（补充包里的 MathSAT5 只有 Linux 版，Mac 上无法加载）
- 每次运行：170 s CPU 时限、5000 MB Java 堆、6000 MB 容器内存，88 次逐个串行
- 论文的资源是 900 s CPU、15 GB 内存，比本实验宽松

## 复现步骤

```bash
# 1. 下载论文补充材料（138 MB，包含原版 CPAchecker 和 MathSAT5），解压到 supplements/
curl -L -o supplements-vstte.tar.bz2 https://www.sosy-lab.org/research/k-ind-compare/supplements-vstte.tar.bz2
mkdir -p supplements && tar xjf supplements-vstte.tar.bz2 -C supplements

# 2. 演示（与视频相同）
bash demo/demo.sh 1   # 环境与冒烟测试
bash demo/demo.sh 2   # s3c-hwmon：BMC 找到错误 + 错误轨迹
bash demo/demo.sh 3   # npgtech：四种算法对比
bash demo/demo.sh 4   # 批量结果汇总

# 3. 全量 88 次运行（约 42 分钟）。先清掉已有结果，否则脚本会跳过已完成的运行
rm -rf results/runs.jsonl results/logs
python3 scripts/run_bench.py --timeout 180 --heap 5000 --mem 6000 --workers 1
python3 scripts/analyze.py && python3 scripts/make_tables.py
```

Docker Desktop 至少分配 8 GB 内存。脚本只用 Python 标准库。

## 主要结果

| 算法 | TRUE | FALSE | 超时 | 内存不足 | 正确结论 |
|---|---:|---:|---:|---:|---:|
| BMC | 6 | 6 | 10 | 0 | 12/22 |
| k-induction | 11 | 5 | 5 | 1 | 16/22 |
| 谓词抽象 | 16 | 5 | 0 | 1 | 21/22 |
| Impact | 16 | 5 | 0 | 1 | 21/22 |

- 70 个 TRUE / FALSE 结论全部与任务标签一致，没有错误结论；21 个 FALSE 都经过 CBMC 复核。
- 88 次运行的结果类别（包括超时、内存不足）与论文逐项一致。
- 22 个任务是按论文结果分层挑选的，上表比例不能代表算法在整个类别上的成功率。论文在全部 2120 个驱动任务上的正确数为：BMC 413、k-induction 1174、谓词抽象 1250、Impact 1239。

## 工具搭建后的主要思考

1. **复现旧工具，环境比代码更难。** 2016 年的补充包只带 x86 Linux 版的 MathSAT5 原生库，新版 CPAchecker 也一样，Apple 芯片的 Mac 无法直接运行。我们用 Docker 的 linux/amd64 容器加 Java 8 解决，并先用冒烟测试确认求解器能加载、能给出正确结论，再开始正式实验。

2. **“没结论”的原因要分清。** CPAchecker 的 `-timelimit` 算的是 CPU 时间，k-induction 并行跑两个分析，墙钟 80 秒就可能用完 170 秒 CPU；容器内存超限被杀时退出码是 137，日志里没有结论。早期我们把内存上限设成 3.2 GB，BMC 被提前杀掉，看起来像“超时”。如果不读日志区分“超时”“内存不足”和“工具异常”，就会把环境问题误当成算法能力问题。

3. **找错误和证安全是两类不同的问题。** 找错误只要存在一条能走通的路径，BMC 展开到那一圈就能找到（s3c-hwmon、vhost_net）；证安全要覆盖“任意多圈”，BMC 只能一圈圈展开，永远完不成（npgtech 展开到 1000 圈以上仍无结论），必须靠归纳（k-induction）或抽象（谓词抽象、Impact）。没有哪种算法总是最好：vhost_net 上只有 BMC 在内存耗尽前找到了错误。

4. **报告结论时要看清证据来自哪里。** k-induction 的 11 个 TRUE 里，有 9 个其实是并行的不变式生成分析完成的，不是归纳本身；vhost_net 的 FALSE 是因为规则模型按锁的名字记录状态，把两把不同的锁当成同一把，只说明违反了规则模型，不等于真实的内核缺陷；88/88 与论文一致，主要说明复现环境正确，因为任务本来就是按论文结果挑的。
