# 案例文件

这里选了六个任务做具体说明。案例文件是从正式运行输出中复制的，原始 XML 统一放在 `results/`。

| 任务 | 本次结果                                                     | 适合说明的内容                                      |
| ---- | ------------------------------------------------------------ | --------------------------------------------------- |
| T01  | 四种算法均为 `false`，符合预期                               | 对比不同算法找到错误路径时的输出                    |
| T02  | BMC、k-induction 超时；predicate、Impact 均为 `true`，符合预期 | 对比不同算法验证同一个安全任务时的结果和耗时        |
| T03  | BMC、predicate 为 `unknown`，k-induction、Impact 超时；预期结果为 FALSE | 说明 `unknown` 不能作为已找到错误或已证明安全的结论 |
| T05  | k-induction、predicate、Impact 为 `true`；BMC 为 Java 堆不足 | 同一个安全任务下，不同算法的内存需求                |
| T06  | BMC、predicate、Impact 有递归相关错误；k-induction 内存不足  | 递归处理限制和资源耗尽是两类问题                    |
| T19  | 只有 Impact 得到 `true`；其余算法超时或 Java 堆不足          | 同一任务、相同限制下的结果差别                      |

## 文件内容

每个任务按算法分目录，例如 `T05/bmc/`。具体说明如下：

- `benchexec/*.results.*.txt`：BenchExec 生成的文本结果。
- `benchexec/*.logfiles.zip`：该次运行的日志归档。
- `cpa-output/CPALog.txt`：CPAchecker 的运行日志。
- `cpa-output/Statistics.txt`：CPAchecker 输出的统计数据。
- `cpa-output/Report.html`：可以直接在浏览器查看的报告。
- `cpa-output/ARG*.dot`、`Counterexample.*`：状态图和反例文件。
- `cpa-output/UsedConfiguration.properties`：当次运行采用的配置内容。
- `run-complete.txt`：原批次留下的完成标记。

总文件较大，`cases/` 只适当选择了部分，完整正式输出未全部呈现。
