# 结果说明

本批次共运行 88 次。15 次得到 `true`、8 次得到 `false`，均与任务预期一致；另外 65 次没有明确验证结论。

| 算法 | 已决正确 | 未决 | 已决正确结果的平均 CPU 时间（秒） |
| --- | ---: | ---: | ---: |
| BMC | 3 | 19 | 68.234 |
| k-induction | 8 | 14 | 54.932 |
| predicate | 4 | 18 | 12.189 |
| Impact | 8 | 14 | 21.282 |

各算法得到结论的任务并不相同，因此上表中的平均时间不能直接用来给四种算法排名。

## 未决状态

| 状态 | 次数 | 如何理解 |
| --- | ---: | --- |
| `TIMEOUT` | 30 | 运行达到时间限制，尚未给出结论。例如 T07/BMC。 |
| `OUT OF MEMORY` | 10 | BenchExec 按外部内存限制终止运行，不能直接等同于 Java 堆不足。 |
| `OUT OF JAVA MEMORY` | 6 | Java 堆耗尽，例如 T05/BMC 有 `java.lang.OutOfMemoryError: Java heap space`。 |
| `ERROR (recursion)` | 15 | 运行中发生与递归处理有关的错误。例如 T06/Impact。 |
| `ERROR` | 2 | T16、T17 的 k-induction 日志出现警告和异常，现有记录尚不足以确定更细的根因。 |
| `unknown` | 2 | CPAchecker 未能确定 TRUE 或 FALSE。例如 T03/BMC 的候选反例检查未完成。 |

本次对比基于选取的 22 个程序、当前工具版本和资源限制。
