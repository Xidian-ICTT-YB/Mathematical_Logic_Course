#!/usr/bin/env python3
"""
07. 位向量理论 - 硬件验证基础

演示内容：
1. 位向量基础操作
2. 位运算验证
3. 加法器正确性验证
4. 溢出检测
5. 硬件电路建模


"""

from cvc5.pythonic import *
import time


def example_basic_bitvector():
    """位向量基础操作"""
    print("=" * 60)
    print("示例 1：位向量基础操作")
    print("=" * 60)
    print()

    x = BitVec('x', 8)
    y = BitVec('y', 8)

    solver = Solver()

    # 基础位运算
    solver.add(x | y == 0xFF)      # 按位或
    solver.add(x & y == 0x0F)      # 按位与
    solver.add(x ^ y == 0xF0)      # 按位异或

    print("约束：")
    print("  - x | y = 0xFF")
    print("  - x & y = 0x0F")
    print("  - x ^ y = 0xF0")
    print()

    result = solver.check()
    print(f"结果: {result}")

    if result == sat:
        model = solver.model()
        x_val = model[x].as_long()
        y_val = model[y].as_long()
        print(f"解: x = 0x{x_val:02X}, y = 0x{y_val:02X}")
        print(f"验证: x | y = 0x{(x_val | y_val):02X}")
        print(f"验证: x & y = 0x{(x_val & y_val):02X}")
        print(f"验证: x ^ y = 0x{(x_val ^ y_val):02X}")
    print()


def example_bit_shift():
    """位移操作"""
    print("=" * 60)
    print("示例 2：位移操作")
    print("=" * 60)
    print()

    x = BitVec('x', 8)

    solver = Solver()

    # 位移约束
    solver.add(x << 2 == 0x40)     # 左移 2 位
    solver.add((x >> 1) & 0x0F == 0x08)  # 右移 1 位后低 4 位

    print("约束：")
    print("  - x << 2 = 0x40")
    print("  - (x >> 1) & 0x0F = 0x08")
    print()

    result = solver.check()
    print(f"结果: {result}")

    if result == sat:
        model = solver.model()
        x_val = model[x].as_long()
        print(f"解: x = 0x{x_val:02X} (二进制: {x_val:08b})")
        print(f"验证: x << 2 = 0x{(x_val << 2) & 0xFF:02X}")
        print(f"验证: (x >> 1) & 0x0F = 0x{((x_val >> 1) & 0x0F):02X}")
    print()


def example_adder_verification():
    """4 位加法器验证"""
    print("=" * 60)
    print("示例 3：4 位加法器正确性验证")
    print("=" * 60)
    print()

    # 输入
    a = BitVec('a', 4)
    b = BitVec('b', 4)

    # 手工实现的加法器（逐位计算）
    c0 = BitVecVal(0, 1)  # 初始进位

    # 提取每一位
    a0, a1, a2, a3 = Extract(0, 0, a), Extract(1, 1, a), Extract(2, 2, a), Extract(3, 3, a)
    b0, b1, b2, b3 = Extract(0, 0, b), Extract(1, 1, b), Extract(2, 2, b), Extract(3, 3, b)

    # 全加器逻辑
    def full_adder_sum(a_bit, b_bit, cin):
        return a_bit ^ b_bit ^ cin

    def full_adder_carry(a_bit, b_bit, cin):
        return (a_bit & b_bit) | ((a_bit ^ b_bit) & cin)

    # 逐位计算
    s0 = full_adder_sum(a0, b0, c0)
    c1 = full_adder_carry(a0, b0, c0)

    s1 = full_adder_sum(a1, b1, c1)
    c2 = full_adder_carry(a1, b1, c1)

    s2 = full_adder_sum(a2, b2, c2)
    c3 = full_adder_carry(a2, b2, c2)

    s3 = full_adder_sum(a3, b3, c3)

    # 拼接结果
    manual_sum = Concat(s3, Concat(s2, Concat(s1, s0)))

    # 验证：寻找手工实现 ≠ 内置加法器的反例
    solver = Solver()
    solver.add(manual_sum != Extract(3, 0, a + b))

    print("验证策略：寻找反例 (手工加法器 ≠ 内置加法器)")
    print()

    start = time.time()
    result = solver.check()
    elapsed = time.time() - start

    print(f"结果: {result}")
    print(f"耗时: {elapsed:.6f} 秒")
    print()

    if result == unsat:
        print("验证通过！")
        print("手工加法器在所有 2^8 = 256 种输入下")
        print("都与内置加法器产生相同结果")
        print()
        print("说明：")
        print("  - 逐位全加器实现正确")
        print("  - 进位传播逻辑无误")
    else:
        print("验证失败！找到反例")
        model = solver.model()
        print(f"a = {model[a]}, b = {model[b]}")
    print()


def example_overflow_detection():
    """溢出检测"""
    print("=" * 60)
    print("示例 4：溢出检测")
    print("=" * 60)
    print()

    x = BitVec('x', 4)  # 4 位有符号数 (-8 到 7)
    y = BitVec('y', 4)

    solver = Solver()

    # 寻找导致溢出的输入
    # 有符号加法：如果 x, y 同号，但 x+y 异号，则溢出
    sum_result = x + y

    # 检测正溢出：两个正数相加得到负数
    positive_x = x >= 0
    positive_y = y >= 0
    negative_sum = sum_result < 0

    solver.add(positive_x)
    solver.add(positive_y)
    solver.add(negative_sum)

    print("约束：")
    print("  - x >= 0 (正数)")
    print("  - y >= 0 (正数)")
    print("  - x + y < 0 (和为负数，溢出！)")
    print()

    result = solver.check()
    print(f"结果: {result}")

    if result == sat:
        model = solver.model()
        x_val = model[x].as_signed_long()
        y_val = model[y].as_signed_long()
        sum_val = model.eval(sum_result).as_signed_long()

        print(f"找到溢出案例:")
        print(f"  x = {x_val}")
        print(f"  y = {y_val}")
        print(f"  x + y = {sum_val} (4 位有符号)")
        print(f"  真实和 = {x_val + y_val} (超出 4 位范围)")
    print()


def example_circuit_equivalence():
    """电路等价性验证"""
    print("=" * 60)
    print("示例 5：电路等价性验证")
    print("=" * 60)
    print()

    x = BitVec('x', 4)

    # 电路 1: (x << 1) | (x >> 3)
    circuit1 = (x << 1) | LShR(x, 3)  # LShR: 逻辑右移

    # 电路 2: 手工优化版本（假设）
    # 这里我们故意制造一个不等价的电路
    circuit2 = (x << 1) | (x >> 2)

    solver = Solver()
    solver.add(circuit1 != circuit2)

    print("电路 1: (x << 1) | (x >> 3)")
    print("电路 2: (x << 1) | (x >> 2)")
    print()
    print("验证：寻找两个电路输出不同的输入")
    print()

    result = solver.check()
    print(f"结果: {result}")

    if result == sat:
        model = solver.model()
        x_val = model[x].as_long()
        c1_val = model.eval(circuit1).as_long()
        c2_val = model.eval(circuit2).as_long()

        print(f"找到不等价案例:")
        print(f"  输入 x = 0x{x_val:X}")
        print(f"  电路 1 输出 = 0x{c1_val:X}")
        print(f"  电路 2 输出 = 0x{c2_val:X}")
        print()
        print("结论：两个电路不等价")
    else:
        print("两个电路等价（未找到反例）")
    print()


def main():
    """主函数"""
    print()
    print("=" * 60)
    print("位向量理论：硬件验证应用")
    print("=" * 60)
    print()

    start_time = time.time()

    example_basic_bitvector()
    example_bit_shift()
    example_adder_verification()
    example_overflow_detection()
    example_circuit_equivalence()

    elapsed = time.time() - start_time

    print(f"总耗时: {elapsed:.3f} 秒")
    print()


if __name__ == "__main__":
    main()
