# z3-4

Z3第4组_z3原理介绍与多方面应用

## 小组成员

| 学号         | 姓名   |
| ------------ | ------ |
| 25030020049G | 郝仕达 |
| 25031212059  | 肖宇   |
| 25031212169  | 张子豪 |

## 工作简介

1.  **理论调研**：梳理了 Z3 的发展历程、基于 **CDCL(T)** 的核心架构等
2.  **工具演示**：基于 Python API (`z3-solver`) 编写了多个实际案例脚本，包括：
    *   **密码学分析**：利用约束求解破解基于 LCG 的弱加密算法。
    *   **程序合成**：基于输入输出范例自动推导函数逻辑。
    *   **形式化验证**：证明浮点数运算结合律的失效（寻找反例）。
    *   **运筹调度**：解决多任务时间规划问题。
3.  **应用拓展**：探讨了 Z3 在神经网络验证、智能合约安全、生物信息学等前沿领域的应用现状。

## 相关链接

- **核心工具**：*Z3 GitHub 仓库* [Z3Prover/z3: The Z3 Theorem Prover](https://github.com/Z3Prover/z3)
- **Z3 PyPI (Python Bindings)**: [z3-solver · PyPI](https://pypi.org/project/z3-solver/)
- [Documentation for Online Z3 Guide | Online Z3 Guide](https://microsoft.github.io/z3guide/)
- **Z3Py 官方指南 (Programming Z3)**: [Z3Py Guide](https://ericpony.github.io/z3py-tutorial/guide-examples.htm)
- **SMT-LIB 标准**:[SMT-LIB The Satisfiability Modulo Theories Library](https://smt-lib.org/)

## 思考

通过本次对 Z3 的调研与实践，我们深刻体会到**“计算逻辑”**作为计算机科学基石的实用价值：

1. **思维范式的转变**：体验了从命令式编程向**声明式编程**的跨越。我们只需定义“问题约束”而非编写繁琐的步骤，这种思维方式极大地简化了运筹调度等复杂问题的解决难度。
2. **理论与工程的统一**：Z3 让我们看到了理论算法落地的力量。即便面对理论上的 NP-Complete 问题，通过 **CDCL** 等工程优化手段，依然能实现工业级的高效求解。
3. **正确性的保障**：认识到形式化验证不可替代的地位。传统测试难以覆盖所有边界，而基于 SMT 的数学证明能为自动驾驶、芯片设计等安全关键系统提供严密的可靠性保障。
4. **前沿展望**：Z3 的精确推理能力与大模型（LLM）的结合（Neuro-symbolic AI）潜力巨大，将是未来构建可解释、可信人工智能的重要基石。
