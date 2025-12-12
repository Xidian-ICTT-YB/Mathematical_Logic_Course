#!/usr/bin/env python3
"""
cvc5 进阶示例：量词逻辑
============================

这个示例展示如何使用 cvc5 处理带量词的一阶逻辑公式。

内容包括：
1. 存在量词（∃）
2. 全称量词（∀）
3. 量词嵌套
4. 量词消除

"""

from cvc5.pythonic import *
import time


def existential_quantifier_example():
    """
    存在量词示例

    命题：∃x. (x > 5 ∧ x < 10)
    含义："存在一个 x，使得 x 大于 5 且小于 10"
    """

    print("=" * 60)
    print("示例 1：存在量词（∃）")
    print("=" * 60)
    print()

    print("📌 命题：∃x. (x > 5 ∧ x < 10)")
    print("   含义：存在一个 x，使得 x 大于 5 且小于 10")
    print()

    # 创建整数变量
    x = Int('x')

    # 定义存在量词公式
    # Exists([x], ...) 表示"存在 x 使得..."
    formula = Exists([x], And(x > 5, x < 10))

    solver = Solver()
    solver.add(formula)

    print("🔍 检查命题是否成立...")
    result = solver.check()

    if result == sat:
        print("✅ 命题为真！")
        print("   （显然，x=6, 7, 8, 9 都满足条件）")
    else:
        print("❌ 命题为假")

    print()


def universal_quantifier_example():
    """
    全称量词示例

    命题：∀x. (x > 0 → x² > 0)
    含义："对于所有正数 x，x 的平方也是正数"
    """

    print("=" * 60)
    print("示例 2：全称量词（∀）")
    print("=" * 60)
    print()

    print("📌 命题：∀x. (x > 0 → x² > 0)")
    print("   含义：对于所有正数 x，x 的平方也是正数")
    print()

    x = Int('x')

    # 全称量词：ForAll([x], ...)
    # 表示"对于所有 x"
    formula = ForAll([x], Implies(x > 0, x*x > 0))

    solver = Solver()
    solver.add(formula)

    print("🔍 检查命题是否成立...")
    result = solver.check()

    if result == sat:
        print("✅ 命题为真！")
        print("   （这是数学事实：正数的平方必然是正数）")
    else:
        print("❌ 命题为假")

    print()


def nested_quantifiers_example():
    """
    嵌套量词示例

    命题：∀x. ∃y. (y > x)
    含义："对于任意 x，总存在一个 y 大于 x"
    """

    print("=" * 60)
    print("示例 3：嵌套量词")
    print("=" * 60)
    print()

    print("📌 命题：∀x. ∃y. (y > x)")
    print("   含义：对于任意 x，总存在一个 y 大于 x")
    print("   （这在整数域中是成立的，因为总有 y = x + 1）")
    print()

    x = Int('x')
    y = Int('y')

    # 嵌套量词
    formula = ForAll([x], Exists([y], y > x))

    solver = Solver()
    solver.add(formula)

    print("🔍 检查命题是否成立...")
    start_time = time.time()
    result = solver.check()
    elapsed = time.time() - start_time

    print(f"⏱️  求解时间：{elapsed:.6f} 秒")

    if result == sat:
        print("✅ 命题为真！")
        print("   （因为整数没有最大值）")
    else:
        print("❌ 命题为假")

    print()


def quantifier_with_parameters():
    """
    带参数的量词

    检查：对于参数 a=50, b=50
    命题：∀x. (x > a → ∃y. (y > b ∧ y > x))
    """

    print("=" * 60)
    print("示例 4：带参数的量词")
    print("=" * 60)
    print()

    # 参数
    a = 50
    b = 50

    print(f"📌 参数：a = {a}, b = {b}")
    print()
    print("📌 命题：∀x. (x > a → ∃y. (y > b ∧ y > x))")
    print("   含义：对于所有大于 a 的 x，")
    print("        都存在一个 y，使得 y 大于 b 且 y 大于 x")
    print()

    x = Int('x')
    y = Int('y')

    # 构建公式
    inner_exists = Exists([y], And(y > b, y > x))
    formula = ForAll([x], Implies(x > a, inner_exists))

    solver = Solver()
    solver.add(formula)

    print("🔍 检查命题是否成立...")
    result = solver.check()

    if result == sat:
        print("✅ 命题为真！")
        print(f"   对于任意 x > {a}，总能找到 y 同时满足 y > {b} 和 y > x")
        print(f"   （例如取 y = max(x, b) + 1）")
    else:
        print("❌ 命题为假")

    print()


def main():
    """主函数"""

    # 示例 1：存在量词
    existential_quantifier_example()

    # 示例 2：全称量词
    universal_quantifier_example()

    # 示例 3：嵌套量词
    nested_quantifiers_example()

    # 示例 4：带参数的量词
    quantifier_with_parameters()


if __name__ == "__main__":
    main()
