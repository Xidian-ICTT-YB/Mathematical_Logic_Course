# 正式实验

## 任务和运行方式

正式批次为 `formal-20261117-141308`。22 个 C 程序编号 T01～T22，每个程序分别运行 BMC、k-induction、predicate 和 Impact，共 88 次。

运行前保存了 `tasks.csv` 和 `runs.csv`，记录任务和配置的哈希。运行脚本会在执行前检查输入文件是否变化。全部运行结果保存在 `results.csv`，原始 BenchExec XML 则放在 `results/`。

## 实验限制

CPU 软限制 900 秒、硬限制 1200 秒；使用 2 个 CPU 核、6000 MB 内存，Java 堆 4000 MB，BenchExec 同时运行 1 个任务。Docker 容器当时的根内存上限为 8 GiB，网络关闭。

正式运行开始前将 CPU 硬限制调整为 1200 秒，相关记录见 `logs/formal-hardlimit-1200-20261117-141820.report.txt`。

## 运行记录

先完成了 T05 的 4 次运行。之后的主批次检查全部 88 条计划，跳过已有结果和完成标记的 4 条，执行剩余 84 条。最终汇总读取到 88 条结果。

整理技术包时又检查了任务和配置的 SHA256、22×4 的组合、88 份压缩 XML 的解压与解析、XML 状态与 `results.csv` 的对应关系，以及原运行目录的完成标记。

## 统计口径

`true` 和 `false` 且与预期一致的结果计为已决正确结果；超时、内存不足、递归错误、其他错误及 `unknown` 均为未决。平均 CPU 时间只针对已决正确结果计算。详细数量见 `experiment/formal-20261117-141308/algorithm_summary.csv`，逐任务对照见 `task_matrix.csv`。
