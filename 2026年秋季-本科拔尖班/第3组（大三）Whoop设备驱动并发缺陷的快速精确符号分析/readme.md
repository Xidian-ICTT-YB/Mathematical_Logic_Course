# Whoop：设备驱动并发缺陷的快速精确符号分析复现

课程：计算机科学使用的数理逻辑  
学期：2026 秋  
组别：第三组

## 小组成员

| 姓名 | 学号 | 主要分工 |
| --- | --- | --- |
| 涂家宏 | 24009290071 | PPT主要构建，原理学习讲解，项目搭建，综合负责，解释善后 |
| 郑冬阳 | 24039100680 | 复现以及可视化网页制作 |
| 饶亿泽 | 24009290068 | 原理学习，演讲汇报 |
| 金煜涵 | 24009290004 | 资料收集，ppt原理部分初稿 |

## 论文与工具来源

- 官方 GitHub 仓库：[Whoop](https://github.com/smackers/whoop)
- 论文：Pantazis Deligiannis, Alastair F. Donaldson, Zvonimir Rakamaric.  
  *Fast and Precise Symbolic Analysis of Concurrency Bugs in Device Drivers*. ASE 2015.
- 论文地址：[Paper PDF](https://fastpl.doc.ic.ac.uk/tools/Whoop/ASE2015/downloads/paper.pdf)
- 原始驱动样例：
  - [generic_nvram](https://github.com/smackers/whoop/tree/master/driversuite/char/generic_nvram)
  - [pc8736x_gpio](https://github.com/smackers/whoop/tree/master/driversuite/char/pc8736x_gpio)

Whoop、SMACK、Boogie、Corral、Z3 及原始驱动代码均来自各自作者。本项目保留相关来源及版权信息，记录课程复现过程中使用的配置、修改、实验结果和分析证据。

## 项目简介

本项目围绕 ASE 2015 论文提出的 Whoop 工具，复现其针对 Linux 设备驱动并发缺陷的分析流程。

Whoop 采用符号成对锁集分析，检查不同并发入口对之间的共享内存访问及共同锁保护关系，识别潜在数据竞争。随后结合 Corral 进行精确符号执行，在给定模型和检查边界内寻找可能触发错误的执行路径，并通过 SMT 求解判断路径条件是否可满足。

本项目选取作者 driversuite 中的两个驱动：

- `generic_nvram`：通用非易失存储驱动。
- `pc8736x_gpio`：PC8736x GPIO 驱动。

在原始驱动分析的基础上，进一步构造不同锁保护范围的修改版本，通过对照实验观察潜在告警和具体错误执行的变化。

## 复现内容

1. **Whoop 潜在竞争分析**

   使用两个原始驱动作为输入，运行 Whoop 的符号锁集分析，检查并发入口对之间是否存在缺少共同锁保护的冲突访问。

2. **Corral 精确检查**

   针对选定的潜在竞争入口对，使用 Corral 搜索具体执行路径，分析不同线程之间的交错过程，并检查错误断言是否能够被触发。

3. **锁保护对照实验**

   对两个驱动进行不同程度的加锁修改，比较修改前后的 Whoop 和 Corral 分析结果，研究共同锁保护与实际错误路径之间的关系。

## 运行环境

- 宿主环境：Windows + WSL2
- WSL2 Ubuntu：24.04.2
- PRoot Ubuntu 用户态：16.04.6 LTS
- LLVM / Clang：3.5.2
- SMACK：1.5.0
- Whoop：0.7
- Boogie：作者提供的 BoogieBinaries
- Corral：作者指定提交版本
- Z3：4.3.2

主要分析参数：

- Whoop：`--find-bugs --yield-race-check --k=2 --recursion-bound=1`
- Corral：`/k:2 /recursionBound:1 /cooperative`

由于旧版 Whoop 存在锁上下文处理问题，本次复现对 `PairCheckingRegion.cs` 使用了两行锁上下文修正补丁，使已有锁声明能够正确参与判断。

此外，使用共同锁校准样例进行测试，5/5 组检查通过；无锁和单侧加锁负对照仍能报告问题。因此，本次工作属于基于保留补丁和校准结果的复现，而非完全未经修改的原版工具运行。

## 实际结果

### 1. Whoop 潜在竞争分析

| 驱动 | 论文潜在竞争入口对 / 总数 | 本地潜在竞争入口对 / 总数 |
| --- | ---: | ---: |
| generic_nvram | 7 / 14 | 7 / 14 |
| pc8736x_gpio | 13 / 27 | 13 / 27 |

两个驱动的潜在竞争入口对数量均与论文对应统计一致。

其中，GPIO 日志中的 `20 errors` 表示错误报告条数，不代表 20 个不同的内存区域。

### 2. Corral 精确检查

**generic_nvram**

- A0：原始版本。
- 检查入口对：`nvram_llseek × nvram_llseek`。
- 发现可行错误执行，涉及第 53 行对 `file->f_pos` 的写入与第 55 行的返回读取。
- A1：在 `llseek` 中增加与原有代码相同的 `nvram_mutex`，并在解锁前保存返回值。
- 修改后，Corral 在本次检查配置下未再发现该目标入口对的反例。

**pc8736x_gpio**

- B0：原始版本。
- 检查入口对：`pc8736x_gpio_change × pc8736x_gpio_current`。
- 找到具体错误执行，涉及第 204 行对 `shadow[port]` 的读取，以及 `change` 调用 `set` 后在第 195 行进行的写入。
- B1：仅对写入操作增加锁保护，仍然能够找到反例。
- B2：让读取与写入双方使用同一把 `gpio_shadow_lock`。
- 修改后，Corral 在当前检查范围内未找到反例，27 个入口对均未得到反例。

B2 的实验说明，仅给写入方加锁不足以建立读写双方的共同保护。需要注意，分别保护读写操作不等于整个 `change` 操作已经具备原子性。

## 工具搭建后的主要思考

1. **Whoop 与 Corral 解决的是不同层次的问题。** Whoop 通过符号锁集分析识别潜在竞争，Corral 则进一步寻找能够触发错误的具体执行路径。潜在告警不等于已经确认的错误执行。

2. **共同锁保护是判断并发访问的重要依据。** 两个线程访问同一共享位置时，如果双方没有共同的保护锁，就不能直接认为访问是安全的。仅有一侧加锁也不足以阻止另一侧并发访问。

3. **符号执行结果受到模型和检查边界限制。** Corral 的无错误结果只能说明当前模型及参数范围内没有找到反例，不能直接证明整个驱动在所有输入和调度下都安全。

4. **复现工具链的难点不仅在于运行程序。** LLVM、SMACK、Boogie、Corral 和 Z3 之间存在版本及依赖关系，旧版工具还需要处理兼容性和源码问题。保留版本信息、补丁和原始日志是保证实验可核验的重要条件。

5. **实验应当区分潜在告警、可行反例与安全结论。** B2 仍然存在 Whoop 潜在竞争告警，但 Corral 在当前边界内没有找到反例。这说明两种分析的抽象程度和覆盖范围不同，不能简单地将潜在告警全部视为真实缺陷，也不能将未找到反例直接等同于证明安全。

## 复现范围与限制

- 本次完成了两个原始驱动的 Whoop 潜在竞争分析。
- 完成了 NVRAM 和 GPIO 的 Corral 具体错误执行检查。
- 完成了 A1、B1、B2 锁保护对照实验。
- 保留了运行日志、错误执行轨迹、源码位置、补丁和相关校验材料。
- Corral 检查采用 `k=2`、递归界 `1` 和 cooperative 调度，结论仅适用于本次模型与检查范围。
- 本次未完成论文全部驱动案例的复现，也未开展论文所报告的运行时间加速倍数对比。

## 项目文件

- `Whoop.ppt`：课程汇报 PPT。
- `index.html`:可视化网站。
- 复现实现视频。

本项目旨在通过实际运行和对照实验，理解 Whoop 的符号锁集分析原理，以及 Corral 与 SMT 求解在并发缺陷验证中的作用。
