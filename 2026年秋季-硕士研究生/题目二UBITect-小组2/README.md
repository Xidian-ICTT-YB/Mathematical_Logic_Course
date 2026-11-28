# 题目 2 · UBITect 两阶段检测复现

西安电子科技大学 2026 年秋季硕士研究生《数理逻辑》课程大作业，题目二，第 2 小组。我们复现了 UBITect 作者提供的 `backlog.c` 教程，并选取 Linux 驱动中的 `ahci_xgene` 案例，对比官方修复前后的函数级分析结果。

## 小组成员

| 序号 | 姓名 | 学号 |
| --- | --- | --- |
| 1 | 陈莹玉 | 26031110043 |
| 2 | 李文 | 26031212360 |
| 3 | 吴松烨 | 26031212356 |

## 工具与参考资料

| 工具或资料 | 我们使用的版本或来源 | 用途与参考地址 |
| --- | --- | --- |
| UBITect | 提交 `fb97a1554f6f` 的源码快照 | 生成未初始化使用候选；[上游项目](https://github.com/seclab-ucr/UBITect) · [随附源码说明](./ubitect-repro/source/UBITect/README.md) |
| LLVM / Clang | 7.0.0 | 将 C 程序编译为 LLVM 位码；[历史版本下载页](https://releases.llvm.org/7.0.0/) |
| KLEE | UBITect 随附的定制版本，构建时版本号为 1.4.0.0 | 根据候选记录探索目标路径；[KLEE 主页](https://klee-se.org/) |
| Z3 | 运行库 4.8.8，Python 包 `z3-solver==4.8.8.0` | 判断路径约束的可满足性，并重放导出的查询；[官方项目](https://github.com/Z3Prover/z3) |
| UBITect 论文 | ESEC/FSE 2020，作者提供的完整版本 | [论文 PDF](./ubitect-repro/source/UBITect/UBITect-FullVersion.pdf) |
| 历史驱动案例材料 | Linux `ahci_xgene` 修复前后源码与官方补丁 | [来源说明](./ubitect-repro/history/ahci_xgene/provenance/README.md) · [官方补丁副本](./ubitect-repro/history/ahci_xgene/provenance/official-fix.patch) |

我们使用的 UBITect 完整提交号为 `fb97a1554f6fc3a5e8b35f680a8bfe2b82a79848`。KLEE 来自该提交中的定制实现，由项目脚本编译。Z3 通过上述 Python 包安装，KLEE 链接包内的 `libz3.so`，查询重放也使用同一虚拟环境。各组件的许可和依赖来源见 [第三方组件说明](./ubitect-repro/THIRD_PARTY.md)。

## 项目内容

我们先将 C 程序编译为 LLVM 位码，由 UBITect 追踪变量的初始化状态并生成候选告警，再由 KLEE 从候选记录指定的函数入口探索路径，检查是否能够到达目标读取。为核对路径条件，我们保存了求解前导出的 SMT 查询，并用 Z3 重放。

教程实验检查的是 `backlog.c` 第 25 行的 `if (backlog)`。当 `a = 0` 时，第 22 行的赋值被跳过，第 25 行的条件判断仍会读取此前未初始化的指针。我们用 Z3 4.8.8 重放该路径的查询，得到 `sat`，模型中的 `input_0 = 0` 对应参数 `a = 0`。

我们的实验工作主要包括：

1. 固定源码与工具链，在同一容器环境下构建 UBITect、基本块命名工具和作者定制的 KLEE。
2. 设置 A–D 四组对照，分别观察报告去重、显式初始化和短路条件保护对检测结果的影响；对 `ahci_xgene` 的 H1/H2 使用相同接口桩比较官方修复前后的目标路径。
3. 在 KLEE 调用 Z3 求解前导出现有约束，保存查询与求解模型，并比较增加导出功能前后的确认位置。三项补丁分别处理构建兼容性、报告去重和查询导出，具体改动见 [补丁说明](./ubitect-repro/patches/README.md)。

## 实验结果

| 组别 | 实验设置 | 静态候选 | 路径确认 |
| --- | --- | ---: | ---: |
| A | 作者示例，默认报告去重 | 1（第 25 行） | 1（第 25 行） |
| B | 同一示例，关闭报告去重 | 2（第 25、26 行） | 2（第 25、26 行） |
| C | 将 `backlog` 初始化为 `NULL` | 0 | 0 |
| D | 使用短路条件保护对 `backlog` 的读取 | 1（第 25 行） | 0 |

历史驱动案例 `ahci_xgene` 的结果如下：

| 版本 | 目标候选对象数 | 目标确认对象数 | 目标 SMT 查询数 | 确认使用点 |
| --- | ---: | ---: | ---: | --- |
| H1：官方修复前 | 2 | 2 | 2 | 第 825 行，同一处源码使用 |
| H2：官方修复后 | 2 | 0 | 0 | 无 |

我们按报告对象统计“候选”和“确认”数量。H1 的两个确认对象对应同一处源码使用，因此不计为两个独立漏洞。详细结果见 [验收汇总](./verification/RESULTS.md) 和 [H1/H2 运行汇总](./verification/evidence/history/ahci_xgene/runs/HIST-20261112T075709Z/summary.json)。

## 汇报材料与目录

- [课程汇报 PPT](./UBITect-讲解PPT.pptx)
- [操作讲解视频（44 分 6 秒）](./UBITect操作讲解视频.mp4)
- [复现源码与构建配置](./ubitect-repro/README.md) · [源码说明](./ubitect-repro/source/UBITect/README.md) · [Docker 构建配置](./ubitect-repro/Dockerfile)
- [实验验收汇总](./verification/RESULTS.md) · [验收环境记录](./verification/ENVIRONMENT.json) · [实验产物索引](./verification/RESULTS.md#key-files)

```text
题目二UBITect-小组2/
├── README.md                         项目说明、成员和心得
├── UBITect-讲解PPT.pptx               课堂汇报
├── UBITect操作讲解视频.mp4             操作讲解与演示
├── ubitect-repro/
│   ├── Dockerfile                    容器构建配置
│   ├── REPRODUCE_ALL.sh               完整复现入口
│   ├── REPRODUCE.sh                   A–D 复现入口
│   ├── RUN_HISTORY.sh                 H1/H2 复现入口
│   ├── DEMO.sh                        分步演示入口
│   ├── source/UBITect/                作者源码快照及论文
│   ├── patches/                      构建、报告与查询导出补丁
│   ├── scripts/                      构建、运行和结果核验脚本
│   └── history/ahci_xgene/            历史源码、接口桩及来源记录
└── verification/
    ├── RESULTS.md                    已归档验收结果与文件索引
    ├── ENVIRONMENT.json              验收环境记录
    ├── COMMANDS.md                   验收时使用的命令
    ├── SHA256SUMS                    验收文件校验清单
    └── evidence/                     原始运行结果、日志及 SMT 查询
```

## 实验环境与复现方式

我们的编译和分析均在 `linux/amd64` 容器中完成，实验环境如下：

| 项目 | 实际运行记录 |
| --- | --- |
| 容器系统与架构 | Ubuntu 24.04.5 LTS，x86_64（`linux/amd64`） |
| 实验虚拟环境 Python | 3.12.16 |
| CMake | 3.31.10 |
| uv | 0.13.6 |

LLVM/Clang、KLEE 和 Z3 的版本见上表“工具与参考资料”，对应的 [工具链运行记录](./verification/evidence/logs/toolchain-versions.txt)和 [KLEE 构建日志](./verification/evidence/logs/reproduce-20261112T075710Z.log)保存在验收材料中。

复现前需安装支持 `linux/amd64` 的 Docker，并准备 Bash、Python 3.9 或更新版本，以及 `curl` 或 `wget`。首次执行需要联网下载镜像和依赖。

在本小组文件夹打开终端，完整复现命令为：

```bash
cd ubitect-repro
./REPRODUCE_ALL.sh
```

脚本依次执行工具构建、A–D 实验、H1/H2 实验和结果检查。全部检查通过后，终端输出 `FULL REPRODUCTION: PASS`，检查结果保存在 `artifacts/ACCEPTANCE.json`。首次执行需要下载依赖并编译工具，运行时间取决于网络和机器配置。

以下命令均在 `ubitect-repro/` 目录运行：

| 命令 | 作用 |
| --- | --- |
| `./REPRODUCE.sh` | 只运行 A–D；首次执行会构建所需镜像与工具 |
| `./RUN_HISTORY.sh` | 只运行 H1/H2；缺少工具时先完成构建 |
| `./DEMO.sh start` | 完成首次构建后，启动或复用分步演示容器 |
| `./DEMO.sh source tutorial` | 查看教程示例源码；其他步骤包括 `compile`、`candidates`、`verify`、`constraints` 和 `compare` |

运行后，A–D 结果保存在项目的 `artifacts/`，历史案例结果保存在 `history/ahci_xgene/runs/` 下以运行编号命名的目录，执行日志保存在 `logs/`。我们将已完成验收的文件另存于 `verification/`；重新运行脚本时，新结果与这份验收记录分别保存。

## 结果文件与核验

我们在 `verification/` 中保留了结果汇总和原始产物。查阅已有结果可从以下文件开始：

| 文件 | 查看内容 |
| --- | --- |
| [验收汇总](./verification/RESULTS.md) | A–D 与 H1/H2 的结果、运行编号和关键文件索引 |
| [ACCEPTANCE.json](./verification/evidence/artifacts/ACCEPTANCE.json) | 每项预期结果检查及总体 `ok` 状态 |
| [A 组 warnings.json](./verification/evidence/artifacts/A_original_default_dedup/warnings.json) | 第一阶段生成的候选记录，包括函数、目标使用点和路径引导字段 |
| [A 组 confirm_result.json](./verification/evidence/artifacts/A_original_default_dedup/confirm_result.json) | 原始 KLEE 构建的路径确认记录 |
| [A 组 query.smt2](./verification/evidence/artifacts/A_original_default_dedup/candidates/candidate-01-line-25/klee-smt-export/query.smt2) | 求解前导出的真实路径约束 |
| [A 组 z3-replay.json](./verification/evidence/artifacts/A_original_default_dedup/candidates/candidate-01-line-25/klee-smt-export/z3-replay.json) | 对该查询的 Z3 重放结果、模型与版本 |

核对提交的验收文件是否完整时，可在本小组文件夹执行：

```bash
cd verification
shasum -a 256 -c SHA256SUMS
```

Linux 上也可使用 `sha256sum -c SHA256SUMS`。该清单覆盖验收材料；源码快照另有独立校验，可在 `ubitect-repro/` 目录运行 `bash scripts/verify_source_snapshot.sh`。

## 结果的适用范围

我们复现的范围是作者教程的四组对照，以及 `ahci_xgene` 目标函数在官方修复前后的分析。历史案例保留目标函数的控制流，用桩函数提供所需的内核类型和接口；具体对应关系见 [函数与接口桩映射](./ubitect-repro/history/ahci_xgene/HARNESS_MAPPING.md)。

本文的 `sat` 表示导出的约束在当前模型中有满足赋值，结论依赖相应的路径条件和接口假设。我们分别记录“未确认”“未生成目标查询”和求解器返回 `unsat`，不将三者合并。实验未覆盖论文的全量内核任务，也未运行完整内核或硬件，因此不据这些案例计算总体准确率、召回率或评价工具的整体检测能力。

## 小组心得

分析 `backlog.c` 时，我们注意到 `if (backlog)` 本身就会读取指针的值。`a = 0` 时，前面的赋值被跳过，后面的判空仍可能读取未初始化的指针。C 组通过赋予初值 `NULL` 解决这一问题；D 组利用 `&&` 的短路规则，在未执行赋值的路径上跳过读取。对照两组的源码和输出，可以看到修复既可以从变量初值入手，也可以通过调整读取条件实现。

D 组保留了静态候选，但路径确认数为 0，使我们对两阶段分析的作用有了更具体的理解：第一阶段定位可能存在问题的读取，第二阶段进一步检查相关路径是否可行。A、B 两组则说明了报告设置对数量的影响。关闭去重后，第 25、26 行分别得到确认，但它们来自同一个未初始化根因。因此，我们在汇总时同时保留候选对象数和源码使用位置，避免只比较告警条数。

将 SMT 查询与源码对应，是我们理解求解结果的关键一步。A 组得到的 `input_0 = 0` 能够解释源码中跳过初始化的分支，也把课堂中的可满足性判断与具体程序路径联系起来。H2 没有生成目标查询，则提醒我们区分分析流程中的不同结果：没有查询，不能表述为求解器已经返回 `unsat`。

在历史案例中，我们将修复前后代码置于相同的接口失败模型下，观察到 `else if` 阻断了失败后的目标读取。这个对照能说明补丁在当前模型中的作用，同时也要求我们交代桩函数的假设。函数级分析便于检查关键控制流，但其结论仍有范围限制，不能代替完整内核环境中的验证。

整理材料时，我们将源码提交、依赖版本、运行命令和原始产物一并保存。这样，汇总表中的每个结果都能找到相应记录，后续复查也能区分代码改动、报告设置和运行环境带来的影响。完成这次实验后，我们更重视对结果依据的说明：除了报告候选和确认数量，还应解释对应路径、模型假设与结论范围。
