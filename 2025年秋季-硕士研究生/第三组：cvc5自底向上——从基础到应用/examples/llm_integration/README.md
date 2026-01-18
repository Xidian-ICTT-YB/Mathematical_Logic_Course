# LLM + cvc5 自然语言约束求解器

## 项目简介

这个模块展示了如何将大语言模型(LLM)与 cvc5 SMT 求解器结合,实现自然语言到约束求解的转换。

**核心思路**:
- 用户用中文描述问题
- LLM 理解并生成 cvc5 Python 代码
- 自动执行代码得到求解结果

这种方式降低了使用 SMT 求解器的门槛,让非专业用户也能利用形式化方法解决问题。

## 快速开始

### 安装依赖

```bash
# 安装必要的库
pip install cvc5 openai python-dotenv
```

### 配置API

**步骤1:** 复制配置文件模板
```bash
cd examples/llm_integration
cp .env.example .env
```

**步骤2:** 编辑 `.env` 文件,填入你的API配置
```bash
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

**注意:** `.env` 文件包含敏感信息,不会被提交到Git

### 运行示例

```bash
# 命令行模式(快速测试)
python nl2smt_solver.py "找三个正整数,和为15,第一个数是偶数"

# 交互模式
python nl2smt_solver.py

# 运行演示脚本(推荐用于展示)
./demo.sh
```

## 使用示例

### 示例 1: 整数约束
```
问题: 找三个正整数,它们的和是15,第一个数是偶数

生成的代码:
from cvc5.pythonic import *

x, y, z = Ints('x y z')
solver = Solver()
solver.add(x > 0, y > 0, z > 0)
solver.add(x + y + z == 15)
solver.add(x % 2 == 0)

if solver.check() == sat:
    model = solver.model()
    print(f"x = {model[x]}, y = {model[y]}, z = {model[z]}")

输出: x = 2, y = 1, z = 12
```

### 示例 2: 方程求解
```
问题: 解方程 x^2 - 5*x + 6 = 0

生成的代码:
from cvc5.pythonic import *

x = Real('x')
solver = Solver()
solver.add(x * x - 5 * x + 6 == 0)

if solver.check() == sat:
    model = solver.model()
    print(f"x = {model[x]}")

输出: x = 2
```

### 示例 3: 逻辑推理
```
问题: 有三个人A、B、C,A比B年龄大,C比A小,B是25岁,问C可能多少岁

生成的代码:
from cvc5.pythonic import *

A, B, C = Ints('A B C')
solver = Solver()
solver.add(A > B)
solver.add(C < A)
solver.add(B == 25)
solver.add(A > 0, C > 0)

if solver.check() == sat:
    model = solver.model()
    print(f"A = {model[A]}, C = {model[C]}")

输出: A = 26, C = 1
```

## 技术架构

```
用户输入(自然语言)
    ↓
LLM (GPT-4 / Qwen2.5-Coder)
    ↓
cvc5 Python 代码
    ↓
Python 解释器执行
    ↓
SMT 求解结果
```

## 支持的 LLM 后端

1. **OpenAI API**
   - 官方API或兼容的中转服务
   - 通过 `.env` 文件配置
   - 支持自定义模型和BASE_URL

2. **本地 Ollama** (免费)
   - 安装: https://ollama.ai/
   - 运行: `ollama pull qwen2.5-coder:7b`
   - 无需配置,自动尝试连接本地服务

## 文件说明

- `nl2smt_solver.py`: 主程序,处理自然语言输入并求解
- `prompts.py`: LLM 提示词模板,包含 few-shot 示例
- `demo_queries.py`: 预设的演示问题集合
- `README.md`: 本文件

## 局限性

1. **LLM 生成的代码可能有错**: 需要人工检查复杂问题
2. **仅支持简单约束**: 复杂的组合优化问题可能生成失败
3. **依赖 LLM 服务**: 需要网络连接或本地模型

