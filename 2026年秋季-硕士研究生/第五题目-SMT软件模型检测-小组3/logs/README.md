# 运行记录

这里只保留与正式环境和正式批次有关的部分日志，原来的排查过程与大多数临时记录没有全部复制进来。日志文件名保留了原始时间戳，方便与实验记录对应。

| 文件 | 内容 |
| --- | --- |
| `cpachecker-image-inspection-20261116-120014.log` | CPAchecker 与 Java 相关文件的检查 |
| `cpachecker-mathsat5-correct-key-20261116-121922.log` | MathSAT5 配置检查 |
| `cgroupsv2-build-20261116-202016.log` | Docker 镜像构建及镜像标识 |
| `cgroupfix-runtime-stdout-20261116-202209.log` | cgroups v2 和容器内存上限的检查 |
| `formal-plan-20261117-141308.report.txt` | 22 个任务、88 次运行的计划 |
| `formal-hardlimit-1200-20261117-141820.report.txt` | CPU 硬限制调整为 1200 秒的记录 |
| `formal-run-T05-20261117-142743.report.txt` | T05 余下三种算法的运行记录 |
| `formal-run-ALL-20261117-142858.report.txt` | 正式主批次运行和跳过已有记录的情况 |
| `formal-run-ALL-20261117-142858.summary.stdout.txt` | 汇总脚本读取到 88 条结果的输出 |
| `formal-run-ALL-20261117-142858.transcript.log` | 正式运行时保留的 PowerShell 记录 |

