#!/usr/bin/env python3
"""
cvc5 基础示例 2：布尔逻辑
============================

这个示例展示如何使用 cvc5 求解布尔逻辑问题（SAT 问题）。

内容包括：
1. 基本的 SAT 问题求解
2. 逻辑运算符（AND, OR, NOT, IMPLIES）
3. 不可满足（UNSAT）问题分析
4. UNSAT Core（不可满足核心）的获取

"""

from cvc5.pythonic import *
import time


def basic_sat_example():
    """
    基础 SAT 问题

    问题：给定以下布尔子句，是否存在满足所有子句的赋值？
    1. (a ∨ b)
    2. (¬a ∨ c)
    3. (¬b ∨ ¬c ∨ d)
    4. (¬d ∨ e)
    5. (a ∨ ¬e)
    6. (b ∨ c ∨ d ∨ ¬e)
    7. (¬a ∨ ¬b ∨ ¬c ∨ e)

    这是一个标准的 CNF（合取范式）SAT 问题
    """

    print("=" * 60)
    print("示例 1：基础 SAT 问题求解")
    print("=" * 60)
    print()

    # 创建布尔变量
    a, b, c, d, e = Bools('a b c d e')

    print("📌 创建了 5 个布尔变量：a, b, c, d, e")
    print()

    # 定义约束（CNF 子句）
    constraints = [
        Or(a, b),                    # 子句 1
        Or(Not(a), c),               # 子句 2
        Or(Not(b), Not(c), d),       # 子句 3
        Or(Not(d), e),               # 子句 4
        Or(a, Not(e)),               # 子句 5
        Or(b, c, d, Not(e)),         # 子句 6
        Or(Not(a), Not(b), Not(c), e),  # 子句 7
    ]

    print("📌 定义了 7 个子句（CNF 格式）：")
    print("   1. (a ∨ b)")
    print("   2. (¬a ∨ c)")
    print("   3. (¬b ∨ ¬c ∨ d)")
    print("   4. (¬d ∨ e)")
    print("   5. (a ∨ ¬e)")
    print("   6. (b ∨ c ∨ d ∨ ¬e)")
    print("   7. (¬a ∨ ¬b ∨ ¬c ∨ e)")
    print()

    # 创建求解器并求解
    solver = Solver()
    solver.add(constraints)

    print("🔍 开始求解...")
    start_time = time.time()
    result = solver.check()
    elapsed = time.time() - start_time

    print(f"⏱️  求解时间：{elapsed:.6f} 秒")
    print(f"📊 结果：{result}")
    print()

    if result == sat:
        model = solver.model()
        print("✅ 问题可满足！找到的一组解：")
        print(f"   a = {model[a]}")
        print(f"   b = {model[b]}")
        print(f"   c = {model[c]}")
        print(f"   d = {model[d]}")
        print(f"   e = {model[e]}")

        # 验证几个子句
        print()
        print("🔬 验证部分子句：")
        a_val = is_true(model[a])
        b_val = is_true(model[b])
        c_val = is_true(model[c])
        print(f"   子句 1：(a ∨ b) = ({a_val} ∨ {b_val}) = {a_val or b_val} ✓")
        print(f"   子句 2：(¬a ∨ c) = ({not a_val} ∨ {c_val}) = {(not a_val) or c_val} ✓")
    else:
        print("❌ 问题不可满足")

    print()


def unsat_example():
    """
    不可满足（UNSAT）问题示例

    问题：要求所有变量都为 True，同时至少有一个为 False
    这显然是矛盾的
    """

    print("=" * 60)
    print("示例 2：不可满足（UNSAT）问题")
    print("=" * 60)
    print()

    a, b, c, d, e = Bools('a b c d e')

    solver = Solver()

    # 添加原来的 SAT 约束
    solver.add(Or(a, b))
    solver.add(Or(Not(a), c))
    solver.add(Or(Not(b), Not(c), d))
    solver.add(Or(Not(d), e))
    solver.add(Or(a, Not(e)))
    solver.add(Or(b, c, d, Not(e)))
    solver.add(Or(Not(a), Not(b), Not(c), e))

    # 添加矛盾约束：强制所有变量为 True
    solver.add(a, b, c, d, e)

    # 同时要求至少有一个为 False
    solver.add(Or(Not(a), Not(b), Not(c), Not(d), Not(e)))

    print("📌 添加了矛盾约束：")
    print("   - 要求 a, b, c, d, e 都为 True")
    print("   - 同时要求至少有一个为 False")
    print()

    print("🔍 开始求解...")
    result = solver.check()

    print(f"📊 结果：{result}")
    print()

    if result == unsat:
        print("✅ 正确识别出矛盾！")
        print("   这些约束是互相冲突的，不存在满足所有约束的赋值")

        # 注意：cvc5 的 Pythonic API 可能不直接支持 unsat_core()
        # 这是一个高级功能，通常需要使用基础 API
        print()
        print("💡 提示：如需分析 UNSAT Core，可使用基础 API")
        print("   （参见 examples/intermediate/08_unsat_core.py）")

    print()


def logical_operators_demo():
    """
    演示各种逻辑运算符
    """

    print("=" * 60)
    print("示例 3：逻辑运算符演示")
    print("=" * 60)
    print()

    a, b, c = Bools('a b c')

    # AND（合取）
    print("1️⃣  AND（合取）：a ∧ b ∧ c")
    solver1 = Solver()
    solver1.add(And(a, b, c))
    if solver1.check() == sat:
        m = solver1.model()
        print(f"   解：a={m[a]}, b={m[b]}, c={m[c]}")
    print()

    # OR（析取）
    print("2️⃣  OR（析取）：a ∨ b ∨ c")
    solver2 = Solver()
    solver2.add(Or(a, b, c))
    if solver2.check() == sat:
        m = solver2.model()
        print(f"   解：a={m[a]}, b={m[b]}, c={m[c]}")
        print(f"   （至少有一个为 True）")
    print()

    # NOT（否定）
    print("3️⃣  NOT（否定）：¬a")
    solver3 = Solver()
    solver3.add(Not(a))
    solver3.add(a == True)  # 矛盾
    result = solver3.check()
    print(f"   与 (a = True) 组合：{result}（矛盾）")
    print()

    # IMPLIES（蕴含）
    print("4️⃣  IMPLIES（蕴含）：a → b")
    print("   含义：如果 a 为 True，则 b 必须为 True")
    solver4 = Solver()
    solver4.add(Implies(a, b))
    solver4.add(a == True)
    if solver4.check() == sat:
        m = solver4.model()
        print(f"   当 a=True 时，b={m[b]}（必须为 True）")
    print()

    # XOR（异或）
    print("5️⃣  XOR（异或）：a ⊕ b")
    print("   含义：a 和 b 有且仅有一个为 True")
    solver5 = Solver()
    # XOR 可以表示为：(a ∨ b) ∧ ¬(a ∧ b)
    solver5.add(Or(a, b))
    solver5.add(Not(And(a, b)))
    if solver5.check() == sat:
        m = solver5.model()
        print(f"   解：a={m[a]}, b={m[b]}")
    print()

    # IFF（当且仅当）
    print("6️⃣  IFF（双向蕴含）：a ↔ b")
    print("   含义：a 和 b 必须同时为 True 或同时为 False")
    solver6 = Solver()
    solver6.add(a == b)  # 等价于 IFF
    if solver6.check() == sat:
        m = solver6.model()
        print(f"   解：a={m[a]}, b={m[b]}（值相同）")
    print()


def n_variable_sat(n=10):
    """
    生成一个 n 变量的随机 SAT 问题
    用于性能测试
    """

    print("=" * 60)
    print(f"示例 4：{n} 变量 SAT 性能测试")
    print("=" * 60)
    print()

    # 创建 n 个布尔变量
    vars = [Bool(f'x{i}') for i in range(n)]

    # 生成一些随机子句
    solver = Solver()

    # 添加约束：至少有一个为 True
    solver.add(Or(*vars))

    # 添加约束：不能所有都为 True
    solver.add(Not(And(*vars)))

    print(f"📌 创建了 {n} 个变量")
    print(f"📌 添加了约束：")
    print(f"   - 至少有一个为 True")
    print(f"   - 不能所有都为 True")
    print()

    print("🔍 开始求解...")
    start_time = time.time()
    result = solver.check()
    elapsed = time.time() - start_time

    print(f"⏱️  求解时间：{elapsed:.6f} 秒")
    print(f"📊 结果：{result}")

    if result == sat:
        model = solver.model()
        true_count = sum(1 for v in vars if is_true(model[v]))
        print(f"✅ 找到解：{true_count} 个变量为 True")

    print()


def main():
    """主函数"""

    # 示例 1：基础 SAT
    basic_sat_example()

    # 示例 2：UNSAT 问题
    unsat_example()

    # 示例 3：逻辑运算符
    logical_operators_demo()

    # 示例 4：性能测试
    n_variable_sat(10)

if __name__ == "__main__":
    main()
