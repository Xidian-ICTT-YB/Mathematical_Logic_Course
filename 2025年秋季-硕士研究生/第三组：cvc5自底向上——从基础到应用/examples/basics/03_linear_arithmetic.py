#!/usr/bin/env python3
"""
cvc5 基础示例 3：线性算术
============================

这个示例展示如何使用 cvc5 求解线性算术约束问题。

内容包括：
1. 整数线性算术（QF_LIA）
2. 实数线性算术（QF_LRA）
3. 整数规划问题
4. 不等式约束
5. 混合整数实数约束

"""

from cvc5.pythonic import *
import time


def integer_arithmetic_basics():
    """
    整数算术基础

    问题：找到整数 x, y, z 满足：
    - x + y + z < 15
    - x + 3y + 2z > 10
    - x, y, z >= 0
    """

    print("=" * 60)
    print("示例 1：整数线性算术基础")
    print("=" * 60)
    print()

    # 创建整数变量
    x, y, z = Ints('x y z')

    print("📌 问题描述：")
    print("   找到整数 x, y, z 满足：")
    print("   - x + y + z < 15")
    print("   - x + 3y + 2z > 10")
    print("   - x, y, z >= 0")
    print()

    # 创建求解器
    solver = Solver()

    # 添加约束
    solver.add(x + y + z < 15)
    solver.add(x + 3*y + 2*z > 10)
    solver.add(x >= 0, y >= 0, z >= 0)

    print("🔍 开始求解...")
    result = solver.check()

    if result == sat:
        model = solver.model()
        x_val = model[x].as_long()
        y_val = model[y].as_long()
        z_val = model[z].as_long()

        print("✅ 找到解：")
        print(f"   x = {x_val}")
        print(f"   y = {y_val}")
        print(f"   z = {z_val}")
        print()

        # 验证
        print("🔬 验证：")
        sum1 = x_val + y_val + z_val
        sum2 = x_val + 3*y_val + 2*z_val
        print(f"   x + y + z = {sum1} < 15? {sum1 < 15} ✓")
        print(f"   x + 3y + 2z = {sum2} > 10? {sum2 > 10} ✓")

    print()


def real_arithmetic_example():
    """
    实数算术示例

    问题：在实数域中求解
    - 0 < x < 1
    - 0 < y < 1
    - x + y = 1
    - x <= y
    """

    print("=" * 60)
    print("示例 2：实数线性算术")
    print("=" * 60)
    print()

    # 创建实数变量
    x, y = Reals('x y')

    print("📌 问题描述（实数域）：")
    print("   - 0 < x < 1")
    print("   - 0 < y < 1")
    print("   - x + y = 1")
    print("   - x <= y")
    print()

    solver = Solver()
    solver.add(x > 0, x < 1)
    solver.add(y > 0, y < 1)
    solver.add(x + y == 1)
    solver.add(x <= y)

    print("🔍 开始求解...")
    result = solver.check()

    if result == sat:
        model = solver.model()
        print("✅ 找到解：")
        print(f"   x = {model[x]}")
        print(f"   y = {model[y]}")
        print()

        # 将分数转换为小数（如果可能）
        x_val = model[x]
        y_val = model[y]
        print("💡 提示：cvc5 返回的实数可能是精确分数形式")
        print(f"   例如：1/2 表示 0.5")

    print()


def integer_programming_example():
    """
    整数规划示例

    问题：最小化目标函数
    - 目标：找到 x^2 + y^2 + z^2 的最小值
    - 约束：x + y + z < 15
    -       x + 3y + 2z > 10
    -       x, y, z >= 0

    注意：SMT 求解器不是优化器，但我们可以通过迭代找最小值
    """

    print("=" * 60)
    print("示例 3：整数规划（寻找最小值）")
    print("=" * 60)
    print()

    x, y, z = Ints('x y z')

    # 基础约束
    base_constraints = [
        x + y + z < 15,
        x + 3*y + 2*z > 10,
        x >= 0, y >= 0, z >= 0
    ]

    print("📌 目标：最小化 x² + y² + z²")
    print("📌 约束：")
    print("   - x + y + z < 15")
    print("   - x + 3y + 2z > 10")
    print("   - x, y, z >= 0")
    print()

    # 迭代查找最小值
    print("🔍 迭代查找最小目标值...")
    print()

    best_value = None
    best_solution = None

    for target in range(500):  # 最多尝试 500 次
        solver = Solver()
        solver.add(base_constraints)

        # 添加目标约束
        target_func = x*x + y*y + z*z
        solver.add(target_func == target)

        start_time = time.time()
        result = solver.check()
        elapsed = time.time() - start_time

        if result == sat:
            model = solver.model()
            x_val = model[x].as_long()
            y_val = model[y].as_long()
            z_val = model[z].as_long()

            best_value = target
            best_solution = (x_val, y_val, z_val)

            print(f"✓ 找到目标值 {target}：", end="")
            print(f"x={x_val}, y={y_val}, z={z_val} ", end="")
            print(f"({elapsed:.6f}s)")

            # 找到第一个可行解就停止（最小值）
            break
        else:
            # 可以偶尔打印进度
            if target % 100 == 0 and target > 0:
                print(f"  目标值 {target} 不可行...")

    print()
    if best_solution:
        print(f"🎯 最小目标值：{best_value}")
        print(f"   最优解：x={best_solution[0]}, y={best_solution[1]}, z={best_solution[2]}")

    print()


def system_of_equations():
    """
    求解线性方程组

    方程组：
    2x + 3y = 13
    x - y = 1
    """

    print("=" * 60)
    print("示例 4：求解线性方程组")
    print("=" * 60)
    print()

    x, y = Ints('x y')

    print("📌 线性方程组：")
    print("   2x + 3y = 13")
    print("   x - y = 1")
    print()

    solver = Solver()
    solver.add(2*x + 3*y == 13)
    solver.add(x - y == 1)

    print("🔍 开始求解...")
    result = solver.check()

    if result == sat:
        model = solver.model()
        x_val = model[x].as_long()
        y_val = model[y].as_long()

        print("✅ 方程组有解：")
        print(f"   x = {x_val}")
        print(f"   y = {y_val}")
        print()

        # 验证
        print("🔬 验证：")
        eq1 = 2*x_val + 3*y_val
        eq2 = x_val - y_val
        print(f"   2x + 3y = 2×{x_val} + 3×{y_val} = {eq1} ✓")
        print(f"   x - y = {x_val} - {y_val} = {eq2} ✓")
    else:
        print("❌ 方程组无解（可能是矛盾的）")

    print()


def mixed_constraints():
    """
    混合约束示例

    同时包含等式和不等式
    """

    print("=" * 60)
    print("示例 5：混合等式和不等式约束")
    print("=" * 60)
    print()

    x, y, z = Ints('x y z')

    print("📌 约束：")
    print("   - x + y = 10 （等式）")
    print("   - y + z > 5  （不等式）")
    print("   - x < y      （不等式）")
    print("   - z >= 0     （不等式）")
    print()

    solver = Solver()
    solver.add(x + y == 10)
    solver.add(y + z > 5)
    solver.add(x < y)
    solver.add(z >= 0)

    print("🔍 开始求解...")
    result = solver.check()

    if result == sat:
        model = solver.model()
        x_val = model[x].as_long()
        y_val = model[y].as_long()
        z_val = model[z].as_long()

        print("✅ 找到解：")
        print(f"   x = {x_val}")
        print(f"   y = {y_val}")
        print(f"   z = {z_val}")

    print()


def main():
    """主函数"""

    # 示例 1：整数算术基础
    integer_arithmetic_basics()

    # 示例 2：实数算术
    real_arithmetic_example()

    # 示例 3：整数规划
    integer_programming_example()

    # 示例 4：线性方程组
    system_of_equations()

    # 示例 5：混合约束
    mixed_constraints()



if __name__ == "__main__":
    main()
