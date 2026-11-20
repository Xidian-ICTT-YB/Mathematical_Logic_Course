# 基于 SMT 的软件模型检测四算法对比实验

本项目为数理逻辑课程第五题的实验作业，参考 VSTTE 2016 论文 *SMT-based Software Model Checking: An Experimental Comparison of Four Algorithms*，使用 CPAchecker 对 BMC、k-induction、Predicate Abstraction 和 Impact 四种算法进行实验比较。

从 SV-COMP 2016 的 `DeviceDriversLinux64` 类别中选取22个验证任务，每个任务分别使用四种算法运行，共完成88次实验。项目保存了测试程序、算法配置、运行脚本、结果统计及部分任务的详细输出。

## 小组成员

| 姓名   | 学号        |
| ------ | ----------- |
| 李优赏 | 26031212363 |
| 刘名浩 | 26031111135 |
| 孙达乐 | 25031212386 |

## 工具与参考资料

| 工具或资料              | 地址                                                         | 用途                             |
| ----------------------- | ------------------------------------------------------------ | -------------------------------- |
| CPAchecker              | [官方网站](https://cpachecker.sosy-lab.org/) · [GitHub](https://github.com/sosy-lab/cpachecker) | 提供四种软件模型检测算法         |
| BenchExec               | [GitHub](https://github.com/sosy-lab/benchexec)              | 执行批量实验、限制资源并记录结果 |
| MathSAT5                | [官方网站](https://mathsat.fbk.eu/)                          | SMT 求解器                       |
| VSTTE 2016 论文补充材料 | [论文实验资料](https://www.sosy-lab.org/research/k-ind-compare/index-vstte.html) | 提供历史工具、算法配置及参考实验 |
| SV-COMP 基准程序        | [sv-benchmarks](https://github.com/sosy-lab/sv-benchmarks)   | 提供 C 程序验证任务              |

## 实验环境与方法

实验在 Windows 11 主机上使用 Docker Desktop 运行，容器环境及主要工具版本如下：

| 项目           | 实验配置           |
| -------------- | ------------------ |
| 容器系统       | Ubuntu 20.04.6 LTS |
| Java           | OpenJDK 8          |
| CPAchecker     | 1.6.1-svn23022     |
| BenchExec      | 3.26               |
| SMT 求解器     | MathSAT5 5.3.12    |
| CPU 限制       | 2核                |
| 内存限制       | 6000 MB            |
| Java 堆内存    | 4000 MB            |
| CPU 软时间限制 | 900秒              |
| CPU 硬时间限制 | 1200秒             |
| 任务并发数     | 1                  |

选取的22个正式任务中，预期结果为 TRUE 的有15个，预期结果为 FALSE 的有7个。

对每个任务分别使用 BMC、k-induction、Predicate Abstraction 和 Impact 运行，采用相同的资源限制，共保存88条实际运行记录。

具体实验过程见 [docs/experiment.md](docs/experiment.md)，环境配置见 [docs/environment.md](docs/environment.md)。

## 实验结果

88次运行的结果统计如下：

| 运行状态           | 次数   |
| ------------------ | ------ |
| TRUE               | 15     |
| FALSE              | 8      |
| TIMEOUT            | 30     |
| OUT OF MEMORY      | 10     |
| OUT OF JAVA MEMORY | 6      |
| ERROR（递归相关）  | 15     |
| ERROR（其他）      | 2      |
| unknown            | 2      |
| **合计**           | **88** |

其中23次得到了明确的 TRUE 或 FALSE 结论，均与对应任务的预期结果一致。其余65次由于超时、内存限制、工具错误等原因，没有得到确定的验证结论。

各算法的具体结果、耗时和任务对照见：

- [results.csv](experiment/formal-20261117-141308/results.csv)：88次运行结果及资源使用明细。
- [algorithm_summary.csv](experiment/formal-20261117-141308/algorithm_summary.csv)：按算法统计的验证结果和耗时。
- [task_matrix.csv](experiment/formal-20261117-141308/task_matrix.csv)：22个任务在四种算法下的结果对照。

结果分析及相关说明见 [docs/result_notes.md](docs/result_notes.md)。

## 典型案例

从正式实验中选取六个任务，保存了较完整的运行日志、统计文件、报告或反例信息。

| 任务 | 实验结果                                                     | 主要观察内容                       |
| ---- | ------------------------------------------------------------ | ---------------------------------- |
| T01  | 四种算法均返回 FALSE                                         | 比较不同算法发现属性违反时的输出   |
| T02  | BMC、k-induction 超时；Predicate、Impact 返回 TRUE           | 比较不同算法验证同一安全任务的表现 |
| T03  | BMC、Predicate 返回 unknown；k-induction、Impact 超时        | 区分未确定结果与明确的验证结论     |
| T05  | k-induction、Predicate、Impact 返回 TRUE；BMC 出现 Java 堆内存不足 | 比较不同算法的内存需求             |
| T06  | 三种算法出现递归相关错误，k-induction 内存不足               | 区分工具支持限制和资源耗尽         |
| T19  | Impact 返回 TRUE，其余算法超时或 Java 堆内存不足             | 比较同一任务下的算法结果差异       |

详细文件见 [cases/](cases/)，具体说明见 [cases/README.md](cases/README.md)。

## 项目目录

```
├── README.md       # 项目说明
├── tasks/          # 正式测试程序、属性文件和自建测试
├── configs/        # 四种算法的实验配置
├── experiment/     # 任务清单、运行记录和统计结果
├── results/        # 88份BenchExec原始XML结果
├── cases/          # 六个任务的详细运行输出
├── docker/         # Docker环境相关文件
├── scripts/        # 实验运行、统计和核验脚本
├── logs/           # 实验运行与环境调试记录
└── docs/           # 环境、实验过程及结果说明
```

## 文件使用与复现说明

实验数据位于 `experiment/formal-20261117-141308/`。

其中，`tasks.csv` 为正式任务清单，`runs.csv` 为实验执行前生成的运行计划，`results.csv` 为实际运行结果。

`results/` 中保存了88份 BenchExec 原始 XML 结果。六个案例的部分 CPAchecker 详细输出保存在 `cases/` 中。

`scripts/source/run-formal.ps1` 是正式实验使用的运行脚本副本，其中包含原实验机器的绝对路径。`docker/` 中保存了环境构建和调试过程中使用的文件。

正式实验的 Docker 镜像已在原电脑上导出，并在同一台电脑完成重新加载检查。

## 实验中的几点观察

**1. 四种算法在相同任务下的表现存在差异。**

T01 中四种算法均发现了属性违反，但耗时不同；T02 中 Predicate Abstraction 和 Impact 得到 TRUE，而 BMC 和 k-induction 在规定时间内未能完成验证。相同的验证对象和资源限制不意味着不同算法一定能得到相同的确定结论。

**2. 未找到反例不等于已经证明安全。**

模型检测工具返回 TRUE、FALSE、TIMEOUT、unknown 或错误状态，含义不同。特别是 BMC 的有限展开分析，不能仅凭当前展开范围内没有发现错误，就推断程序在所有执行情况下安全。

**3. 算法能力与实验资源限制需要区分。**

本次实验存在超时、进程内存不足、Java 堆内存不足及递归相关错误。资源耗尽可能与实验设置有关，递归相关错误则可能涉及工具或配置的支持能力，不能将所有未解决任务归结为算法本身的验证能力不足。

**4. 性能比较需要使用一致的统计口径。**

本实验保留了每次运行的 CPU 时间和 Wall Time，同时记录未得到确定结论的运行。比较算法耗时时，应区分不同任务、不同运行状态及资源条件，不宜仅凭少数成功案例判断某种算法整体优于其他算法。

## 数据来源与说明

实验参考 VSTTE 2016 论文及其公开补充材料，测试任务来自 SV-COMP 基准程序集。

本次实验与原论文的工具、硬件及资源限制并非完全一致，因此本实验是选定任务和实验条件下的复现记录，不是与原论文完全相同条件下的直接性能对比。
