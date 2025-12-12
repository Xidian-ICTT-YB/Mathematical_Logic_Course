#!/usr/bin/env python3
"""
04. 数据类型 - cvc5 支持的各种数据类型

演示内容：
1. 整数类型 (Int)
2. 实数类型 (Real)
3. 布尔类型 (Bool)
4. 位向量类型 (BitVec)
5. 数组类型 (Array)
6. 字符串类型 (String)
"""

from cvc5.pythonic import *
import time


def example_int_type():
    """整数类型示例"""
    print("=" * 60)
    print("示例 1：整数类型 (Int)")
    print("=" * 60)
    print()

    x, y = Ints('x y')
    solver = Solver()

    # 整数约束
    solver.add(x + y == 10)
    solver.add(x > 0)
    solver.add(x % 2 == 0)  # x 是偶数

    print("约束：")
    print("  - x + y = 10")
    print("  - x > 0")
    print("  - x % 2 = 0 (x 是偶数)")
    print()

    result = solver.check()
    print(f"结果: {result}")

    if result == sat:
        model = solver.model()
        x_val = model[x].as_long()
        y_val = model[y].as_long()
        print(f"解: x = {x_val}, y = {y_val}")
        print(f"验证: {x_val} + {y_val} = {x_val + y_val}")
        print(f"验证: {x_val} % 2 = {x_val % 2}")
    print()


def example_real_type():
    """实数类型示例"""
    print("=" * 60)
    print("示例 2：实数类型 (Real)")
    print("=" * 60)
    print()

    x, y = Reals('x y')
    solver = Solver()

    # 实数约束
    solver.add(x + y == 1)
    solver.add(x > 0)
    solver.add(y > 0)
    solver.add(x < 0.5)

    print("约束：")
    print("  - x + y = 1")
    print("  - x > 0, y > 0")
    print("  - x < 0.5")
    print()

    result = solver.check()
    print(f"结果: {result}")

    if result == sat:
        model = solver.model()
        x_val = model[x]
        y_val = model[y]
        print(f"解: x = {x_val}, y = {y_val}")
        print("注意: cvc5 可能返回分数形式 (如 1/4)")
    print()


def example_bool_type():
    """布尔类型示例"""
    print("=" * 60)
    print("示例 3：布尔类型 (Bool)")
    print("=" * 60)
    print()

    p, q, r = Bools('p q r')
    solver = Solver()

    # 布尔约束
    solver.add(Implies(p, q))
    solver.add(Or(p, r))
    solver.add(Not(And(q, r)))

    print("约束：")
    print("  - p → q (如果 p 则 q)")
    print("  - p ∨ r (p 或 r)")
    print("  - ¬(q ∧ r) (q 和 r 不能同时为真)")
    print()

    result = solver.check()
    print(f"结果: {result}")

    if result == sat:
        model = solver.model()
        print(f"解: p = {model[p]}, q = {model[q]}, r = {model[r]}")
    print()


def example_bitvector_type():
    """位向量类型示例"""
    print("=" * 60)
    print("示例 4：位向量类型 (BitVec)")
    print("=" * 60)
    print()

    # 8 位位向量
    x = BitVec('x', 8)
    y = BitVec('y', 8)

    solver = Solver()

    # 位向量约束
    solver.add(x + y == 200)
    solver.add(x > 100)
    solver.add(x & 0x0F == 0x05)  # 低 4 位 = 0101

    print("约束：")
    print("  - x + y = 200 (8 位无符号加法)")
    print("  - x > 100")
    print("  - x & 0x0F = 0x05 (低 4 位为 0101)")
    print()

    result = solver.check()
    print(f"结果: {result}")

    if result == sat:
        model = solver.model()
        x_val = model[x].as_long()
        y_val = model[y].as_long()
        print(f"解: x = {x_val} (0x{x_val:02X}), y = {y_val} (0x{y_val:02X})")
        print(f"验证: {x_val} + {y_val} = {(x_val + y_val) & 0xFF} (模 256)")
        print(f"验证: {x_val} & 0x0F = {x_val & 0x0F}")
    print()


def example_array_type():
    """数组类型示例"""
    print("=" * 60)
    print("示例 5：数组类型 (Array)")
    print("=" * 60)
    print()

    # 整数到整数的数组
    arr = Array('arr', IntSort(), IntSort())

    solver = Solver()

    # 数组约束
    solver.add(Select(arr, 0) == 10)
    solver.add(Select(arr, 1) == 20)
    solver.add(Select(arr, 2) == 30)
    solver.add(Select(arr, 0) + Select(arr, 1) == Select(arr, 2))

    print("约束：")
    print("  - arr[0] = 10")
    print("  - arr[1] = 20")
    print("  - arr[2] = 30")
    print("  - arr[0] + arr[1] = arr[2]")
    print()

    result = solver.check()
    print(f"结果: {result}")

    if result == sat:
        model = solver.model()
        arr0 = model.eval(Select(arr, 0)).as_long()
        arr1 = model.eval(Select(arr, 1)).as_long()
        arr2 = model.eval(Select(arr, 2)).as_long()
        print(f"解: arr[0] = {arr0}, arr[1] = {arr1}, arr[2] = {arr2}")
        print(f"验证: {arr0} + {arr1} = {arr0 + arr1}")
    print()


def example_string_type():
    """字符串类型示例"""
    print("=" * 60)
    print("示例 6：字符串类型 (String)")
    print("=" * 60)
    print()

    s = String('s')
    solver = Solver()

    # 字符串约束
    solver.add(Length(s) == 5)
    solver.add(PrefixOf("ab", s))
    solver.add(SuffixOf("xy", s))

    print("约束：")
    print("  - Length(s) = 5")
    print("  - s 以 'ab' 开头")
    print("  - s 以 'xy' 结尾")
    print()

    result = solver.check()
    print(f"结果: {result}")

    if result == sat:
        model = solver.model()
        s_val = model[s]
        print(f"解: s = {s_val}")
    else:
        print("无解 (长度为 5 的字符串不能同时以 'ab' 开头和 'xy' 结尾)")
    print()


def main():
    """主函数"""
    print()
    print("=" * 60)
    print("cvc5 数据类型完整演示")
    print("=" * 60)
    print()

    start_time = time.time()

    example_int_type()
    example_real_type()
    example_bool_type()
    example_bitvector_type()
    example_array_type()
    example_string_type()

    elapsed = time.time() - start_time

    print("=" * 60)
    print("总结")
    print("=" * 60)
    print()
    print("cvc5 支持的主要数据类型：")
    print("  1. Int     - 整数 (任意精度)")
    print("  2. Real    - 实数 (分数表示)")
    print("  3. Bool    - 布尔值")
    print("  4. BitVec  - 位向量 (固定宽度)")
    print("  5. Array   - 数组 (索引映射)")
    print("  6. String  - 字符串")
    print()
    print(f"总耗时: {elapsed:.3f} 秒")
    print()


if __name__ == "__main__":
    main()
