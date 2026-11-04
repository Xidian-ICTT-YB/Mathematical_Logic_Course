# QCP 大作业：LiteOS 双向链表验证复现与分析

> 课程：数理逻辑大作业  
> 题目方向：SAT/SMT 与形式化验证——基于 QCP 的 OpenHarmony/LiteOS 内核链表验证

## 小组成员

| 成员 | 学号 | 分工 |
| --- | --- | --- |
| 戴子琛 | 24009300251 | 环境搭建、QCP 案例复现、PPT排版与整合 |
| 陈怡蓉 | 24009290072 | 环境搭建、规约与验证条件分析、视频录制 |
| 崔家诚 | 24009290051 | 环境搭建、OpenHarmony 源码对照、报告与演示 |

## 任务简介

本项目复现 QCP 中 LiteOS 双向链表的初始化、插入和删除案例，研究带逻辑规约的 C 程序如何通过符号执行、分离逻辑和轻量自动求解生成验证条件（VC），并由 Rocq/Coq 后端检查证明工件。

选取的三个 C 输入文件为：

| 文件 | 主要函数 | 核心行为 |
| --- | --- | --- |
| `LOS_ListInit.c` | `LOS_ListInit` | 令表头的前驱和后继都指向自身，建立空循环双向链表 |
| `List_Add.c` | `LOS_ListAdd`、`LOS_ListTailInsert`、`LOS_ListHeadInsert` | 用局部指针重连完成插入操作 |
| `LOS_ListDelete.c` | `LOS_ListDelete` | 修复相邻节点的链接，并清空被摘节点的两个链接字段 |

项目还对照 OpenHarmony LiteOS-A 的 `los_list.h`，比较对应函数的指针更新顺序。源码对照说明案例与实际内核实现具有对应关系，但不等于已证明整个 OpenHarmony 内核或两套规约形式化等价。

## 工具与材料来源

| 工具/材料 | 用途 | 来源 |
| --- | --- | --- |
| QCP | 符号执行、VC 生成和 Rocq 证明工件生成 | [项目主页](https://github.com/QinxiangCao/QualifiedCProgramming)，[v1.0 工件](https://github.com/QinxiangCao/QualifiedCProgramming/releases/tag/v1.0) |
| QCP 论文 | 工具原理、系统架构与实验背景 | [QCP: A Practical Separation Logic-based C Program Verification Tool](https://arxiv.org/abs/2505.12878) |
| Rocq/Coq | 检查生成的 `.v` 证明文件 | [Rocq 官网](https://rocq-prover.org/) |
| Coq Platform | Windows 下安装 Coq、OCaml、`coqc` 与 `vscoqtop` | [Coq Platform GitHub](https://github.com/coq/platform) |
| Dune | 构建 Rocq 工程和 `.vo` 证明对象 | [Dune 官网](https://dune.build/) |
| Visual Studio Code | 代码编辑、QIDE 和 VsCoq 的运行平台 | [VS Code 官网](https://code.visualstudio.com/) |
| QIDE | 在 VS Code 中交互执行带注释的 C 文件、查看当前位置断言 | [QIDE Git 仓库](https://bitbucket.org/WxWyashen/qide-extension.git)；本项目 `QualifiedCProgramming-main/qide.vsix` |
| VsCoq | 在 VS Code 中查看、交互检查 Rocq `.v` 文件 | [VsCoq GitHub](https://github.com/coq-community/vscoq)；本项目 `QualifiedCProgramming-main/vscoq-2.2.3.vsix` |
| OpenHarmony LiteOS-A | 对照 `LOS_ListAdd` 等内核链表实现 | [kernel_liteos_a](https://github.com/openharmony/kernel_liteos_a) |

## 基本原理

```text
带 /*@ ... */ 规约的 C 程序
          ↓
QCP 符号执行与断言处理
          ↓
验证条件（VC）及 *_goal.v、*_proof_auto.v、*_proof_manual.v
          ↓
分离逻辑蕴含求解、策略规则与轻量自动求解
          ↓
Rocq/Coq 检查最终 *_goal_check.v 入口
```

`Require` 表示调用前必须拥有的资源和条件，`Ensure` 表示函数执行后应满足的状态，`With` 声明规约中的逻辑参数。分离逻辑使用分离合取描述彼此不重叠的堆资源，因此能够将局部的指针更新与未修改的链表区域组合推理。

QCP 对 C 语句做符号执行，生成安全性、返回条件、局部求解和规约派生等验证条件。自动策略、分离逻辑蕴含推理和轻量求解处理一部分子目标；无法自动完成的目标保留在手工证明文件中，最终由 Rocq/Coq 后端检查。

## 运行环境

本项目当前在 Windows 原生环境中进行演示与构建。

| 组件 | 版本/配置 |
| --- | --- |
| 操作系统与终端 | Windows + PowerShell |
| Rocq/Coq | 8.20.1 |
| OCaml | 4.14.2 |
| Dune | 3.16.1 |
| 编辑器 | Visual Studio Code |
| C 代码交互界面 | QIDE（由 `qide.vsix` 安装） |
| Rocq 证明交互界面 | VsCoq 2.2.3（由 `vscoq-2.2.3.vsix` 安装） |

QIDE 与 VsCoq 的工作区配置位于 [`QualifiedCProgramming-main/.vscode/settings.json`](QualifiedCProgramming-main/.vscode/settings.json)。QIDE 使用 `win-binary/lsp.exe`，VsCoq 使用 Coq Platform 提供的 `vscoqtop.exe`。

## 工具搭建与运行方法

### 1. 安装编辑器插件

在 VS Code 中执行 **Extensions: Install from VSIX...**，依次安装：

```text
QualifiedCProgramming-main/qide.vsix
QualifiedCProgramming-main/vscoq-2.2.3.vsix
```

安装完成后重新加载 VS Code 窗口。不要同时启用 VsRocq 与 VsCoq，以免两种 Rocq 编辑器扩展发生冲突。

### 2. 检查环境

在 PowerShell 中进入 QCP 工程目录：

```powershell
Set-Location 'D:\0xidian\数理逻辑大作业\QualifiedCProgramming-main'
coqc --version
.\dune.cmd --version
```

### 3. 构建三个最终检查目标

```powershell
.\dune.cmd build -j1 Rocq/examples/Applications_human/LiteOS/LOS_ListInit_goal_check.vo
.\dune.cmd build -j1 Rocq/examples/Applications_human/LiteOS/List_Add_goal_check.vo
.\dune.cmd build -j1 Rocq/examples/Applications_human/LiteOS/LOS_ListDelete_goal_check.vo
```

构建成功后，Dune 会在 `_build/default/Rocq/examples/Applications_human/LiteOS/` 下生成对应的 `.vo` 二进制证明对象。`.vo` 不是文本文件，不能用编辑器直接阅读；应根据 Dune 命令无报错结束和目标文件生成来判断构建是否成功。

### 4. 使用 QIDE 查看符号执行状态

打开 [`List_Add.c`](QualifiedCProgramming-main/QCP_examples/Applications_human/LiteOS/List_Add.c)，将光标移到第 140—143 行的四条指针更新语句，按 `Alt + →`，或在命令面板执行 `QIDE: Interpret To Point`。右侧 **Current Assertions** 面板会显示当前程序点的断言状态、函数规约推导关系及自动化边界。

## 实际结果(具体可见main文件夹)

### 三个案例构建

已对初始化、插入和删除三个案例执行 `goal_check` 构建目标，三个目标均无报错完成：

| 案例 | 最终检查目标 | 结果 |
| --- | --- | --- |
| 初始化 | `LOS_ListInit_goal_check.vo` | 构建通过 |
| 插入 | `List_Add_goal_check.vo` | 构建通过 |
| 删除 | `LOS_ListDelete_goal_check.vo` | 构建通过 |

### QIDE 交互展示

在 `List_Add.c` 的第 140 行执行到指定程序点后，QIDE 已能显示：

- `Function: LOS_ListAdd`；
- **Current Assertions**：当前位置的堆断言；
- `high_level_spec / low_level_spec`：高层规约与低层规约的推导关系；
- **Needs manual proof**：该状态存在自动化未直接完成的证明义务。

这表明 QIDE 已正确连接 QCP 语言服务器并刷新当前位置状态。`Needs manual proof` 不是 C 程序运行错误，而是说明该义务仍需通过后续证明工件和 Rocq 后端处理。

### List Add 与 OpenHarmony 对照

`List_Add.c` 第 140—143 行的插入核心为：

```c
node->pstNext = list->pstNext;
node->pstPrev = list;
list->pstNext->pstPrev = node;
list->pstNext = node;
```

OpenHarmony 当前 `master` 分支的 [`LOS_ListAdd`](https://github.com/openharmony/kernel_liteos_a/blob/master/kernel/include/los_list.h#L178-L184) 在第 180—183 行采用同样顺序的四条指针更新：先保存旧后继，再设置新节点前驱，随后回写旧后继前驱和表头后继。

### 证明边界

`goal_check` 构建通过表示当前工程的证明接口和已有工件能够被 Rocq 编译检查；它不等价于所有验证条件都已经无假设证明。作者工件的自动证明文件中仍可看到 `Admitted` 占位，因此汇报中不能把构建成功表述为“全部 VC 已完整自动证明”。

## 工具搭建与任务完成后的思考

1. **QIDE、QCP 和 Rocq 的分工不同。** QIDE 用于在 C 代码层观察符号执行和断言状态；QCP 负责生成 VC 及对应证明文件；VsCoq/Rocq 负责检查 `.v` 证明工件。
2. **分离逻辑适合链表局部更新。** 四条 C 赋值只改动新节点、表头和旧后继附近的字段；分离逻辑可以将这些局部资源与未改动的链表片段组合起来推理。
3. **自动化有明确边界。** 自动策略和轻量求解可处理一部分 VC，但并不能保证所有目标自动完成。界面中的 `Needs manual proof` 和自动文件中的 `Admitted` 都说明仍需要人工证明或进一步审计。
4. **构建成功不等于完全证明。** `.vo` 成功生成说明当前证明工件可被检查；若存在 `Admitted`、公理或模型参数，还必须如实说明证明依赖和限制。
5. **源码对照不等于形式化等价。** QCP 样例与 OpenHarmony 函数的指针更新顺序一致，支持案例的工程相关性；但若要证明真实内核调用场景，还需要覆盖宏、类型、平台语义、调用前提和完整构建上下文。

## 项目结构与交付物

```text
.
├─ QualifiedCProgramming-main/        # QCP 源码、二进制、Rocq 库和 LiteOS 案例
│  ├─ QCP_examples/Applications_human/LiteOS/
│  ├─ Rocq/examples/Applications_human/LiteOS/
│  ├─ qide.vsix
│  └─ vscoq-2.2.3.vsix
├─ result/
│  ├─ QCP_OpenHarmony链表验证大作业报告.docx
│  ├─ QCP_LiteOS链表验证汇报_完善版.pptx
│  └─ 视频/录屏脚本.md
└─ README.md
```

- [完整报告](result/QCP_OpenHarmony链表验证大作业报告.docx)
- [汇报 PPT](result/QCP_LiteOS链表验证汇报_完善版.pptx)
- [视频录制脚本](result/视频/录屏脚本.md)
