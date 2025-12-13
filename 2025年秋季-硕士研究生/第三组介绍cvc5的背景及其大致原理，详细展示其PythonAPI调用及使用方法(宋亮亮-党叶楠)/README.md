# CVC5

## 1. 小组成员

|  学号 | 姓名 |
|------|------|
|25171111421     | 宋亮亮      |
|25171111422     | 党叶楠      |

## 2. 项目思考

在本次课程项目中，我们深入学习和实践了 CVC5 SMT 求解器，我们不仅掌握了 CVC5 的使用方法，更重要的是：
- 理解了 SMT 求解器的工作原理
- 培养了约束建模的思维能力
- 体验了形式化方法在实际问题中的应用
- 认识到数理逻辑在计算机科学中的核心地位

**未来展望**：我们希望将这些知识应用到实际项目中，如程序静态分析、智能合约验证等领域，让形式化方法真正发挥价值。同时，我们也认识到 SMT 求解器仍有很多待解决的挑战，如量词处理效率、非线性算术求解等，这些都是值得深入研究的方向。

---

## 3. 项目简介

CVC5 是一个开源的自动定理证明器和满足性模理论求解器。它是 CVC 系列求解器的最新版本，继承并发展了CVC、CVC3 和 CVC4 的技术。


## 4. Python API 使用指南

### 4.1 安装

```bash
pip install cvc5
```

### 4.2 基本工作流程

1. **创建求解器实例**
2. **创建类型和变量**
3. **构建约束公式**
4. **添加断言**
5. **检查可满足性**
6. **提取模型（如果可满足）**

### 4.3 核心API概览

#### Solver类

| 方法 | 描述 |
|------|------|
| `Solver()` | 创建求解器实例 |
| `setLogic(logic)` | 设置逻辑（如 "QF_LIA", "ALL"） |
| `setOption(opt, val)` | 设置选项 |
| `mkConst(sort, name)` | 创建常量（变量） |
| `mkVar(sort, name)` | 创建绑定变量（用于量词） |
| `mkTerm(kind, *args)` | 创建复合项 |
| `assertFormula(term)` | 添加断言 |
| `checkSat()` | 检查可满足性 |
| `getValue(term)` | 获取项的值 |

#### 类型创建

| 方法 | 描述 |
|------|------|
| `getBooleanSort()` | 布尔类型 |
| `getIntegerSort()` | 整数类型 |
| `getRealSort()` | 实数类型 |
| `mkBitVectorSort(n)` | n位位向量类型 |
| `mkArraySort(idx, elem)` | 数组类型 |
| `getStringSort()` | 字符串类型 |
| `mkFunctionSort(args, ret)` | 函数类型 |

#### 常用Kind（操作符）

**逻辑运算**：
- `Kind.AND`, `Kind.OR`, `Kind.NOT`
- `Kind.IMPLIES`, `Kind.XOR`, `Kind.ITE`

**算术运算**：
- `Kind.ADD`, `Kind.SUB`, `Kind.MULT`
- `Kind.LT`, `Kind.LEQ`, `Kind.GT`, `Kind.GEQ`
- `Kind.EQUAL`, `Kind.DISTINCT`

**位向量**：
- `Kind.BITVECTOR_AND`, `Kind.BITVECTOR_OR`, `Kind.BITVECTOR_XOR`
- `Kind.BITVECTOR_ADD`, `Kind.BITVECTOR_MULT`
- `Kind.BITVECTOR_CONCAT`, `Kind.BITVECTOR_EXTRACT`

**数组**：
- `Kind.SELECT`（读取）
- `Kind.STORE`（写入）

**量词**：
- `Kind.FORALL`（全称量词）
- `Kind.EXISTS`（存在量词）

### 4.4 代码示例

详细的示例代码请参见 `code_examples/` 目录：

- **01_basic_usage.py** - 基础使用：布尔逻辑、整数/实数算术、增量求解
- **02_advanced_features.py** - 高级特性：数组、位向量、量词、未解释函数、数据类型、字符串
- **03_sudoku_solver.py** - 应用实例：数独求解器
- **04_n_queens.py** - 应用实例：N皇后问题
- **05_circuit_verification.py** - 应用实例：逻辑电路验证

## 运行示例

```bash
# 基础示例
python code_examples/01_basic_usage.py

# 高级特性
python code_examples/02_advanced_features.py

# 数独求解器
python code_examples/03_sudoku_solver.py

# N皇后问题
python code_examples/04_n_queens.py

# 电路验证
python code_examples/05_circuit_verification.py
```
## 参考资源

- [CVC5 官方网站](https://cvc5.github.io/)
- [CVC5 GitHub](https://github.com/cvc5/cvc5)
- [API 文档](https://cvc5.github.io/docs/latest/api/python/python.html)
- [SMT-LIB 标准](https://smtlib.cs.uiowa.edu/)


