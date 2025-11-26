# Z3 Prover + LLM Agent

## 小组成员

| 学号        | 姓名   |
|-------------|--------|
| 25031212046 | 江政杰 |

## 工作简介
1. **介绍了 Z3 Prover 背后的数学原理**

   包括命题逻辑、一阶逻辑、理论约束以及 DPLL(T) 框架，帮助从原理层面理解 SMT 求解器的运行机制。

2. **完成 Z3 的编译与安装演示**

   通过源码构建流程展示了 Z3 的工程化结构，并掌握从配置、编译到环境配置的完整安装步骤。

3. **基于 Python Binding 的数独问题建模与求解**

   将数独问题形式化为约束满足模型，使用 Z3 变量、域约束、Distinct 约束等构建完整 SMT 模型，并成功求解实例。

4. **探索大模型与 Z3 的工具链集成**

   通过“工具调用（Tool Calling）”将 Z3 的求解能力暴露给大语言模型，实现大模型自动生成约束，调用 Z3， 获得严谨推理结果的流程，为构建具备逻辑推理能力的 LLM Agent 进行了实践验证。

## 相关链接

- [Z3 Guide](https://microsoft.github.io/z3guide/)
- [Z3 Source Code](https://github.com/Z3Prover/z3)
- [LangChain (LLM Agent Framework) Official Website](https://www.langchain.com/)
- [LangChain Source Code](https://github.com/langchain-ai/langchain)
- [LangGraph Source Code](https://github.com/langchain-ai/langgraph)
- [Sudoku Wikipedia](https://en.wikipedia.org/wiki/Sudoku)
- [Einstein’s Riddle Wikipedia](https://en.wikipedia.org/wiki/Zebra_Puzzle)


## 思考

1. 深刻认识到 Z3 作为逻辑建模与约束求解工具的价值

    无论在学术研究（程序验证、模型检测、逻辑推理）还是日常问题分析中，Z3 都展现出了极高的灵活性和表达能力，是学习形式化方法的理想工具。

2. 在大模型时代，符号推理依旧不可替代

    传统的符号逻辑具有严谨性、确定性、可验证性，而这些正是当下纯数据驱动的大模型难以做到的。将符号系统与大模型结合，是提升 AI 可靠性的关键方向。

3. 理解并实践了“LLM + SMT Solver” 的协同机制

    大模型负责自然语言理解和抽象建模；Z3 负责精确逻辑推理与约束求解。
    在亲自构建集成系统后，我对如何结合两者增强智能体的推理能力有了更加直观和深入的认识，这对未来的研究方向具有很强的启发意义。