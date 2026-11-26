# CPAchecker 大作业：VSTTE 2016 四种 C 程序验证算法对比

> 课程：数理逻辑大作业（2026 年秋季本科拔尖班，第五组）  
> 题目方向：SAT/SMT 与软件模型检测

## 小组成员

| 姓名 | 学号 | 分工 |
| --- | --- | --- |
| 谷政辉 | 24009290065 | ppt制作，讲解视频录制 |
| 王子杰 | 24009290053 | 实验运行 |
| 丁奕仁 | 24009290006 | ppt讲解 |

## 任务简介

本项目参照 VSTTE 2016 的四算法对比实验，使用 CPAchecker 和 MathSAT5 检查 C 程序能否到达错误位置。在 SV-COMP 2016 的 DeviceDriversLinux64 类别中选取 24 个任务，其中 12 个预期安全、12 个预期不安全。每个任务由四种算法分别运行，共 96 次正式实验。

另选一个同步计数器程序用于演示。循环内 `x` 和 `y` 同时递增，将 `y` 赋给 `z`，若 `x != z` 则调用 `__VERIFIER_error()`。四种算法验证同一条性质，即该错误函数不可达。

## 工具与材料来源

| 工具或材料 | 用途 | 来源 |
| --- | --- | --- |
| CPAchecker | C 程序可达性验证 | [项目主页](https://cpachecker.sosy-lab.org/)、[官方代码仓库](https://github.com/sosy-lab/cpachecker) |
| VSTTE 2016 论文 | 四种算法的原理和实验设计 | [SMT-based Software Model Checking: An Experimental Comparison of Four Algorithms](https://www.sosy-lab.org/research/pub/2016-VSTTE.SMT-based_Software_Model_Checking_An_Experimental_Comparison_of_Four_Algorithms.pdf) |
| 作者实验补充包 | CPAchecker、MathSAT5、作者配置和原实验结果 | [官方实验页](https://www.sosy-lab.org/research/k-ind-compare/index-vstte.html)、[下载补充包](https://www.sosy-lab.org/research/k-ind-compare/supplements-vstte.tar.bz2) |
| SV-COMP 2016 验证任务 | 批量实验的 C 程序和性质 | [sv-benchmarks 的 svcomp16 标签](https://github.com/dbeyer/sv-benchmarks/tree/svcomp16) |

## 基本原理

| 算法 | 如何判断错误位置能否到达 |
| --- | --- |
| BMC（有界模型检测） | 按界限 `k` 展开循环，用 SMT 检查界内是否存在错误路径。在本实验启用前向条件检查，当确认无须继续展开且未发现错误时，可得出安全结论。 |
| k-induction（k 归纳） | 基础检查排除起始执行片段内的反例，归纳步检查在连续若干状态均满足性质时，下一状态是否也满足。配置并行生成可加强归纳的辅助不变式。 |
| 谓词抽象 + CEGAR | 用谓词描述抽象状态。发现抽象错误路径后检查其可行性，遇到伪反例时提取谓词并细化抽象。 |
| Impact | 用插值加强抽象可达图上各节点的局部公式。当某节点的公式蕴含同一程序位置上已有节点的公式时，可利用覆盖关系避免重复探索。 |

## 运行环境

使用 x86-64 Ubuntu（WSL2）、OpenJDK 11.0.29、Python 3 和 GNU `time` / `timeout`。官方实验页列出的版本为 CPAchecker 1.6.8-vstte，实际使用的官方补充包内 JAR 自报 `1.6.1-svn 23022`，MathSAT5 为补充包自带的 5.3.12。

归档中的 BenchExec 1.10-dev 在本机 WSL2 的 cgroups v2 环境下无法可靠施加限制。正式运行采用串行调度，CPAchecker CPU 时间限制为 55 秒，外部墙钟超时为 60 秒，JVM 堆上限为 1200 MiB。堆上限只约束 Java 堆。

## 工具搭建与运行方法

请在 WSL2 的 Linux 文件系统中建立一个新目录，将 [实验代码包](CPAchecker_实验代码.zip) 放入该目录。以下命令从该目录执行。需要能使用 `unzip`、`curl`、`git`、`patch`、`python3` 和 Java 11。

```bash
unzip CPAchecker_实验代码.zip
curl -fLO https://www.sosy-lab.org/research/k-ind-compare/supplements-vstte.tar.bz2
echo '0e531f81b8fa079b3611fe22c6c7d3261ed7dbbf9210b23346abab33d14aefe9  supplements-vstte.tar.bz2' | sha256sum -c -
tar -xjf supplements-vstte.tar.bz2
git clone --depth 1 --branch svcomp16 https://github.com/dbeyer/sv-benchmarks.git sv-comp16
git -C sv-comp16 rev-parse HEAD
mkdir -p supplements-vstte/CPAchecker/test/programs
ln -s "$(realpath sv-comp16/c)" supplements-vstte/CPAchecker/test/programs/benchmarks
patch supplements-vstte/CPAchecker/scripts/cpa.sh < configs/cpa.sh.patch
```

任务集的提交应为 `dbb9372541d3c068d970a2b76a92d8fa8f9a9d48`。补丁修正历史启动脚本对 Java 11 版本号的识别。官方补充包提供 JAR、配置和本地求解器库，解压后保留其目录结构。

查看同步计数器源码并分别运行四种算法：

```bash
python3 Four_Algorithm_Demo/show.py code
for algorithm in bmc k-induction predicate impact; do
    python3 Four_Algorithm_Demo/show.py run "$algorithm"
done
python3 Four_Algorithm_Demo/show.py detail predicate
python3 Four_Algorithm_Demo/show.py detail impact
```

运行 24 个正式任务：

```bash
python3 scripts/experiment_runner.py manifests/formal24.tsv \
    --phase formal24 --wall-limit 60 --internal-time 55 --heap-mb 1200
```

每次运行的命令、日志、计时和分类保存在 `runs/formal24/`，同一阶段可沿用相同命令继续运行。

## 实际结果

| 算法 | 正确证明 | 正确反例 | 超时 | 内存不足 | 工具异常 | 正确结论 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BMC | 6 | 9 | 4 | 0 | 5 | 15/24 |
| k-induction | 12 | 10 | 2 | 0 | 0 | 22/24 |
| 谓词抽象 + CEGAR | 9 | 10 | 0 | 1 | 4 | 19/24 |
| Impact | 9 | 10 | 0 | 1 | 4 | 19/24 |

96 次正式运行中，75 次给出正确结论，错误结论和 UNKNOWN 均为 0。同步计数器演示中，四种算法均证明错误函数不可达。日志分别展示了 BMC 增加循环展开界限、k-induction 在 `k=1` 完成归纳证明、CEGAR 增加谓词，以及 Impact 加强节点公式并建立覆盖。

## 汇报案例与录屏

汇报先用同步计数器说明四种算法的路径公式、抽象与停止条件，再用两个正式实验任务展示真实反例和算法差异。

| 录屏 | 内容 | 时长 |
| --- | --- | :--- |
| 错误路径说明 | 在 s3c-hwmon 驱动模型中，首次执行属性创建后，两个计数器的值分别为 0 和 1，检查失败并到达错误位置。四种算法都找到了真实反例。 | 3 分 15 秒 |
| 四种算法对比 | 在 rc-npgtech 驱动模型中，BMC 持续增加展开界限直到超时，另三种方法给出安全结论。 | 1 分 59 秒 |

两段录屏合计约 5 分 14 秒。幻灯片第 31–34 页对应这两个正式实验案例。 

## 工具搭建与任务完成后的思考

1. 四种算法即使给出相同结论，所需的证明过程也不同。同步计数器案例中，单步归纳即可完成证明，而 BMC 逐步增加展开界限，直到排除更长的执行。
2. 谓词抽象与 Impact 在这 24 项任务中的结果计数相同。演示日志仍能看到两者各自更新的对象，前者加入抽象谓词，后者加强局部节点公式并重新判断覆盖。
3. k-induction 在本样本中得到最多正确结论。样本选取、资源限制及历史工具的运行环境都会影响结果，这一排名仅适用于本次 24 项实验。

## 项目结构与交付物

- [汇报幻灯片 PDF](数理逻辑.pdf)（36 页）。
- [实验代码包](CPAchecker_实验代码.zip)，包含批量运行脚本、固定任务清单、配置与补丁、同步计数器样例和正式实验结果。
- 两段原始案例录屏的提交版链接见上方「汇报案例与录屏」。
