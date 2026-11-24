# DrvHorn 轻量实验复现

西安电子科技大学 2026 年秋季硕士研究生《数理逻辑》课程大作业，第一题目，第 5 小组。

我们运行了作者提供的 17 个轻量平台驱动，另跑了 1 个 TPM 文件操作案例。结合 TPM、GED 和 WMI 的源码与求解记录，我们分析了真实缺陷、未报告缺陷和已知误报三种情况。

DrvHorn 检查 Linux 驱动在初始化失败后能否把引用计数恢复到基准值。SeaHorn 将检查编码为约束 Horn 子句，由 Z3 查询断言失败的状态是否可达。

## 小组成员

| 姓名 | 学号 |
| --- | --- |
| 黄正鑫 | 26181214734 |
| 夏昱珩 | 26031110033 |
| 李鸿斌 | 26181214748 |

## 工具与参考资料

- [DrvHorn 开源项目](https://github.com/joehattori/drvhorn)
- [作者的轻量实验说明](https://github.com/joehattori/drvhorn#evaluation)
- [论文《Automatic Detection of Reference Counting Bugs in Linux Kernel Drivers》](https://arxiv.org/abs/2605.13246v2)

## 汇报材料与目录

- [课堂汇报 PPTX](./DrvHorn_课程汇报.pptx)
- [工具运行讲解视频（5 分 53 秒）](./DrvHorn_工具运行讲解.mp4)
- [实验报告](./evidence/实验结果与分析.md)
- [证据索引](./index.html)
- [三例证据速查](./evidence/实验分析/三例证据速查.html)

查阅已有结果时，解压提交包并打开与 PPTX 同目录的 `index.html`。课堂 PPT 第 14 页也有索引入口。

```text
evidence/
├── data/                 三例首次结果及 17 项逐项对照表
├── 环境配置/            运行脚本和环境记录
├── drvhorn/              作者轻量实验清单及相关工具源码
├── experiment-results/  首次三例和 17 项轻量实验的日志与汇总
├── 实验分析/            案例源码、实际求解文件和 WMI 补充轨迹
└── tools/                证据文件校验脚本
```

解压后，可在提交包根目录用 Python 3.8 或更高版本运行 `python ./evidence/tools/verify_evidence.py`。

## 复现方式

本组在 WSL2（Ubuntu 22.04.5 LTS）中使用 Docker。作者镜像内的 LLVM／Clang 版本为 14.0.0，Z3 版本为 4.8.9，实验输入是镜像自带的精简内核 bitcode。

1. 在 WSL 发行版内配置 Docker，确认 `drvhorn` 用户可以运行 Docker，并准备脚本中按摘要指定的作者镜像。脚本默认使用 `DrvHorn-Ubuntu22.04`，已有其他配置好的发行版时可用 `-Distro` 指定。[运行脚本](./evidence/环境配置/Run-Experiments.ps1) · [环境记录](./evidence/环境配置/setup-state.json)
2. 在解压目录打开 PowerShell，运行三个代表案例。

   ```powershell
   Set-Location -LiteralPath .\evidence
   & '.\环境配置\Run-Experiments.ps1' -Suite Selected -TimeoutSeconds 500
   ```

3. 在 `evidence/experiment-results/` 下按时间戳查找新生成的 `summary.json`、标准输出和错误日志。将命令中的 `Selected` 改为 `All`，即可运行 17 个轻量平台驱动。

## 实验结果

| 案例 | 本机首次输出 | 作者标签 | 案例判断 |
| --- | --- | --- | --- |
| TPM（`tpm_bios_measurements_ops`） | `sat` | `sat` | 打开失败时遗漏释放，属于真实缺陷 |
| GED（`ged_driver`） | `unsat` | `unsat` | 本次检查未报告引用计数错误 |
| WMI（`acpi_wmi_driver`） | `sat` | `unsat` | 复现作者记录的已知误报 |

17 个平台驱动得到 7 个 `sat` 和 10 个 `unsat`，其中 16 项与作者标签一致。唯一有差异的是 WMI，GED 和 WMI 都计入这 17 项。批次中断后，我们单独补跑了 GED，并在汇总里注明。[三例运行记录](./evidence/experiment-results/20261019-152023/summary.json) · [17 项汇总](./evidence/experiment-results/20261019-175330/summary.json)

逐项对照表列出本机输出、作者标签、补充材料中的输出和日志位置。表中的耗时是本机整次命令的运行时间，路径以 `evidence/` 为起点。[17 项逐项对照 CSV](./evidence/data/lightweight-comparison.csv) · [三例首次运行 CSV](./evidence/data/representative-cases.csv)

## 复现后的思考

TPM 和 WMI 都输出了 `sat`。沿着 TPM 的源码往下看，`get_device()` 把同一个设备的模型计数从 1 加到 2，打开失败后函数直接返回，引用没有归还。WMI 的补充轨迹会在空链表上进入遍历，源码在这个条件下会结束遍历。对照这两例后，我们判断告警时会先找准被检查的对象，再核对模型给出的分支在源码中能否走通。本机重求解确认了 WMI 模型中的错误可达，具体路径和计数取值来自补充轨迹。[本机求解输出](./evidence/实验分析/ir/acpi_wmi_driver/solver.stdout.txt) · [WMI 补充轨迹](./evidence/实验分析/外部材料核查/wmi.trace.txt)

GED 让我们回头查了送进求解器的内容。前端日志提示没有找到剩余断言，失败处理函数直接返回，后端收到的是 `(query false)`。这次 `unsat` 回答的是这个恒假查询。解读这类结果时，我们会先确认前端留下了哪些断言。[GED 的实际查询](./evidence/实验分析/ir/ged_driver/solver.smt2)

这次补跑也让我们体会到，汇总里要留着镜像摘要、每项的作者标签和原始日志位置。遇到有差异的结果，才能追到当时的运行条件和求解器输出。
