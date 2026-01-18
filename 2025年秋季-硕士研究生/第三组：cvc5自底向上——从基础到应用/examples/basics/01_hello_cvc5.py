#!/usr/bin/env python3
"""
cvc5 基础示例 1：Hello cvc5
============================

这是最简单的 cvc5 示例，演示：
1. 如何导入 cvc5 的 Pythonic API
2. 如何创建变量
3. 如何添加约束
4. 如何求解并获取结果

问题描述：
    找到两个正整数 x 和 y，使得 x + y = 5

"""

from cvc5.pythonic import *


def hello_cvc5():
    """最简单的 cvc5 示例"""

    print("=" * 60)
    print("cvc5 示例 1：Hello cvc5")
    print("=" * 60)
    print()

    # 步骤 1：创建整数变量
    # Ints('x y') 会创建两个整数变量，类似于数学中的未知数
    x, y = Ints('x y')
    print("📌 步骤 1：创建变量 x, y（整数类型）")
    print()

    # 步骤 2：定义约束
    # 我们要求：x + y = 5，并且 x > 0, y > 0
    constraints = [
        x + y == 5,  # 约束 1：和为 5
        x > 0,       # 约束 2：x 是正整数
        y > 0,       # 约束 3：y 是正整数
    ]

    print("📌 步骤 2：定义约束")
    print(f"   - x + y = 5")
    print(f"   - x > 0")
    print(f"   - y > 0")
    print()

    # 步骤 3：调用求解器
    # solve() 函数会自动创建求解器，添加约束，并求解
    print("📌 步骤 3：调用 SMT 求解器...")
    print()

    result = solve(*constraints)

    # 步骤 4：解释结果
    # solve() 返回的结果会自动打印模型（如果有解）
    # 模型就是满足所有约束的变量赋值

    print()
    print("📊 结果说明：")
    print("   cvc5 找到了一组满足所有约束的解")
    print("   其中一个可能的解：x = 1, y = 4")
    print("   注意：可能还有其他解（如 x=2, y=3 或 x=3, y=2）")
    print("   SMT 求解器通常返回找到的第一个解")
    print()


def explicit_solver_example():
    """使用显式的 Solver 对象（更灵活的方式）"""

    print("=" * 60)
    print("进阶示例：显式使用 Solver 对象")
    print("=" * 60)
    print()

    # 创建求解器对象
    solver = Solver()

    # 创建变量
    x, y = Ints('x y')

    # 添加约束
    solver.add(x + y == 5)
    solver.add(x > 0)
    solver.add(y > 0)

    print("📌 添加了 3 个约束到求解器")
    print()

    # 检查可满足性
    result = solver.check()
    print(f"🔍 求解结果：{result}")
    print()

    if result == sat:
        # 获取模型（变量的具体值）
        model = solver.model()
        print("✅ 问题可满足！找到的解：")
        print(f"   x = {model[x]}")
        print(f"   y = {model[y]}")
        print()

        # 验证解的正确性
        x_val = model[x].as_long()
        y_val = model[y].as_long()
        print("🔬 验证解的正确性：")
        print(f"   x + y = {x_val} + {y_val} = {x_val + y_val} ✓")
        print(f"   x > 0：{x_val} > 0 = {x_val > 0} ✓")
        print(f"   y > 0：{y_val} > 0 = {y_val > 0} ✓")
    elif result == unsat:
        print("❌ 问题不可满足（不存在解）")
    else:
        print("❓ 求解器无法确定（可能是超时或其他原因）")

    print()


def multiple_solutions_example():
    """演示如何获取多个不同的解"""

    print("=" * 60)
    print("进阶示例：获取多个不同的解")
    print("=" * 60)
    print()

    solver = Solver()
    x, y = Ints('x y')

    # 基本约束
    solver.add(x + y == 5)
    solver.add(x > 0)
    solver.add(y > 0)

    solutions = []

    for i in range(1, 4):  # 尝试找 3 个不同的解
        result = solver.check()

        if result == sat:
            model = solver.model()
            x_val = model[x].as_long()
            y_val = model[y].as_long()

            solutions.append((x_val, y_val))
            print(f"解 {i}：x = {x_val}, y = {y_val}")

            # 添加约束，排除这个解，以便找到不同的解
            # "不要再给我这个解"
            solver.add(Or(x != x_val, y != y_val))
        else:
            print(f"没有更多解了（已找到 {len(solutions)} 个）")
            break

    print()
    print(f"📊 总共找到 {len(solutions)} 个不同的解")
    print()


def main():
    """主函数"""

    # 示例 1：最简单的用法
    hello_cvc5()

    # 示例 2：显式使用 Solver 对象
    explicit_solver_example()

    # 示例 3：获取多个解
    multiple_solutions_example()



if __name__ == "__main__":
    main()
