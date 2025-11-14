# The introduction and use of the symbolic execution engine KLEE

## 小组成员

| 学号 | 姓名 |
| ---- | ---- |
| 23009290053 | 张辅志 |
| 23009200097 | 陈新宇 |
| 23009290038 | 张翔 |
| 23009290037 | 王敬皓 |

## 工作简介

- KLEE 原理介绍：概述了符号执行的基本思想、KLEE 的系统架构与工作流程，说明其在自动生成高覆盖率测试用例和发现潜在程序错误方面的作用。
- 实例演示与实践：通过编译 LLVM bitcode 并运行 KLEE，对示例程序进行符号执行，展示如何生成 `.ktest` 测试文件及查看测试结果。
- 迷宫求解案例：设计了一个 ASCII 迷宫程序，将用户输入符号化，利用 KLEE 自动探索所有可能路径，验证其路径求解能力，并通过“假墙”实验分析逻辑控制对路径可达性的影响。
- 应用与思考：讨论了 KLEE 在程序测试、错误检测和验证中的应用潜力，同时分析了路径爆炸、约束求解开销等现实局限性。

## 相关链接

- [KLEE 官方入门指南](https://klee-se.org/getting-started/) —— 官方使用与安装说明  
- [GNU Coreutils 项目](https://www.gnu.org/software/coreutils/) —— KLEE 测试目标示例项目  
- [KLEE 符号执行教程](https://klee-se.org/tutorials/using-symbolic/?utm_source=chatgpt.com) —— 官方符号执行教学示例  
- [Adalogics 博客](https://adalogics.com/blog/symbolic-execution-with-klee?utm_source=chatgpt.com) —— KLEE 实战与应用分析  
- [The Symbolic Maze](https://feliam.wordpress.com/2010/10/07/the-symbolic-maze/) —— 经典 KLEE 迷宫实验介绍  
- [SymEx Tarot 讲义](https://srg.doc.ic.ac.uk/files/slides/symex-tarot-18.pdf?utm_source=chatgpt.com) —— 符号执行教学幻灯片  
- [KLEE 原始论文](https://hci.stanford.edu/cstr/reports/2008-03.pdf?utm_source=chatgpt.com) —— 《KLEE: Unassisted and Automatic Generation of High-Coverage Tests》

## 思考

通过实验，我们对符号执行技术的机制与价值有了更直观的理解。

+ KLEE 展示了程序路径可达性取决于逻辑条件与约束求解，而不仅是输入或结构。它让我们以更系统的方式分析程序行为，从逻辑层面揭示潜在漏洞与异常路径。

+ 在迷宫实验中，KLEE 的路径探索与“假墙”现象说明了符号执行在复杂逻辑分析中的能力与局限——能识别隐藏通路，但也受限于路径爆炸与求解复杂度。
+ 使用 KLEE 进行符号执行测试，有助于提高代码覆盖率与错误检测效率，并强化我们对程序验证方法的理解。
