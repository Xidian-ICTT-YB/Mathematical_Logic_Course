# 指标定义表

本文件先于测量编写。所有数值都来自 `metrics/raw/` 的原始输出，图表只读取
`metrics/results.csv`、`metrics/resources.csv` 和 `metrics/summary.json`。

## 1. 功能指标

| 指标 | 定义 |
|---|---|
| `warning_objects` | `warnings.json` 流中 JSON 对象数量；一个对象是一个报告的使用点记录 |
| `independent_use_points` | 去重后的源码使用位置（案例级）；同一行的多个分析节点可共享一个 use 点 |
| `target_warning_objects` | 与当前历史目标源码行对应的 warning 对象数量；backlog 的目标由案例定义 |
| `target_confirmed_objects` | 目标 warning 对象中 KLEE 写出 `find:"Yes"` 的对象数 |
| `target_confirmed_use_points` | 目标已确认 use 点去重数 |
| `klee_candidates_run` | 实际调用了定制 KLEE 的候选数 |
| `timeouts` | 超过 120 秒被终止的 KLEE 调用数 |
| `errors` | 非零退出码的候选 KLEE 调用数（不等同于未确认） |
| `solver_status` | 真实导出的 Z3 重放结果：`sat` / `unsat` / `unknown` / `none` |
| `repeat_consistency` | 同一测量阶段 3 次独立顺序运行的确认数/求解状态是否一致 |

“候选告警对象”“独立缺陷根因”“use 点”不是同一个量。历史 H1 有 2 个同源
warning 对象（指针 load 与字段读取），但只有 1 个 use 基本块/源码行；本报告
不把 2 个对象说成 2 个独立缺陷。

未确认不等于误报。必须区分：路径不满足、KLEE 未到达 use、超时、UNKNOWN、
真实错误，以及尚未运行。

本报告只讨论选定案例，不计算通用准确率、召回率、F1 或“检测率”。

## 2. 性能与资源指标

| 指标 | 定义 / 单位 | 获取方式 |
|---|---|---|
| `wall_s` | 单次命令墙钟时间，秒 | Python `time.monotonic()` |
| `max_rss_kb` | 单次进程（不含子进程可能的内存）峰值 RSS，KiB | 容器内 `/usr/bin/time -v` 的 `Maximum resident set size` |
| `cgroup_current_bytes` | 测量开始/结束时容器 cgroup 当前内存，字节 | `/sys/fs/cgroup/memory.current` |
| `cgroup_peak_bytes` | 容器 cgroup 生命周期峰值，字节；不是单阶段峰值 | `/sys/fs/cgroup/memory.peak`（如可读） |
| `vm_configured_memory_mib` | Docker Desktop VM 配置内存，MiB | backend settings |
| `vm_configured_cpus` | Docker Desktop VM 配置 CPU 数 | backend settings |
| `artifact_bytes` | 产物目录字节数 | `du -sb` |
| `disk_available_bytes` | 宿主/容器可用空间，字节 | `df` |
| `build_first_time` | 首次构建时间 | 冷构建没有在本轮重新执行；只报告日志/镜像时间，无法可靠给出时写 `unavailable` |

`max_rss_kb` 是进程峰值，不是容器内存，也不是 Docker VM 内存，更不能把配置的
8 GiB 当作实际峰值。cgroup 值如果不是按单阶段重置，只作为容器总量记录。

## 3. 测量边界

- 每个关键阶段顺序重复 3 次：编译、BBTag、候选分析、KLEE、Z3 重放。
- 版本、输入位码、warning JSON、KLEE 二进制、timeout、并行度保持一致。
- 每次 KLEE 都使用独立输出目录；不使用前一次的结果冒充本次结果。
- 准备阶段（首次编译/链接）与重复测量分开；准备时间不计入 KLEE 统计。
- 演示运行使用新的运行编号；指标测量不覆盖 A–D 或历史案例证据。
- 无法可靠获得的值不填零；在 `resources.csv` 中写 `NA` 并在报告说明。

## 4. 逐候选 KLEE 记录

`metrics/candidate_timings.csv` 从每次真实运行的 `result.json` 提取每个候选的
KLEE 原版/导出构建耗时、返回码、确认状态和 SMT 是否导出。它是逐候选运行记录，
不是 3 次重复测量；3 次重复的聚合统计见 `resources.csv` 和 `summary.json`。
