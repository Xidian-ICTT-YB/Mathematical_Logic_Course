#!/usr/bin/env python3
"""
基础测试脚本 - 不依赖 LLM API
直接测试生成的代码是否能正确执行
"""

from cvc5.pythonic import *


def test_simple_constraint():
    """测试: 找三个正整数,和为15,第一个数是偶数"""
    print("\n" + "="*60)
    print("测试1: 整数约束问题")
    print("="*60)

    x, y, z = Ints('x y z')
    solver = Solver()

    solver.add(x > 0, y > 0, z > 0)  # 正整数
    solver.add(x + y + z == 15)       # 和为15
    solver.add(x % 2 == 0)            # x是偶数

    if solver.check() == sat:
        model = solver.model()
        print(f"✓ 找到解: x = {model[x]}, y = {model[y]}, z = {model[z]}")

        # 验证
        x_val = model[x].as_long()
        y_val = model[y].as_long()
        z_val = model[z].as_long()
        assert x_val + y_val + z_val == 15
        assert x_val % 2 == 0
        assert x_val > 0 and y_val > 0 and z_val > 0
        print("✓ 验证通过")
    else:
        print("✗ 无解")


def test_equation():
    """测试: 解方程 x^2 - 5x + 6 = 0"""
    print("\n" + "="*60)
    print("测试2: 方程求解")
    print("="*60)

    x = Real('x')
    solver = Solver()

    solver.add(x * x - 5 * x + 6 == 0)

    if solver.check() == sat:
        model = solver.model()
        x_val = model[x]
        print(f"✓ 找到解: x = {x_val}")
    else:
        print("✗ 无解")


def test_logic_reasoning():
    """测试: 逻辑推理 - 年龄问题"""
    print("\n" + "="*60)
    print("测试3: 逻辑推理问题")
    print("="*60)

    A, B, C = Ints('A B C')
    solver = Solver()

    solver.add(A > B)   # A比B年龄大
    solver.add(C < A)   # C比A小
    solver.add(B == 25) # B是25岁
    solver.add(A > 0, C > 0)  # 年龄为正

    if solver.check() == sat:
        model = solver.model()
        a_val = model[A].as_long()
        c_val = model[C].as_long()
        print(f"✓ 一种可能: A = {a_val}岁, C = {c_val}岁")

        # 验证
        assert a_val > 25
        assert c_val < a_val
        print("✓ 验证通过")
    else:
        print("✗ 无解")


def test_distinct():
    """测试: Distinct 约束 - 身高排序"""
    print("\n" + "="*60)
    print("测试4: Distinct 约束")
    print("="*60)

    A, B, C, D, E = Ints('A B C D E')
    solver = Solver()

    # 身高都不同
    solver.add(Distinct(A, B, C, D, E))

    # 身高都是正数
    solver.add(A > 0, B > 0, C > 0, D > 0, E > 0)

    # 约束条件
    solver.add(A > B)   # A比B高
    solver.add(C < D)   # C比D矮
    solver.add(E > A, E > B, E > C, E > D)  # E最高

    if solver.check() == sat:
        model = solver.model()
        heights = {
            'A': model[A].as_long(),
            'B': model[B].as_long(),
            'C': model[C].as_long(),
            'D': model[D].as_long(),
            'E': model[E].as_long()
        }
        sorted_people = sorted(heights.items(), key=lambda x: x[1], reverse=True)
        print("✓ 一种可能的身高排序(从高到低):")
        for name, height in sorted_people:
            print(f"  {name}: {height}")

        # 验证
        assert heights['A'] > heights['B']
        assert heights['C'] < heights['D']
        assert heights['E'] > max(heights['A'], heights['B'], heights['C'], heights['D'])
        print("✓ 验证通过")
    else:
        print("✗ 无解")


def main():
    print("\n" + "="*60)
    print("LLM + cvc5 基础功能测试")
    print("="*60)
    print("\n说明: 这些测试不依赖 LLM API,只测试 cvc5 求解能力")
    print("如果所有测试通过,说明环境配置正确\n")

    try:
        test_simple_constraint()
        test_equation()
        test_logic_reasoning()
        test_distinct()

        print("\n" + "="*60)
        print("✓ 所有测试通过!")
        print("="*60)
        print("\n下一步:")
        print("1. 配置 LLM API (OpenAI 或 Ollama)")
        print("2. 运行: python nl2smt_solver.py")
        print("3. 输入自然语言问题进行测试")

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
