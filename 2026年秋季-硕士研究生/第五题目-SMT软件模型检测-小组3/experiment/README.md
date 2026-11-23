# 实验数据

正式批次为 `formal-20261117-141308`。目录内有七份 CSV。

| 文件 | 内容 |
| --- | --- |
| `tasks.csv` | 22 个任务的编号、源文件、预期值、大小和 SHA256 |
| `runs.csv` | 88 条运行计划、对应任务和配置哈希 |
| `results.csv` | 88 次实际运行的结果及资源数据 |
| `algorithm_summary.csv` | 按算法汇总状态、已决数和 CPU 时间 |
| `status_summary.csv` | 各状态出现的次数 |
| `task_matrix.csv` | 22 个任务与四种算法的交叉结果 |
| `resolved_results.csv` | 23 次已决且符合预期的结果 |

统计见 `docs/experiment.md` 和 `docs/result_notes.md`。
