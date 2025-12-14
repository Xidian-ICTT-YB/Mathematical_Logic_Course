# 项目结构与示例总体方案

## 1. 目录结构
```
.
|-- code/
|   |-- level1/
|   |   |-- level1_array_bounds.c
|   |   |-- level1_integer_overflow.c
|   |   `-- level1_null_pointer.c
|   |-- level2/
|   |   |-- level2_linked_list_memory.c
|   |   `-- level2_loop_logic.c
|   `-- level3/
|       |-- level3_concurrency_race.c
|       `-- level3_environment_model.c
|-- docs/
|   |-- structure_plan.md
|   `-- tech_notes.md (后续补充验证思路)
|-- logs/ (运行脚本输出)
|-- Plan.md
`-- README.md (待生成)
```

## 2. Level 1 示例
- `level1_array_bounds.c`：循环上界与条件组合造成的数组越界；展示 `--unwind`、`--no-unwinding-assertions` 控制循环展开。
- `level1_integer_overflow.c`：多步累加后的无符号/有符号溢出；强调 `--overflow-check` 默认能力，以及为何普通测试不易发现。
- `level1_null_pointer.c`：条件路径导致的空指针解引用；配合 `--pointer-check` 与 `--trace` 观察反例。
  - 目标：证明 ESBMC 可以自动扫描出入门级 bug，并解释常用检测开关。

## 3. Level 2 示例
- `level2_linked_list_memory.c`：链表删除路径造成的泄漏与 use-after-free；需要 `--memory-leak-check` 与 `--pointer-check`。
- `level2_loop_logic.c`：带计数器与断言的嵌套循环逻辑，要求设置 `--unwind` 并解释为何 unwinding-assertions 重要；同时涵盖函数调用与局部状态。
  - 目标：训练对循环、函数以及动态内存的建模，展示 BMC 在有限深度内涵盖复杂路径。

## 4. Level 3 示例
- `level3_concurrency_race.c`：两个线程竞争更新共享计数器，分别给出无锁与加锁版本，强调 `--context-bound`、`--unwind`、`--sched` 等并发选项。
- `level3_environment_model.c`：模拟设备输入状态机（例如 watchdog 喂狗），需要建模有限环境，证明某条性质在界内成立；突出状态编码与断言设计。
  - 目标：展示 ESBMC 在并发、环境抽象与复杂性质验证上的能力。

## 5. 推荐扩展
- 将链表示例扩展为环形缓冲区，结合 `--k-step` 探索更深界限。
- 引入 `--floatbv` 的浮点运算例子，展示实际与理想模型差异。
- 在并发示例中加入 `pthread_cond_t`，讨论条件变量与状态空间爆炸。
- 撰写脚本自动统计验证时间，便于课堂展示不同示例的复杂度差异。
