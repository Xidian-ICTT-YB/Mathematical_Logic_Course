# The introduction and use of the symbolic execution engine KLEE

## 小组成员

| 学号 | 姓名 |
| ---- | ---- |
| 25031212025 | 王陈偲 |
| 25031212053 | 方斌 |

## 工作简介
- KLEE 原理介绍：对符号执行的核心概念进行了阐述，并介绍了 KLEE 的系统架构及运行机制，说明了其如何通过系统化路径分析，实现高覆盖率的自动化测试生成与潜在缺陷发现。
- 实例演示：通过将示例程序编译成 LLVM bitcode 并使用 KLEE 执行符号分析，演示了生成 .ktest 测试输入文件的过程以及查看对应执行结果的方法。
- 寻找路径案例：程序定义了 Fire 与 Ice 两个角色的移动逻辑，并将动作序列声明为符号输入。KLEE 在执行过程中会探索所有可能的路径组合，并根据断言判断哪些状态合法。

## 相关链接
- [KLEE 官方入门指南](https://klee-se.org/getting-started/) 
- [KLEE 部署、使用与原理分析](https://blog.csdn.net/IronmanJay/article/details/143357236) 
- [探索 KLEE 符号执行引擎：安装与入门实战指南](https://blog.gitcode.com/31f97d4619626f39efa86581cd51e51c.html) 
- [KLEE 原论文](https://www.usenix.org/legacy/events/osdi08/tech/full_papers/cadar/cadar.pdf) 
- [KLEE 实战示例](https://feliam.wordpress.com/2010/10/07/the-symbolic-maze/) 


## 思考
    通过本次实验对 KLEE 的使用，我对符号执行的原理和价值有了更加直观的理解。与依赖人工构造测试用例的传统方法相比，KLEE 能将输入建模为符号变量，系统地探索程序的所有可行路径，并自动生成触达每条路径的测试用例。在协作迷宫示例中，KLEE 不仅找到了能够通关的有效动作序列，也通过断言主动剪除撞墙、未开门进门等非法路径，使“程序是否能到达目标状态”这一问题转化为可直接由工具回答的可达性分析。
    同时，实验也暴露出符号执行的局限性。随着程序规模扩大、分支与循环增多，路径数量会急剧膨胀，若不对输入空间施加约束或合理设计模型，容易出现状态爆炸和资源耗尽。因而使用 KLEE 并非简单地“运行一下”，而是需要在建模阶段刻意控制搜索空间、明确断言设计，并合理限制符号范围。