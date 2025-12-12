# cvc5 SMT 求解器介绍与使用演示

> 西安电子科技大学 数理逻辑课程 - 第三小组

## 小组成员

| 学号 | 姓名 |
|------|------|
| 25171111405 | 陆海健 |
| 25031212188 | 吕天 |
| 25031212307 | 苏佳 |

## 项目简介

本项目介绍了 cvc5 SMT（Satisfiability Modulo Theories，可满足性模理论）求解器的基本原理和使用方法，包括：

- SMT 核心概念和 cvc5 架构原理
- 从基础到高级的 Python API 使用教程
- 实际应用案例：约束求解、形式化验证、有界模型检查
- Jupyter Notebook 交互式演示

---

## 项目结构

```
cvc5/
├── README.md                           # 项目总览
├── requirements.txt                    # Python 依赖
│
├── docs/                               # 理论文档
│   ├── 01_introduction.md              # cvc5 背景介绍
│   ├── 02_smt_basics.md                # SMT 核心概念
│   ├── 03_cvc5_architecture.md         # cvc5 架构原理
│   └── 04_api_guide.md                 # Python API 完整指南
│
├── examples/                           # 代码示例
│   ├── basics/                         # 基础篇
│   │   ├── 01_hello_cvc5.py           # 最简示例
│   │   ├── 02_boolean_logic.py        # 布尔逻辑
│   │   ├── 03_linear_arithmetic.py    # 线性算术
│   │   └── 04_data_types.py           # 数据类型
│   │
│   ├── intermediate/                   # 进阶篇
│   │   ├── 05_quantifiers.py          # 量词逻辑
│   │   ├── 06_arrays_theory.py        # 数组理论
│   │   ├── 07_bitvectors.py           # 位向量
│   │   └── 08_unsat_core.py           # 不可满足核心分析
│   │
│   ├── advanced/                       # 高级应用篇
│   │   ├── 09_sudoku_solver.py        # 数独求解器（带可视化）
│   │   ├── 10_n_queens.py             # N 皇后问题
│   │   ├── 11_graph_coloring.py       # 图着色问题
│   │   ├── 12_program_verification.py # 程序验证
│   │   └── 13_bounded_model_checking.py # 有界模型检查
│   │
│   └── llm_integration/                # LLM 集成
│       ├── nl2smt_solver.py           # 自然语言约束求解器
│       ├── prompts.py                 # LLM 提示词模板
│       └── README.md                  # 详细说明
│
├── notebooks/                          # Jupyter 演示
│   └── cvc5_presentation.ipynb        # 课堂展示 Notebook
│
├── utils/                              # 工具函数
│   ├── visualizer.py                  # 可视化工具
│   └── helpers.py                     # 通用辅助函数
│
└── Verilog-BMC/                        # Verilog 有界模型检查
    └── ...                             # BMC 相关代码和文档
```

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- `cvc5` - cvc5 Python API
- `matplotlib` - 可视化
- `numpy` - 数值计算
- `jupyter` - Notebook 支持

### 2. 运行示例

```bash
# 运行基础示例
python examples/basics/01_hello_cvc5.py

# 运行数独求解器
python examples/advanced/09_sudoku_solver.py

# 运行有界模型检查
python examples/advanced/13_bounded_model_checking.py
```

### 3. 查看交互式演示

```bash
jupyter notebook notebooks/cvc5_presentation.ipynb
```

---

## 学习路径

### 初学者
1. 阅读 `docs/01_introduction.md` 了解 cvc5 背景
2. 阅读 `docs/02_smt_basics.md` 理解 SMT 概念
3. 运行 `examples/basics/` 下的所有示例
4. 查看 `notebooks/cvc5_presentation.ipynb` 前半部分

### 进阶学习
1. 阅读 `docs/03_cvc5_architecture.md` 深入理解原理
2. 运行 `examples/intermediate/` 下的示例
3. 尝试修改示例代码，解决自己的问题

### 高级应用
1. 阅读 `docs/04_api_guide.md` 掌握完整 API
2. 研究 `examples/advanced/` 下的实战案例
3. 特别关注有界模型检查（BMC）示例

---

## 核心示例介绍

### 基础示例

#### 1. Hello cvc5 - 最简约束求解
```python
from cvc5.pythonic import *

x, y = Ints('x y')
solve(x + y == 5, x > 0, y > 0)
# 输出: [x = 1, y = 4] (或其他满足条件的解)
```

#### 2. 数独求解器
使用 cvc5 求解任意数独谜题，支持可视化输出。

#### 3. N 皇后问题
经典约束满足问题，演示如何用 SMT 求解器处理组合优化。

### 高级应用

#### 有界模型检查（Bounded Model Checking）
展示 cvc5 在形式化验证中的实际应用：

- 简单状态机验证（交通灯系统）
- 硬件电路正确性验证（加法器）
- 如何将系统建模为符号转换系统

#### LLM + cvc5 自然语言约束求解器
将大语言模型与 SMT 求解器结合,实现自然语言转约束求解:

```bash
cd examples/llm_integration
python nl2smt_solver.py "找三个正整数,和为10,第一个数是偶数"
```

- 用户用中文描述问题
- LLM 自动生成 cvc5 代码
- 执行求解并返回结果
- 详见 `examples/llm_integration/README.md`

---

## 相关链接

- [cvc5 GitHub](https://github.com/cvc5/cvc5)
- [cvc5 官方文档](https://cvc5.github.io/)
- [cvc5 Python API 文档](https://cvc5.github.io/docs/cvc5-1.2.1/api/python/pythonic/quickstart.html)
- [Z3 Theorem Prover](https://github.com/Z3Prover/z3) - 微软开发的 SMT 求解器
- [Yosys](https://github.com/YosysHQ/yosys) - 开源 Verilog 综合工具

---

## 主要思考

1. **SMT 求解器的实用性超出预期**

   在做这个项目之前,我们以为 SMT 求解器只是理论工具,但通过实现数独、N皇后等问题后发现,很多实际问题都可以转化为约束求解。特别是有界模型检查(BMC)部分,能用几十行代码验证硬件电路的正确性,这在传统测试中需要大量用例才能覆盖。

2. **形式化验证的门槛比想象中低**

   刚开始接触形式化验证时觉得很抽象,但 cvc5 的 Python API 让这个过程变得很直观。只要把问题的约束用代码表达出来,求解器就能自动推理。这个"声明式编程"的思路和平常写程序很不一样,需要转变思维方式。

3. **与 Z3 的对比**

   我们在选择工具时对比过 Z3 和 cvc5。Z3 的文档和社区更成熟,但 cvc5 在某些理论(特别是字符串理论和超越函数)上支持更好。最后选择 cvc5 也是因为它的 Pythonic API 更符合 Python 习惯,代码写起来更简洁。

4. **Verilog-BMC 的难点**

   在实现 Verilog 有界模型检查时遇到了不少问题。主要是 Verilog 语法解析和转换为 SMT 约束这部分,需要理解硬件电路的语义。不过这个过程让我们深刻体会到形式化方法在硬件验证中的价值,比随机测试要严谨得多。

5. **LLM + SMT 的协同价值**

   后期我们增加了 LLM 与 cvc5 的集成模块。这个思路是受课堂上其他组展示的启发,但我们的实现更注重实用性。LLM 负责理解自然语言并生成约束代码,SMT 求解器负责保证求解的正确性。这种"神经网络+符号系统"的结合,既降低了使用门槛,又保持了逻辑严谨性。

6. **项目的局限性**

   目前的示例都是相对简单的问题,对于大规模工程问题(比如操作系统验证、复杂协议验证)还需要更多的技巧和优化。SMT 求解器虽然强大,但在约束复杂度很高时性能会急剧下降,如何设计合理的抽象层次是个挑战。

---

## 许可证

MIT License

---

> 本项目所有代码均经过测试。运行环境要求: Python 3.8+
