# 50个任务的SMT软件模型检测实验

本实验选取50个Linux驱动验证程序，其中预期安全25个、预期存在错误25个，使用CPAchecker中的BMC、k-induction、谓词抽象（predicateAnalysis）和IMPACT四种配置进行检测。每个程序使用每种配置运行一次，共200次正式实验。

实验统计安全、错误、超时及运行时间，并解释一条错误轨迹和一个不同算法表现存在差异的案例。Python脚本负责运行调度、日志解析和统计，模型检测算法由CPAchecker提供。

## 1. 实验结果

| 配置 | SAFE | UNSAFE | TIMEOUT | RSS内存限制 | Java堆错误 | ERROR | UNKNOWN |
|---|---:|---:|---:|---:|---:|---:|---:|
| BMC | 2 | 5 | 16 | 0 | 1 | 24 | 2 |
| k-induction | 7 | 4 | 35 | 1 | 0 | 2 | 1 |
| 谓词抽象 | 11 | 4 | 11 | 2 | 0 | 22 | 0 |
| IMPACT | 11 | 4 | 12 | 1 | 0 | 22 | 0 |

每行对应50次运行。`SAFE`表示证明指定性质成立，`UNSAFE`表示确认存在错误路径。`ERROR`是工具运行报错，不能算作被验证程序有缺陷；超时、内存终止和`UNKNOWN`均未给出确定结论。所有确定判定均与基准标签一致。

本实验使用 Dirk Beyer 和 Matthias Dangl 在 VSTTE 2016 发表的论文 [*SMT-based Software Model Checking: An Experimental Comparison of Four Algorithms*](https://doi.org/10.1007/978-3-319-48869-1_14) 作为对照。我们从[论文补充材料](https://www.sosy-lab.org/research/k-ind-compare/index-vstte.html)中取出同一批 50 个任务在四种配置下的结果，按统一的粗分类逐项比较。200 条记录中有 189 条结果类别一致（94.5%）。成功求解率另按得到 SAFE 或 UNSAFE 判定的记录计算。详细统计和解释见[50任务实验结果](experiment-v2/review-coverage-20261114/覆盖实验分析.md)及[结果核验说明](experiment-v2/review-coverage-20261114/审计补充说明.md)。

## 2. 文件结构与查阅方法

下面按实际文件层级展示项目结构。`*`表示已有目录名的后缀或同类文件，省略具体日期后缀；这只是阅读示意，不需要重命名文件。正式实验仍为50个任务、200次运行，标为“案例补充”的材料不计入主表。

```text
main/
├── README.md                         # 总说明、结果概览与核验入口
├── demo/                             # 课堂展示与离线核验
│   ├── README.md                     # 演示命令和操作说明
│   ├── run.py                        # 读取证据，展示统计与两个案例
│   ├── live-schedule.json            # 单题工具操作示例的计划
│   └── trace-sha256.json             # 补充错误轨迹的文件哈希
├── scripts/                          # 实验调度、统计与检查代码
│   ├── run_v2.py                     # 调用CPAchecker执行运行计划
│   ├── v2_evidence.py                # 从日志解析判定、终止原因与指标
│   ├── fetch_v2_inputs.py            # 获取并校验固定版本输入
│   ├── review_v2_coverage.py          # 复核200次正式结果并对照论文
│   ├── build_timing_appendix.py      # 生成耗时汇总与逐题明细
│   ├── review_v2_repeats.py           # 案例补充记录的统计分析
│   ├── test_run_v2.py                # 运行器自检
│   └── test_v2_evidence.py           # 日志解析器自检
├── experiment-v2/                    # 实验输入、正式记录及分析
│   ├── design-*/                     # 任务清单与执行计划
│   │   ├── tasks50-candidates.json   # 50题候选清单
│   │   ├── tasks50-frozen.json       # 正式输入清单、标签和哈希
│   │   ├── coverage200-schedule.json # 50题×4配置的200次执行计划
│   │   ├── case-repeat-schedule.json # 案例补充运行计划
│   │   ├── selection-provenance.json # 任务选择依据
│   │   └── download-provenance.json # 输入版本、下载来源与哈希
│   ├── inputs/c/                     # 被检测程序与性质
│   │   └── ldv-*/                    # 不同基准类别
│   │       ├── *.c / *.i             # C程序或预处理后的C程序
│   │       └── ALL.prp               # 同类别程序共用的验证属性
│   ├── evidence/                     # 原始运行记录，按批次独立保存
│   │   └── v2-*/                     # 正式实验与案例补充各有目录
│   ├── review-coverage-*/            # 50任务正式实验分析
│   │   ├── 覆盖实验分析.md            # 结果表、论文对照与结论范围
│   │   ├── 审计补充说明.md            # 错误分类、计时及证据说明
│   │   ├── comparison200.json        # 200条结果的论文逐项对照
│   │   ├── summary.json              # 正式实验统计汇总
│   │   └── local-evidence-sha256.json # 正式记录的文件哈希
│   ├── review-repeat-*/              # 算法差异案例的补充分析
│   │   ├── 重复实验分析.md            # 补充记录的状态与耗时分析
│   │   ├── 下载校验.md                # 补充记录完整性说明
│   │   ├── summary.json              # 案例重复统计
│   │   ├── metric-evidence.json      # 从日志提取的内部指标
│   │   └── local-evidence-sha256.json # 补充记录的文件哈希
│   ├── config-evidence/              # 案例引用的关键配置摘录
│   ├── case-analysis.json            # pcd配置差异与指标证据
│   ├── timing-summary.json           # 正式实验的算法耗时汇总
│   └── timing-task-map.json          # 逐题耗时及日志位置映射
├── evidence/                         # 独立的案例展示材料
│   ├── vhost-trace/                  # 错误轨迹补充导出
│   │   ├── command.json              # 导出轨迹的实际命令
│   │   ├── run.log                   # 反例确认日志
│   │   └── output/
│   │       └── Counterexample.1.core.txt # 带源码行号的核心错误路径
│   └── live-demo/                    # 单题操作示例，不计入主表
│       ├── command.json              # 示例命令
│       ├── result.json               # 示例结果
│       └── run.log                   # 示例日志
└── third_party/                      # 论文与工具的参考材料
    └── supplements-vstte/
        ├── results/
        │   └── *.DeviceDriversLinux64.xml # 论文四种配置的结果
        └── CPAchecker/
            ├── config/               # 工具配置库及性质定义
            ├── test/test-sets/
            │   └── *-bitprecise.xml  # 四种配置的实验定义
            ├── Authors.txt           # 第三方作者与贡献者说明
            └── README.txt            # 原工具说明
```

两处名为`evidence`的目录用途不同：`experiment-v2/evidence`保存批量实验的完整记录；根目录下的`evidence`保存便于课堂讲解的独立轨迹与操作示例。`third_party/supplements-vstte/CPAchecker`中只有参考材料，不是完整可执行工具安装。

### 一次运行的结果在哪里

下面以[正式实验原始记录](experiment-v2/evidence/v2-20261113-125655-b19929)为例。编号对应执行计划中的第几次运行，不是题号；一个程序使用四种配置会产生四条运行记录。

```text
正式实验批次目录/
├── metadata.json                     # 环境、资源限制、工具和输入身份
├── schedule.json                     # 200次运行的顺序与程序/算法对应
├── results.json                      # 200次结果的汇总
├── COMPLETE                          # 计划已经全部处理完的标记
├── 001/                              # 第1次运行
│   ├── result.json                   # 判定、CPU/墙钟时间和终止原因
│   └── attempt-*/                    # 该次实际执行记录
│       ├── command.json              # CPAchecker命令及参数
│       ├── run.log                   # 工具原始输出
│       └── output/                   # 仅部分运行生成的额外输出
│           ├── ErrorPath.txt         # 路径文本
│           └── witness.graphml.gz    # 压缩的机器可读见证
├── 002/
├── …
└── 200/
```

先读`result.json`了解结果，再看`run.log`查找诊断，最后用`command.json`核对参数。`COMPLETE`仅表示计划处理完毕，不能理解为200次均验证成功；存在路径或见证文件也不自动等于确认了错误，仍需结合结果与日志判断。

### 常用阅读入口

| 想查看的内容 | 文件入口 |
|---|---|
| 四种算法的安全、错误、超时数量 | [50任务实验结果](experiment-v2/review-coverage-20261114/覆盖实验分析.md) |
| 每个任务与论文的对照 | [逐项对照](experiment-v2/review-coverage-20261114/comparison200.json) |
| 总体耗时和逐题耗时 | [耗时汇总](experiment-v2/timing-summary.json)、[逐题映射](experiment-v2/timing-task-map.json) |
| 被检测的程序和验证性质 | [程序输入](experiment-v2/inputs/c)、[固定任务清单](experiment-v2/design-20261111/tasks50-frozen.json) |
| 一条错误轨迹 | [vhost核心路径](evidence/vhost-trace/output/Counterexample.1.core.txt) |
| 算法表现差异的依据 | [pcd案例分析](experiment-v2/case-analysis.json) |
| 核验或课堂演示命令 | [演示说明](demo/README.md) |

`ALL.prp`规定待验证性质：从`main`开始的执行不能调用`__VERIFIER_error()`。本文的结果和耗时统计仅采用50个任务的200次正式记录；案例补充证据不增加主表的任务数或运行次数。


## 3. 离线查看与核验

需要Python 3.8或更高版本，仅使用标准库。在同时包含本README、`demo`、`scripts`和`experiment-v2`的项目根目录打开终端。以下命令读取保存的记录，不启动新的模型检测；`-B`表示不生成Python字节码缓存。Windows可将`python3`替换为`py -3`。

下面命令核验保存证据的文件哈希、输入程序、运行计划、日志和结果一致性；检查范围包括案例补充证据，主表仍只统计200次正式运行。

```bash
python3 -B demo/run.py --check
```

下面命令从200份正式实验日志重新计算四种配置的结果统计。

```bash
python3 -B demo/run.py --summary
```

下面命令展示vhost错误路径及日志中的反例确认信息。

```bash
python3 -B demo/run.py --case vhost
```

下面命令展示pcd案例的补充分析，解释谓词抽象与IMPACT的耗时及内部统计差异。该命令会读取案例重复记录，不把它们合并进正式主表。

```bash
python3 -B demo/run.py --case pcd
```

## 4. 运行环境与脚本

新验证需要Linux x86-64、Java 8和论文对应的完整CPAchecker工件，包含所需的MathSAT5及反例核查工具。当前目录提供代码、输入及证据，不包含完整工具安装包。Java和CPAchecker需分别部署到项目下的`tools/java8/bin/java`和`tools/supplements-vstte/CPAchecker`，具体步骤见[演示说明](demo/README.md)。

本实验任务串行执行，使用两个逻辑CPU、900秒CPU软时限、1000秒硬保护、`10000M` Java堆、15,000,000,000字节进程组RSS监控阈值和2000秒墙钟保护。实际配置与工具哈希保存在正式实验的`metadata.json`中。

| 脚本 | 用途 |
|---|---|
| `run_v2.py` | 根据任务计划执行验证；默认预检查，显式加`--run`才开始。复跑本实验须指定200次覆盖计划 |
| `v2_evidence.py` | 解析日志中的判定、终止原因、诊断和统计 |
| `fetch_v2_inputs.py` | 取得固定版本输入并校验哈希；默认检查，`--download`才下载 |
| `review_v2_coverage.py` | 复核200条正式结果，生成论文对照、汇总和分析 |
| `review_v2_repeats.py` | 分析案例补充记录，不合并进正式200条结果 |
| `build_timing_appendix.py` | 计算运行时间汇总与逐题明细；默认写派生文件，`--check`检查已有成品一致性 |
| `test_run_v2.py`、`test_v2_evidence.py` | 检查运行器与结果分类代码 |

已有冻结清单和输入可用于复跑50题，不需要重新选择任务。新运行的结果写入新的`results`子目录，离线演示默认仍读取随包保存的正式结果。

## 5. 结果解释与证据

CPU时间采用日志中的`Total CPU time for CPAchecker`，与墙钟时间及完整进程组CPU时间不同。缺失值保留为空；成功耗时统计只使用得到确定判定的条目，各算法成功集合不同，不能仅按累计时间直接排名。

资源监测使用进程组RSS和CPU轮询，与严格的BenchExec/cgroup计量存在差异。本实验覆盖论文任务中的50个程序，每个程序—配置组合运行一次，结果可用于该子集的比较，不支持对论文全部任务性能或统计显著性的推断。

pcd的补充指标为配置差异提供线索，尚未通过单独切换参数的实验确认全部耗时差距的因果来源。vhost错误轨迹对应转换后的验证基准，不能直接推断真实驱动存在同一缺陷。

原始记录和哈希清单用于结果追溯，文件中的批次标识及服务器路径保持原样。
