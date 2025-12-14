# 本项目组成员
- 许天一 学号：25171111417
- 蔡小慧 学号：25171111442
- 蒋天健 学号：25171111416

# 本文件夹包括

- 一个报告：对我们小组的实验设计和ESBMC的理解的一个详细报告（必读）
- 一个视频：具体的代码讲解和结果展示（11min38s, 必看）
- 一个ppt：对我们实验的展示
- 一个三层的实验：从浅到深，挖掘如何用ESBMC
- 一组结果：logs展示的是三层实验的结果
- 具体的代码：esbmc && code文件夹
- 几个脚本：logs/run_all.sh可直接运行三层实验等

# ESBMC 教学示例套件

## 项目结构说明
- `code/`：全部 C 源码与 `run_all.sh`。按 Level 区分目录，文件名即示例主题。
  - `level1/`：数组越界、整数溢出、空指针等入门示例，每个文件同时包含故障版与修复版。
  - `level2/`：链表内存管理与嵌套循环调度，侧重动态内存、函数调用与复杂分支。
  - `level3/`：并发竞态和 watchdog 环境建模，演示 context bound 及有限环境假设。
- `docs/`：结构规划、讲解草稿等文档，方便整理 PPT/README 内容。
- `logs/`：自动脚本运行时输出的日志，会为每个示例生成独立的 `.log`。
- `code/run_all.sh`：一键执行所有 ESBMC 命令，自动分级输出日志。

## 运行说明
1. **准备 ESBMC**
   - 建议按照 [ESBMC 官方文档](https://esbmc.org/) 安装；在大多数 Linux/WSL 环境，可通过
     `sudo apt install esbmc` 或从源码编译。
   - 确保 `esbmc` 已加入 `PATH`。若可执行文件名称不同，可在运行脚本前导出 `ESBMC=/path/to/esbmc`。

2. **一键运行全部示例**
   ```bash
   bash code/run_all.sh
   ```
   - 脚本会按 Level 依次运行 bug 版与修复版，将输出写入 `logs/<示例名>.log`。
   - bug 版返回非零状态属预期（因为被验证器抓到问题），脚本不会中断。
   - 若想减少噪声，可自行编辑脚本中对应命令，比如删掉 `--trace`。

3. **单独运行一个示例**
   ```bash
   esbmc code/level1/level1_null_pointer.c --pointer-check --trace
   esbmc code/level1/level1_null_pointer.c --pointer-check --trace -DUSE_SAFE_VERSION
   ```
   - 约定：使用 `-DUSE_SAFE_VERSION` 切换到修复版函数；
     其他 Level 的示例也遵循同样的宏。
   - 可根据需要调整 `--unwind`、`--context-bound` 等参数，以验证不同深度。

4. **查看日志与 trace**
   - 每个 `.log` 首行会提示 PASS/FAIL。需要深入调试时，可在命令行额外加入 `--trace`
     或直接使用脚本生成的 trace。

## 验证要点总结
- **有界模型检测的界限含义**：`--unwind`、`--context-bound`、`--k-step` 等选项决定了
  搜索深度，示例展示了“界内正确、界外不保证”的真实含义。选址应结合工程经验——
  例如链表示例把 `--unwind` 设为 4，仅覆盖 3 个节点构造及一次删除。
- **典型错误类型与选项映射**：
  - 数组越界 → 默认启用的 bounds check，必要时可用 `--no-bounds-check` 关闭；配合 `--no-unwinding-assertions` 控制循环展开。
  - 有符号溢出 → `--overflow-check`。
  - 空指针与动态内存 → 默认 pointer check + `--memory-leak-check`。
  - 并发 → `--context-bound` 等调度限制。
  - 环境建模 → `__ESBMC_assume` 结合 `--k-step`。
- **消除特殊情况优先于补丁式分支**：每个修复版都回到“正常路径”：
  - 滑动窗口通过统一的索引裁剪，避免额外 if；
  - 链表删除先缓存 next，再 free，保证资源生命周期一致；
  - 并发示例使用互斥锁；watchdog 用 pending 队列把“忙碌时心跳”视为正常数据。
- **实用主义的验证流程**：
  - 先建模关键数据结构（数组窗口、链表、watchdog）；
  - 再选定最能暴露问题的界限，避免盲目放大状态空间；
  - 最后借助脚本自动跑通所有示例，把日志当成教学/答辩材料。
