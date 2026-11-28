# PPT 逐页内容方案（12 页，10–12 分钟，v3）

> **v3（2026-11-04）：** 标准案例名 **example**；第 3 页加入宿主 → Docker
> Desktop → 项目容器 → Clang/UBITect/KLEE/Z3 的运行拓扑。当前证据来自
> `DEMO-20261104T065000Z/example`、`HIST-20261104T065006Z/history` 和
> `demo/verification-20261104T064956Z.json`。旧 tutorial 运行只作归档。


## 0. 定位、页数与统一规则

**中心命题：SMT 求解在未初始化使用缺陷路径验证中的应用。**
本方案不是“UBITect 工具介绍 + 结果罗列”，而是围绕一条可检查的链条展开：

```text
UBITect 用初始化状态/类型限定符产生候选
        ↓  同一份 warning JSON
KLEE 从函数入口做路径探索，收集目标 use 的路径条件
        ↓  真实导出 query.smt2
Z3 判断路径条件是否可满足；SAT 给出模型
        ↓
结合初始化事实解释：候选是否被确认，为什么不是现实崩溃
```

**页数：保留 12 页。** 不增加到 13–14 页。理由：

- 12 页覆盖“问题—两阶段—真实求解链—A/B/C/D—历史补丁—H1/H2—资源—边界”，
  每页一个中心证据；再加页会把历史源码和求解器讲成两段重复内容。
- 用户要求 10–12 分钟；本方案按 **11 分 20 秒**设计，留约 40 秒缓冲。
- 环境信息压缩进第 1/3 页的边栏和备注，不单独占一页；完整环境仍可在提问时
  打开 `ENVIRONMENT.md`。
- H1/H2 的“源码补丁”和“求解结果”必须分开：第 9 页回答“补丁改变了什么
  控制流”，第 10 页回答“本次实际确认了几个对象、有没有 query”。

**统一版式规则：**

- 每页只保留 3–5 条正文 bullet；完整日志、长 IR、变量表、SHA 放备注/附录。
- 投影正文不小于 20 pt；代码不小于 16 pt；SMT 摘录最多 8 行、不小于 14 pt。
- 真实查询标注“真实导出”；等价简化标注“等价简化（教学表达）”；独立公式
  标注“独立教学重建，不是 KLEE 日志”。
- 每页页脚保留一个“证据路径”，不把路径写成不可点击的口号。
- 不出现“漏洞数 = 候选数/确认数”的写法。

**时间预算：**

| 页 | 内容 | 目标秒数 | 累计 |
|---:|---|---:|---:|
| 1 | 封面与任务 | 40 | 0:40 |
| 2 | 问题与两个案例 | 50 | 1:30 |
| 3 | 运行位置与三工具分工 | 65 | 2:35 |
| 4 | 第一阶段：候选 | 55 | 3:30 |
| 5 | 第二阶段：KLEE 路径 | 60 | 4:30 |
| 6 | 求解器核心 A/B 完整链 | 70 | 5:40 |
| 7 | 读 query 与状态语义 | 60 | 6:40 |
| 8 | A–D 结果 | 55 | 7:35 |
| 9 | 历史补丁、入口、桥接 | 60 | 8:35 |
| 10 | H1/H2 实际结果 | 65 | 9:40 |
| 11 | 性能与资源边界 | 55 | 10:35 |
| 12 | 结论与限制 | 45 | 11:20 |

---

## 第 1 页：封面与任务

**正式标题：** SMT 求解在未初始化使用缺陷路径验证中的应用

**副标题：** UBITect 两阶段复现：`backlog.c` 示例与 `ahci_xgene` 历史案例

**核心结论：** 本项目复现的不是“一个会报错的脚本”，而是“候选生成 → KLEE
路径条件 → SMT 查询 → Z3 可满足性”的可复算链条；结论限定在函数级模型内。

**页面正文（可直接上屏）：**

- 论文：UBITect，ESEC/FSE 2020；上游 `seclab-ucr/UBITect` @ `fb97a15`
- 任务：复现两阶段分析，保留 A–D、H1/H2 的真实查询与结果
- 主题：**UBITect 找候选，KLEE 走路径，Z3 判可满足**
- 工具：LLVM/Clang 7.0.0、作者定制 KLEE 1.4.0.0、Z3 4.8.8
- 边界：函数级带桩模型；不是完整内核、硬件运行或漏洞利用

**一句话版本：** “我们验证的是：在给定初始化事实和路径引导下，目标 use 的
路径公式是否可满足；不是验证现实系统一定会崩溃。”

**推荐版式：** 左侧标题与五行范围；右侧三枚纵向标签：

```text
UBITect  初始化状态 / 类型限定符 → 候选
KLEE     从函数入口探索 / 收集路径条件
Z3       对已有断言做 SAT / UNSAT / UNKNOWN
```

底部一条细线：“Python、uv、Docker 是驱动和环境，不参与语义判断”。

**使用素材：** `ppt_assets/figures/two_stage_flow.png`（只作右下角缩略图，不
在本页展开）；`README.md`；`artifacts/SUMMARY.md`。

**讲稿（约 40 秒）：**

> 这次汇报的主题是 SMT 求解在未初始化使用缺陷路径验证中的应用。我们复现
> UBITect 的两阶段方法：第一阶段用初始化状态和类型限定符产生候选；第二阶段
> 用 KLEE 从函数入口探索路径、收集目标 use 的条件，再把真实查询交给 Z3 判断
> 可满足性。案例只有示例 `backlog.c` 和历史函数 `xgene_ahci_probe`，结论都在
> 函数级模型内，不是完整内核运行。

**证据：** `README.md`、`demo/verification-20261104T064956Z.json`、`artifacts/SUMMARY.md`。

**必要限定：** 不把“复现两阶段流程”说成“复现论文全部实验”；不把 SAT 说成
“真实崩溃”。

**衔接：** “先看这个实验到底检测什么，以及示例和历史案例各自扮演什么角色。”

---

## 第 2 页：问题与两个案例的角色

**正式标题：** `if(backlog)` 本身已经读取了未初始化指针

**核心结论：** 未初始化使用不一定发生在 `->` 解引用；条件判断必须先 `load`
指针，读取本身已经是 use。示例负责可控对照，历史案例负责真实函数切片。

**页面正文：**

```c
struct test_struct *backlog;      /* 18: 声明，未赋值 */
if (a) backlog = init;           /* 22: 仅 a != 0 才写 */
if (backlog) {                   /* 25: 先 load，已经是 use */
    backlog->irq = 0;            /* 26: 更晚的解引用 */
}
```

- **示例 A–D**：控制变量，分别看默认报告、关闭去重、`NULL` 初始化、短路保护；
- **历史 H1/H2**：`xgene_ahci_probe` 的真实函数切片 + 失败模式桩；
  H1 是修复前父提交，H2 是官方 `else if` 修复后；
- 两者都不是完整内核；示例用于讲清机制，历史案例用于检验真实代码上的同一条
  求解链。

**“两个案例各回答什么”小表：**

| 对象 | 回答的问题 | 不能回答的问题 |
|---|---|---|
| 示例 A–D | 候选、报告粒度、初始化、短路怎样改变结果 | 真实驱动安全性、通用准确率 |
| 历史 H1/H2 | 官方补丁是否改变失败路径的目标可达性 | 成功路径、完整硬件、所有 ACPI 错误 |

**推荐版式：** 左侧代码占 55%，右侧上下两块“示例/历史”角色卡；代码只高亮
第 25 行 `if(backlog)` 和第 33 行 `%8 = load`，不要高亮整个函数。

**使用素材：** `ppt_assets/code/backlog_snippet.c`；
`artifacts/A_original_default_dedup/backlog.c:18-26`；
`ppt_assets/figures/backlog_cfg.png`（右下角小图）。

**讲稿（约 50 秒）：**

> 这段代码的关键不是第 26 行的箭头，而是第 25 行的 `if(backlog)`。C 必须先
> 把指针值读出来，才能判断真假；这个 load 本身就是未初始化使用。`a=0` 时
> 第 22 行不执行，指针没有被写过。示例用 A 到 D 四个受控版本讲清报告和路径
> 的差别；历史案例则把同样的两阶段放到真实的 `xgene_ahci_probe` 函数切片上。
> 两者都不是完整内核，用途不同。

**证据：** `artifacts/A_original_default_dedup/backlog.c:18-26`；
`artifacts/A_original_default_dedup/backlog.ll:23-35`；
`history/ahci_xgene/source/`；`HARNESS_MAPPING.md`。

**必要限定：** “未初始化”指某条路径上没有写入，不等于值一定是零，也不等于
一定崩溃；第 26 行只是更晚的第二个使用点。

**衔接：** “这三个工具在一条真实流水线上各自做什么？”

---

## 第 3 页：运行位置与三工具分工

**正式标题：** 宿主 → Docker → 项目容器 → UBITect/KLEE/Z3

**核心结论：** Docker 只提供运行环境，不是分析工具；真正的执行位置是持久
项目容器 `ubitect-repro-demo`。容器里才运行 Clang、UBITect、KLEE 和 Z3。
UBITect 只产生候选，KLEE 从函数入口探索，Z3 只判断已有断言是否可满足。

**页面正文（上屏用）：**

- **宿主 macOS / arm64**：终端、项目文件、`DEMO.sh`；不直接跑分析。
- **Docker Desktop**：提供 `linux/amd64` 运行环境；不是求解器。
- **项目容器**：`ubitect-repro-demo`，容器内 `x86_64`，Ubuntu 24.04 用户态，
  挂载项目目录到 `/work`；`start/status/stop` 只管理它。
- **容器内工具**：Clang 7 → 位码；UBITect → 候选；KLEE → 路径；Z3 → 判定。

| 角色 | 输入 | 做什么 | 输出/边界 |
|---|---|---|---|
| **UBITect** | C → LLVM 7 位码 → BBTag | 初始化状态/类型限定符传播，生成 warning | `warnings.json`；不调用 Z3，不证明可达 |
| **KLEE** | warning + 位码 | 从 `function` 入口探索；`use` 是目标块 | `confirm_result.json`、真实 `query.smt2`；不判断现实崩溃 |
| **Z3** | KLEE 导出的 SMT-LIB | 对 `assert` 合取做可满足性判定 | `sat` + 模型 / `unsat` / `unknown`；不发明事实 |

**页脚一行：** Python/uv 只做驱动和环境；Ubuntu 24.04 不是内核版本，容器内
运行内核是 Docker Desktop 的 linuxkit。

**推荐版式：** 上半屏 58% 放全宽 `runtime_topology.png`；下半屏压缩成三列
角色卡，不放大表。环境版本只留 “Clang 7 / KLEE 1.4.0.0 / Z3 4.8.8”。

**使用素材：** `ppt_assets/figures/runtime_topology.png`；
`ppt_assets/figures/two_stage_flow.png`（备注缩略图）；
`demo/container.json`；`docs/原理与数理逻辑讲解.md` §8；
`artifacts/A_original_default_dedup/compile_command.txt`。

**讲稿（约 65 秒）：**

> 先看运行位置。宿主机是 Apple Silicon macOS，只负责终端和 Docker Desktop；
> Docker 提供 linux/amd64 运行环境，但 Docker 本身不是分析工具。真正的执行
> 位置是持久容器 `ubitect-repro-demo`：容器内是 x86_64，Ubuntu 24.04 只是
> 用户态，运行内核是 Docker Desktop 的 linuxkit；项目目录挂载到 `/work`。
> 容器里才运行 Clang、UBITect、KLEE 和 Z3。UBITect 的第一阶段只做初始化
> 状态和类型限定符传播，输出 warning：入口函数、目标 use、黑白名单；它不
> 调用 Z3。KLEE 从 warning 的 `function` 入口开始，`use` 是它要到达的目标
> 块，不是起点；它沿分支收集条件，在真实 check 前导出 query。Z3 最后只判断
> 这些已有断言是否可满足。Python、uv 和 Docker 是驱动和环境，不是分析语义
> 的一部分。

**证据：** `demo/container.json`；`demo/verification-20261104T064956Z.json`；
`demo/runs/DEMO-20261104T065000Z/example/A/candidate-01/klee-original/command.sh`；
`artifacts/A_original_default_dedup/compile_command.txt`。

**必要限定：** 运行拓扑是实际环境关系，`two_stage_flow.png` 是方法示意；
阶段二仍是欠约束模型，KLEE 的路径引导是搜索策略，不是语义证明。

**衔接：** “第一阶段具体怎样从初始化状态得到候选？”

---

## 第 4 页：第一阶段，初始化状态与候选

**正式标题：** 第一阶段：`join(_UD, _ID) = _UD`，候选不是结论

**核心结论：** `_UD` 表示可能未初始化，`_ID` 表示已初始化；只要有一条路径
没有写，汇合后仍保留 `_UD`。这一阶段产生候选，不做 SMT 求解。

**页面正文：**

- 声明：`backlog → _UD`
- 第 22 行：`backlog = init → _ID`
- `a=0` 的路径不经过第 22 行，仍为 `_UD`
- 汇合：`join(_UD, _ID) = _UD`（保守保留可疑）
- A 默认报告第 25 行；B 是关闭报告去重的**教学构建**，才出现 25、26 两行

**状态表：**

| 位置 | 状态 | 含义 |
|---|---|---|
| 声明后 | `_UD` | 尚未看到赋值 |
| 第 22 行 true 边 | `_ID` | 已用 `init` 写入 |
| 第 22 行 false 边 | `_UD` | 跳过初始化 |
| 第 25 行汇合 | `_UD` | 任一前驱未初始化即保留 |

**投影上的边界句：** “类型限定符状态不是 SMT 断言；本阶段没有 Z3 调用。”

**推荐版式：** 左侧 `backlog_cfg.png`（55%），右侧状态表 + 一个 A/B 对照小框。
A/B 框都标注“候选对象”，不要写“漏洞”。

**使用素材：** `ppt_assets/figures/backlog_cfg.png`；
`demo/runs/DEMO-20261104T065000Z/example/A/candidate-01/warning.json`；
`demo/runs/DEMO-20261104T065000Z/example/variants/B/warnings.json`；
`ppt_assets/tables/case_results.md`。

**讲稿（约 55 秒）：**

> 第一阶段不需要求解器，它跟踪的是初始化状态。声明时是 `_UD`，执行第 22 行
> 后变成 `_ID`；但 `a=0` 的路径没执行初始化。两条路径汇合时，只要有一条没
> 写，就必须保留 `_UD`，否则会漏报。A 是默认报告，只有第 25 行；B 是另一个
> 教学构建，显式关掉报告去重，才显示 25、26 两行。这里得到的都是候选，不是
> 已确认缺陷，也没有 SMT 查询。

**证据：** 本轮 `DEMO-20261104T065000Z/example/A/stage1.log`；
`A/candidate-01/warning.json`；`variants/B/stage1.log`；`variants/B/warnings.json`；
`patches/0002-no-dedup-reporting.patch`。

**必要限定：** 候选数不等于漏洞数；B 不是 A 的原版默认输出；H1 两个对象同址
同根因，后面单独解释。

**衔接：** “拿到候选后，KLEE 到底从哪里开始，怎样走到 use？”

---

## 第 5 页：第二阶段，KLEE 从入口走到目标 use

**正式标题：** KLEE 从 `function` 入口开始，`use` 是目标块

**核心结论：** warning 的 `function` 决定入口；`use` 只是要到达的目标位置。
`blacklist` 避开块、`whitelist` 保留上下文；目标块是否到达由真实 KLEE 结果
决定，不由候选本身决定。

**页面正文（左栏真实 JSON 摘录）：**

```json
{"lineNo": 25,
 "function": "test",
 "use": "backlog.llbc-test-2",
 "blacklist": ["...test-1", "...test-3", "...test-4"],
 "whitelist": ["...test-0"],
 "warning": "%8 = load %struct.test_struct*, ..."}
```

**右栏：一条真实分支怎样变成目标条件（A）：**

```text
源码  if (a)                 // a 是符号输入
LLVM  %6 = icmp ne i32 %5, 0
      br i1 %6, label test-1, label test-2
KLEE  false 边 → 进入 test-2（第 25 行 load）
查询  input_0 = 0（等价简化） ∧ test-2 = 1
```

- KLEE 从 `function: "test"` 入口开始；`use: test-2` 是目标，不是起点。
- `blacklist` 中的 `test-1` 是初始化块，避开它才能保留“未初始化”路径；
- `whitelist` 的 `test-0` 是入口上下文；
- 确认结果来自 `confirm_result.json` 的 `find:"Yes"` 和目标行，不是候选 JSON。

**推荐版式：** 左侧 JSON（40%），右侧一条竖向“入口 → 分支 → use”图；底部
放 A 的真实 `path` 一行。不要在这一页展开完整 `query.smt2`，留给第 6 页。

**使用素材：** `demo/runs/DEMO-20261104T065000Z/example/A/candidate-01/warning.json`；
`.../klee-original/command.sh`；`.../klee-original/confirm_result.json`；
`ppt_assets/figures/backlog_cfg.png`（可裁切）。

**讲稿（约 60 秒）：**

> 第二阶段不是把候选直接当结论。每条 warning 给 KLEE 一个入口函数、一个目标
> use、一个要覆盖的 whitelist 和一个要避开的 blacklist。注意，KLEE 从
> `function` 入口开始，`use` 是目标块，不是起点。以 A 为例，KLEE 从 `test`
> 入口分叉；`a=0` 的 false 边进入 `test-2`，也就是第 25 行的 load，路径条件
> 被保存下来。候选 JSON 只说“这里可疑”；`find:"Yes"` 和 query 才是 KLEE
> 真正到达目标后的产物。

**证据：** 本轮 A 的 `warning.json`、`command.sh`、`confirm_result.json`；
`confirm_result.json` 的 `path`：
`false : br i1 %6, label %backlog.llbc-test-1, label %backlog.llbc-test-2`。

**必要限定：** 黑白名单是搜索引导，不保证语义上的 UNSAT/安全；D 组证明
“候选仍在，但路径不确认”是可能的。

**衔接：** “KLEE 保存下来的条件，怎样变成一条真实的 SMT 查询，并让 Z3 给出
模型？”

---

## 第 6 页：求解器核心（一）——A/B 的完整真实链

**正式标题：** 从源码分支到 Z3 模型：A 第 25 行 vs B 第 26 行

**核心结论：** A 只需 `a=0` 就能到达第 25 行读取；B 要再满足 `backlog` 残值
非零，才能进入第 26 行解引用。两处的 SAT 都表示“路径公式有模型”，不是
“指针已证明有效”。

**页面正文分两栏：**

**A｜第 25 行：跳过初始化，直接读取**

```text
源码：if (a) ...;  if (backlog) { ... }   // 25 行 load
IR  ：%6 = icmp ne i32 %5, 0
      br i1 %6, label test-1, label test-2
路径：false 边 → test-2
查询：input_0 = 0（等价简化） ∧ test-2 = 1
Z3  ：sat，模型 input_0 = 0
```

A 的真实断言（`DEMO-.../A/candidate-01/klee-smt-export/query.smt2`）：

```smt2
(assert
 (= backlog.llbc-test-0 1))
(assert
 (let (($x29 (= false (= (_ bv0 64) input_0))))
 (= $x29 false)))
(assert
 (= backlog.llbc-test-2 1))
(check-sat)
```

**B｜第 26 行：还要残值非零**

```text
源码：if (backlog) { backlog->irq = 0; }  // 26 行解引用
IR  ：%9 = icmp ne %struct.test_struct* %8, null
      br i1 %9, label test-3, label test-4
路径：true 边 → test-3
查询：alloca != 0（等价简化） ∧ test-3 = 1
Z3  ：sat，模型 alloca = 18446744073709551615
```

B 的真实断言（`artifacts/analysis/real-exports/B_candidate-02-line-26.smt2`）：

```smt2
(declare-fun alloca () (_ BitVec 64))
(assert
 (= (= false (= (_ bv0 64) alloca)) true))
(assert
 (= backlog.llbc-test-3 1))
```

**页面下方固定说明：**

- A 的查询**没有**“backlog 残值非零”断言；它只要求 `a=0` 和目标块 `test-2`。
- B 的查询多出 `alloca != 0` 和 `test-3 = 1`；模型里的
  `18446744073709551615` 只是位向量中的一个非零值，不是有效地址。
- 源码 `int a` 是 32 位；真实编码器的 `input_0` 是 64 位 `BitVec`；页面上的
  `input_0=0` 是**等价简化（教学表达）**，不是把原始断言改写后冒充导出。

**推荐版式：** 左右两列 A/B；每列“源码→IR→查询→Z3”四行纵向箭头；
每列只放 3 行真实 SMT，完整 query 放备注。A/B 顶部用同一颜色标“真实导出”，
“等价简化”用灰色斜体。

**使用素材：** 本轮 A `query.smt2`/`z3-replay.json`；
`artifacts/analysis/real-exports/B_candidate-02-line-26.smt2`/`.result.json`；
`artifacts/A_original_default_dedup/backlog.ll:23-38`；
`ppt_assets/code/backlog_line25.smt2`、`backlog_line26.smt2`。

**讲稿（约 70 秒）：**

> 这一页是整场的核心。A 的源码分支是 `if(a)`：a 等于零时跳过初始化，进入
> 第 25 行的 load。LLVM 里是 `%6 = icmp ne` 加一条 `br`；KLEE 走 false 边
> 到 `test-2`，导出的真实断言要求 `input_0=0`，并且 `test-2=1`。这里没有
> 要求 backlog 非零，所以 Z3 给 sat，模型就是 `input_0=0`。
>
> B 是下一行：`if(backlog)` 为真才解引用。IR 多一条指针比较，KLEE 要
> `test-3=1`；真实查询多一个 `alloca != 0`。Z3 同样 sat，模型给了一个全 1 的
> 非零值。这个值不是有效地址，也不是漏洞利用；它只说明路径条件允许一个非零
> 残值。A 和 B 的差别，就是“读取本身”与“解引用还要求非零”的差别。

**证据：** A 真实 query/model：
`demo/runs/DEMO-20261104T065000Z/example/A/candidate-01/klee-smt-export/`；
B 归档真实 query/model：`artifacts/analysis/real-exports/B_candidate-02-line-26.*`；
IR：`artifacts/A_original_default_dedup/backlog.ll:23-38`。

**必要限定：** B 的查询来自正式归档的真实导出，不是本轮 `compare example`
重新导出的；页面要标“归档真实导出”。A/B 的 `input_0` 都是 64 位编码，不能
说成 32 位 `a` 的逐位等价。

**衔接：** “这条 query 的语法和 sat/unsat 到底怎么读？”

---

## 第 7 页：求解器核心（二）——读 query，读状态

**正式标题：** 一条 query 的四件事：声明、断言、检查、模型

**核心结论：** `declare-fun` 只声明符号，`assert` 才是约束，`check-sat` 触发
判定；模型由重放脚本从 Z3 API 取出。`sat/unsat/unknown/无 query/超时` 必须
分开解释。

**页面正文（左上：A 的真实 query 节选；右侧注释为教学标注，不属于文件）：**

```smt2
(set-info :status unknown)                 ; 元数据，不是结果
(declare-fun input_0 () (_ BitVec 64))     ; 声明一个 64 位符号
(assert
 (= backlog.llbc-test-2 1))                ; 目标块必须到达
(check-sat)                                ; 让求解器判定
```

| 语法 | 含义 | 本页要点 |
|---|---|---|
| `declare-fun` | 声明常量/函数符号及其排序 | 不是赋值，不产生约束 |
| `assert` | 把公式加入断言集合 | 多条断言取合取 |
| `check-sat` | 请求判定当前断言集合 | 文件里没有 `get-model` |
| model | 一组让断言为真的赋值 | 由 `replay_z3.py` 的 Python API 取出 |

**右上：状态表（投影必须完整）：**

| 观察 | 含义 | 不能说什么 |
|---|---|---|
| `sat` | 存在模型，路径条件与断言一致 | 不能说“现实一定崩溃” |
| `unsat` | 断言合取无模型；仅当确有目标 query | 不能把“无 query”写成 UNSAT |
| 无 query | KLEE 未确认目标 / 未导出；没有求解结果 | 不能说“已排除所有路径” |
| `unknown` | 求解器无法判定（理论/资源/超时等） | 不能当 sat 或 unsat |
| timeout | 外部/求解器时限终止，未得到结果 | 不能补造成 UNSAT |

**底部两行：**

- `set-info :status unknown` 只是 SMT-LIB 元数据；本次真实结果是重放日志里的
  `sat`。
- 源码 `int a` 32 位；作者编码器的 `input_0` 是 64 位 `BitVec`。讲“等价”时
  必须说“在该编码模型内等价”，不是 C 语义的逐位证明。

**推荐版式：** 左上 4 行真实 query；右上状态表；底部一条“无 query ≠ UNSAT”
红色提示。变量表只保留 4 行，完整符号表放备注。不要用 `sat_cards.png` 代替
状态表；卡片可在第 8/10 页作视觉辅助。

**使用素材：** 本轮 A `query.smt2`；`scripts/replay_z3.py`；
`docs/原理与数理逻辑讲解.md` §4.1/§4.3；
`artifacts/analysis/independent/a_zero_and_nonzero_32bit.smt2`（D 的独立 UNSAT）。

**讲稿（约 60 秒）：**

> 读 query 只看四件事。第一，`declare-fun` 只是声明一个符号，比如 64 位的
> `input_0`，它不是赋值。第二，`assert` 才是约束；多条断言是合取。第三，
> `check-sat` 触发判定；导出的文件里没有 `get-model`，模型是重放脚本通过
> Z3 的 Python API 取出来的。第四，结果要分清：sat 是有模型；unsat 是断言
> 合取无模型；没有 query 不等于 unsat，只表示 KLEE 没有确认目标；unknown 和
> 超时都是“未判定”。另外，`set-info :status unknown` 只是元数据，不是结果。

**证据：** A `query.smt2` 与 `z3-replay.json`；`scripts/replay_z3.py`；
D 独立公式及 `a_zero_and_nonzero_32bit.result.json`；H2
`confirm_result.absent.txt`。

**必要限定：** 本轮没有观察到 `unknown` 或 timeout；它们在表里是语义定义，
不是本轮实验数据。D 的 UNSAT 是独立教学重建，不是 KLEE 导出。

**衔接：** “把 A/B/C/D 放在一起，候选和确认各自是什么？”

---

## 第 8 页：A–D 示例结果

**正式标题：** A 默认一行，B 教学两行；C 消失，D 不确认

**核心结论：** 四组分别验证默认报告、关闭去重、`NULL` 初始化和短路保护。
候选对象数、独立 use 点数、确认数必须分开；D 没有目标 query。

**页面正文：**

| 组 | 源码控制 | 候选对象 | 独立 use 点 | 确认对象 | 目标 query |
|---|---|---:|---:|---:|---|
| A | 原始默认（去重） | 1 | 1（25） | 1 | 有，SAT |
| B | 教学构建：`-DUBITECT_NO_DEDUP` | 2 | 2（25、26） | 2 | 有，SAT |
| C | `backlog = NULL` | 0 | 0 | 0 | 无 |
| D | `if (a && backlog)` | 1 | 1（25） | 0 | 无 |

- A/B 的差别是**报告粒度**，不是两个不同缺陷；
- C 在声明处写 `NULL`，初始化状态消失，候选为 0；
- D 仍报第 25 行候选，但 KLEE 在到达 use 前终止；没有确认，也没有导出 query；
- “确认”只指 KLEE 的 `find:"Yes"` + 目标行，不是现实崩溃。

**计数口径（页脚）：** 对象数/独立 use 点/确认对象数来自
`demo/runs/DEMO-20261104T065000Z/example/compare.json`；它与正式
`metrics/results.csv` 的 A–D 行一致。对象数不是漏洞数；B 的两行是两个 use 点，
H1 的两个对象才是同一 use 点（见第 10 页）。

**推荐版式：** 左侧 `case_counts.png`（55%），右侧上表；底部一条
“候选 ≠ 确认 ≠ 漏洞”。D 的“无 query”用红色标签。

**使用素材：** `ppt_assets/figures/case_counts.png`；
`ppt_assets/tables/case_results.md`；`artifacts/SUMMARY.md`；
本轮 `example/compare.json`。

**讲稿（约 55 秒）：**

> A 是原版默认，只报第 25 行。B 是教学构建，关掉报告去重，才出现 25、26
> 两行；它不是 A 的原版输出。C 在声明处写 NULL，初始化状态消失，所以候选为
> 零。D 改成 `a && backlog` 后，静态分析仍报第 25 行候选，但 KLEE 在到达 use
> 前终止；没有确认，也没有目标 query。这里千万不要把候选数或确认数直接叫
> 漏洞数；D 尤其不能补一个 UNSAT。

**证据：** `demo/runs/DEMO-20261104T065000Z/example/compare.json`；
`artifacts/A_original_default_dedup/`、`B_no_dedup_reporting/`、
`C_null_initialization_fix/`、`D_short_circuit_control/`；
`metrics/results.csv`。

**必要限定：** 四组是选定小案例，不能计算通用准确率/F1；B 不是原版默认；
D 未确认不等于“所有路径都安全”。

**衔接：** “示例之外，真实历史函数上能否走同一条链？”

---

## 第 9 页：历史失败模式、官方补丁、入口与桥接

**正式标题：** 官方 `else if` 改变了失败路径的目标可达性

**核心结论：** H1 在 `acpi_get_object_info` 失败后仍执行 `if(info->valid...)`；
H2 的 `else if` 把读取限制在成功分支。失败桩不写输出参数 `*out`；入口限制
和 SSA 桥接只服务于 KLEE 装载，必须单独说明。

**页面正文（左：补丁；右：边界）：**

```c
/* H1: 8ba559fd, line 825 */
status = acpi_get_object_info(..., &info);
if (ACPI_FAILURE(status)) {
    version = XGENE_AHCI_V1;
}
if (info->valid & ACPI_VALID_CID)   /* 失败后仍读取 */
    version = XGENE_AHCI_V2;

/* H2: 8134233e, line 824 */
} else if (info->valid & ACPI_VALID_CID) {  /* 失败时跳过 */
    version = XGENE_AHCI_V2;
}
```

- 失败语义：`acpi_get_object_info` 失败时**没有给 `info` 赋值 / 没有写输出
  参数 `*out`**；不是说“没有写 `*info`”。
- harness：`-DHISTORY_ACPI_FAILURE_ONLY`，只建模失败分支；
  `history_entry_failure(int acpi_handle_value)` 的
  `if (acpi_handle_value != 0) return 0;` 固定入口选择。
- `input_0 = 0` 是入口选择器（选择失败路径），不是攻击者输入。
- SSA 桥接：H1 `%137 → %138`、H2 `%140 → %141`，只是匹配副本的调试后缀
  差异；`use`/blacklist/whitelist/断言/求解器设置不变。入口限制是语义上更
  重要的一步：它固定了“从哪个函数、哪条失败路径开始”。

**推荐版式：** 上半屏 `ahci_code_compare.png`（补丁前后）；下半屏三张窄卡：
“失败桩”“入口选择器”“SSA 桥接”。不要把完整 1000 行函数放上屏。

**使用素材：** `ppt_assets/figures/ahci_code_compare.png`；
`ppt_assets/code/ahci_h1_snippet.c`、`ahci_h2_snippet.c`；
`history/ahci_xgene/provenance/official-fix.patch`；
`HARNESS_MAPPING.md`、`KLEE_BRIDGE.md`。

**讲稿（约 60 秒）：**

> 这是论文 Table 2 里的真实历史案例。修复前，`acpi_get_object_info` 失败后
> 仍然执行 `if(info->valid)`；失败时没有给 info 赋值，也没有写输出参数
> `*out`，所以这里读的是未初始化指针。官方补丁把第二个 if 改成 else if，
> 失败路径就跳过读取。我们的 harness 只建模失败分支，入口参数 `input_0=0`
> 是失败选择器，不是攻击者输入。为了让 KLEE 装载，SSA 副本里的 `%137` 变成
> `%138`，但 use、黑白名单、断言和求解器设置都没变；入口限制本身有语义影响，
> 后面结论只覆盖失败路径。

**证据：** `history/ahci_xgene/source/ahci_xgene.8ba559fd09bc.c:817-828`；
`...8134233e8d34.c:817-828`；
`history/ahci_xgene/provenance/official-fix.patch`；
`history/ahci_xgene/HARNESS_MAPPING.md`；`KLEE_BRIDGE.md`。

**必要限定：** 真实函数体 ≠ 完整内核；补丁存在 ≠ 所有输入安全；H1/H2 只覆盖
失败模式；桥接不改变原始 warning，但入口限制会缩小结论范围。

**衔接：** “在这个失败模式模型里，H1/H2 实际确认了什么？”

---

## 第 10 页：H1/H2 实际结果与真实查询

**正式标题：** H1 两个对象确认、一个根因；H2 无目标查询

**核心结论：** 本轮 H1 的 2 个目标对象都确认，2 个 query 都 SAT；它们同址
825，只对应 1 个 use 点/根因。H2 的 2 个对象都未确认，没有目标 query；不能
写成 UNSAT。

**页面正文（上：结果表）：**

| 版本 | 目标行 | 目标对象 | 确认对象 | 独立 use 点 | 目标 query | Z3 |
|---|---:|---:|---:|---:|---|---|
| H1 | 825 | 2 | 2 | 1 | 2 个 | sat, sat |
| H2 | 824 | 2 | 0 | 0 | 0 个 | — |

**下左：H1 真实 query 的关键断言（candidate-01，节选）：**

```smt2
(assert
 (= ahci_xgene_h1.llbc-history_entry_failure-2 1))
(assert
 (let (($x30 (bvule (_ bv18446744073709547521 64)
                    |%128 G22_30866688L1|)))
 (= $x30 false)))
(assert
 (= ahci_xgene_h1.llbc-xgene_ahci_probe-21 1))
(check-sat)
```

> 这是真实文件的逐字节选，只删掉部分块断言，未改断言内容；注释在正文中另写，
> 不混入文件。

真实文件：
`demo/runs/HIST-20261104T065006Z/history/h1/candidates/candidate-01/klee-smt-export/query.smt2`
（11 个 `declare-fun`、11 个 `assert`）。模型关键字段：
`input_0 = 0`、`%128 = 18446744073709551615`、`probe-21 = 1`，结果 `sat`。

**下右：H2 的“无查询”证据：**

```text
demo/runs/HIST-20261104T065006Z/history/h2/
  confirm_result.absent.txt:
  No target candidate was confirmed by KLEE in this case.
  → 没有 query.smt2
  → bridge.json 的 klee_instruction = null
```

**页面固定三条边界：**

1. H1 的 `input_0=0` 是失败入口选择器；查询中没有 `info` 变量，也没有
   “info 未初始化”的 SMT 断言。
2. H1 的 `%128` 是 ACPI 分支上的 64 位符号，不是 `info` 指针，也不是地址。
3. H2 的 `else if` 让失败路径跳过 824 行；候选仍在，但没有目标确认/查询。

**推荐版式：** 上方结果表；左下真实 query + 模型；右下 H2 absent 文件；
底部一条红色“H2 无 query ≠ UNSAT”。不要放 `sat_cards.png` 的四卡全图，除非
有足够投影面积；本页信息密度已高。

**使用素材：** 本轮 `verify.json`、`compare.json`；
H1 `query.smt2`、`z3-replay.json`；H2 `confirm_result.absent.txt`、
`bridge.json`；正式归档 `HIST-20261027T133810Z/summary.json`。

**讲稿（约 65 秒）：**

> H1 在失败模式下有两个同址 warning 对象，行 825，都被 KLEE 确认，两个
> query 都是 sat；但它们落在同一个 use 块，只算一个 use 点、一个根因，不能
> 说两个漏洞。看真实 query：入口选择器 `input_0=0`、失败入口块标记、`%128`
> 非零、以及到达 probe-21 的块标记；里面没有 info 变量，也没有“info 未初始
> 化”的断言。`%128` 不是 info，也不是地址。
>
> H2 是两个对象、零确认、零 query。`else if` 让失败路径跳过 824 行，KLEE
> 没有目标指令，所以没有 query。这里只能写“无目标查询”，不能写 UNSAT。

**证据：** `demo/runs/HIST-20261104T065006Z/history/verify.json`、`compare.json`；
H1/H2 候选目录；`history/ahci_xgene/runs/HIST-20261027T133810Z/summary.json`；
`HARNESS_MAPPING.md`、`KLEE_BRIDGE.md`。

**必要限定：** 只覆盖失败模式；H1 两个对象不是两个漏洞；H2 候选仍存在；
不是完整内核/硬件；符号后缀按运行生成，不能逐字符比较不同运行。

**衔接：** “这些确认的耗时和资源是多少？哪些是存档测量？”

---

## 第 11 页：性能与资源：n=3、范围、边界

**正式标题：** 局部测量：14 个阶段 × 3 次；RSS、cgroup、VM 配置分开

**核心结论：** 测量来自 `MET-20261027T133810Z`，不是本轮实时测量。14 个阶段
各 3 次，全部 rc=0、无超时；历史重复只用 candidate-01，不能叫“历史全流程
总时间”。

**页面正文：**

- 测量编号：`MET-20261027T133810Z`；14 个阶段 × 每阶段 3 次；全部返回 0，
  `timeouts=0`。
- 阶段：编译、BBTag、候选分析、KLEE、Z3 重放；A 与 H1/H2。
- 代表值（中位数）：
  - A 分析：0.067 s / 14,448 KiB；
  - A KLEE：0.170 s / 48,744 KiB；
  - A 重放：0.278 s / 59,768 KiB（含 Python 启动/导入）；
  - H1 KLEE：0.231 s / 49,936 KiB；H1 重放：0.280 s / 60,440 KiB；
  - H2 KLEE：0.226 s / 49,792 KiB。
- **RSS**：GNU `time -v` 的单进程峰值，不是容器 RSS。
- **cgroup**：容器生命周期 current/peak（起始 current 33.8 MiB、peak 50.6 MiB；
  结束 current 66.9 MiB、peak 105.2 MiB），不是每阶段峰值。
- **VM**：Docker Desktop 配置 6 CPU / 8192 MiB / 102400 MiB，是配置上限，
  不是使用量。
- **冷构建**：`build_first_time = null`，本轮未重测；不能拿日志时间差冒充。

**页脚统计口径：** 墙钟单位秒（`time.monotonic()`）；RSS 单位 KiB；1 MiB =
1024 KiB；图中误差线是 min–max，不是标准差。B/C/D 只有逐候选单次记录，没有
像 14 阶段那样做 3 次；H1/H2 的 3 次重复只用 candidate-01。

**推荐版式：** 上排 `timing_backlog.png` + `timing_history.png`；下排
`memory_process.png` + 一张“测量边界”三行卡。不要同时放大表；数字只保留
代表值，完整表放备注。

**使用素材：** `ppt_assets/figures/timing_backlog.png`、`timing_history.png`、
`memory_process.png`；`metrics/summary.json`、`metrics/candidate_timings.csv`、
`metrics/vm_and_build_sample.json`、`ppt_assets/tables/stage_metrics.md`。

**讲稿（约 55 秒）：**

> 这些数字不是内核基准，也不是本轮实时测量。测量编号是
> MET-20261027T133810Z，14 个阶段各做 3 次，全部返回 0，没有超时。A 的分析
> 中位约 0.067 秒、14 MiB；KLEE 约 0.17 秒、48 MiB；重放约 0.28 秒，包含
> Python 启动和导入。历史重复 KLEE 只用 candidate-01，所以不能叫完整历史
> 工作流时间。RSS 是单进程峰值；cgroup 是容器生命周期；8 GiB 只是 Docker VM
> 配置。冷构建没有重测，记录是 null。

**证据：** `metrics/summary.json`、`metrics/candidate_timings.csv`、
`metrics/resources.csv`、`metrics/vm_and_build_sample.json`；
`ppt_assets/tables/stage_metrics.md`。

**必要限定：** 不外推通用性能/加速比；不把 8192 MiB 当实际峰值；不把重放
墙钟当成纯 Z3 求解时间；不把 `MET-...` 当本轮运行。

**衔接：** “最后把可声称与不可声称的结论收束。”

---

## 第 12 页：结论与边界

**正式标题：** 结论：两阶段链可复现，SAT 只支持模型内结论

**核心结论：** UBITect 产生候选；KLEE 从入口走路径并导出条件；Z3 判可满足性。
A/B/C/D 和 H1/H2 都能落到实际文件；但它们是选定案例和失败模式模型，不是
完整内核、通用准确率或现实漏洞证明。

**页面正文（三列）：**

**已完成**

- A–D + H1/H2 的真实运行与查询；
- KLEE 路径、Z3 重放、模型、桥接和补丁证据；
- 本轮 `DEMO-20261104T065000Z`、`HIST-20261104T065006Z` 验证记录。

**主要发现**

- `if(backlog)` 本身是 load；
- 候选 ≠ 已确认；D 有候选无查询；
- A 第 25 行只需 `a=0`；B 第 26 行还要求残值非零；
- H1 2 对象 / 1 use 根因；H2 0 确认 / 0 query。

**不能声称**

- 不是完整内核/硬件运行；
- 不是漏洞利用；
- H2 没有 UNSAT；
- 没有通用准确率/F1/检测率；
- 32 位源码与 64 位编码不是逐位等价。

**推荐版式：** 三列等宽卡片；底部固定一行“真实文件 → 真实查询 → 真实状态”，
不放新图。若时间紧，优先删第 11 页的部分数字，不删“H2 无 query”和“SAT 不是
崩溃”。

**使用素材：** `artifacts/SUMMARY.md`、`FINAL_ACCEPTANCE.md`、
`HISTORICAL_CASE_REPORT.md`、`metrics/results.csv`；可选缩略
`case_counts.png`。

**讲稿（约 45 秒）：**

> 最后总结：UBITect 产生候选，KLEE 从函数入口走路径并导出条件，Z3 判断这些
> 条件是否可满足。A 第 25 行只需 `a=0`；B 第 26 行还要求残值非零；C 消除
> 候选；D 有候选但没有 query。历史 H1 的两个对象确认，但只是同一个 use 点；
> H2 的 else if 阻断目标读取，零确认、零 query。我们可以复现流程和证据，但
> 不能把 SAT 说成现实崩溃，也不能给 H2 补一个 UNSAT。

**证据：** `FINAL_ACCEPTANCE.md`、`artifacts/SUMMARY.md`、
`history/ahci_xgene/runs/HIST-20261027T133810Z/summary.json`、
`metrics/results.csv`、本文件配套的 `presentation/演示与求解器关系核对.md`。

**必要限定：** 函数级带桩/失败输入范围/欠约束；没有完整内核；没有通用指标。

**衔接：** 结束，进入提问；可指向附录与证据目录。

---

## 附录与演讲者备注（不占 12 页）

- 完整 `query.smt2`、11 个 H1 断言、完整 `klee.log`、SSA 名称表：放备注，
  正文只留关键断言。
- `presentation/演示与求解器关系核对.md`：12 项关系核对、真实文件映射、
  本轮验证记录。
- `docs/原理与数理逻辑讲解.pdf`：公式、状态语义、历史案例细节。
- `HISTORICAL_CASE_REPORT.md`、`REPRODUCTION_REPORT.md`：正式归档数据。
- `ppt_assets/INDEX.md`：每张图的生成命令、数据源、边界、建议页。

## 页间逻辑检查

```text
任务/主题（1）
→ 问题与案例角色（2）
→ 三工具分工（3）
→ 第一阶段候选（4）
→ 第二阶段 KLEE 路径（5）
→ A/B 完整 SMT 链（6）
→ 读 query/状态语义（7）
→ A–D 结果（8）
→ 历史补丁/入口/桥接（9）
→ H1/H2 真实结果（10）
→ 测量与资源边界（11）
→ 结论（12）
```

每页只新增一个问题；第 6/7 页是求解器核心，不把“公式解释”拆散到结果页；
第 9/10 页故意拆成“补丁改变什么”和“本次确认什么”，避免把补丁本身误读成
漏洞数量。
