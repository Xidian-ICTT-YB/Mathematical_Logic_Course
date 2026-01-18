#!/usr/bin/env python3
"""
cvc5 进阶示例：数组理论
============================

这个示例展示如何使用 cvc5 的数组理论（Array Theory）。

数组理论的核心概念：
- select(array, index)：读取数组元素
- store(array, index, value)：写入数组元素


"""

from cvc5.pythonic import *


def basic_array_operations():
    """
    基础数组操作示例

    演示：select 和 store 的基本用法
    """

    print("=" * 60)
    print("示例 1：基础数组操作")
    print("=" * 60)
    print()

    # 创建一个整数到整数的数组
    # Array(name, index_type, value_type)
    arr = Array('arr', IntSort(), IntSort())

    # 创建索引变量
    i, j = Ints('i j')

    solver = Solver()

    # 约束 1：arr[0] = 10
    solver.add(Select(arr, 0) == 10)

    # 约束 2：arr[1] = 20
    solver.add(Select(arr, 1) == 20)

    # 约束 3：arr[2] = arr[0] + arr[1]
    solver.add(Select(arr, 2) == Select(arr, 0) + Select(arr, 1))

    print("📌 约束：")
    print("   - arr[0] = 10")
    print("   - arr[1] = 20")
    print("   - arr[2] = arr[0] + arr[1]")
    print()

    print("🔍 开始求解...")
    result = solver.check()

    if result == sat:
        model = solver.model()
        print("✅ 可满足！")
        print()
        print("📊 结果：")
        print(f"   arr[0] = {model.eval(Select(arr, 0))}")
        print(f"   arr[1] = {model.eval(Select(arr, 1))}")
        print(f"   arr[2] = {model.eval(Select(arr, 2))}")

    print()


def array_store_operation():
    """
    数组 store 操作示例

    store(array, index, value) 返回一个新数组
    """

    print("=" * 60)
    print("示例 2：数组 Store 操作")
    print("=" * 60)
    print()

    arr = Array('arr', IntSort(), IntSort())

    solver = Solver()

    # 初始状态：arr[0] = 5
    solver.add(Select(arr, 0) == 5)

    # 创建新数组：arr2 = store(arr, 0, 10)
    # 意思是将 arr[0] 修改为 10
    arr2 = Store(arr, 0, 10)

    # 验证：arr2[0] = 10
    solver.add(Select(arr2, 0) == 10)

    # 验证：其他索引保持不变
    # arr2[1] = arr[1]
    solver.add(Select(arr2, 1) == Select(arr, 1))

    print("📌 操作：")
    print("   1. 初始：arr[0] = 5")
    print("   2. 修改：arr2 = store(arr, 0, 10)")
    print("   3. 验证：arr2[0] = 10")
    print("   4. 验证：arr2[1] = arr[1]（其他元素不变）")
    print()

    print("🔍 开始求解...")
    result = solver.check()

    if result == sat:
        model = solver.model()
        print("✅ 可满足！")
        print()
        print("📊 验证 store 的性质：")
        print(f"   arr[0] = {model.eval(Select(arr, 0))}")
        print(f"   arr2[0] = {model.eval(Select(arr2, 0))} ← 已修改")
        print()
        print("💡 Store 操作是函数式的（创建新数组，不修改原数组）")

    print()


def array_property_verification():
    """
    验证数组性质

    性质：如果 i != j，则 store(arr, i, v)[j] = arr[j]
    """

    print("=" * 60)
    print("示例 3：验证数组理论性质")
    print("=" * 60)
    print()

    arr = Array('arr', IntSort(), IntSort())
    i, j, v = Ints('i j v')

    solver = Solver()

    # 假设：i != j
    solver.add(i != j)

    # arr2 = store(arr, i, v)
    arr2 = Store(arr, i, v)

    # 性质：arr2[j] 应该等于 arr[j]（因为 i != j）
    # 我们检查性质的否定，看是否能找到反例
    solver.add(Select(arr2, j) != Select(arr, j))

    print("📌 要验证的性质：")
    print("   如果 i ≠ j，则 store(arr, i, v)[j] = arr[j]")
    print()
    print("📌 验证方法：")
    print("   寻找性质的反例（如果 UNSAT，则性质成立）")
    print()

    print("🔍 开始验证...")
    result = solver.check()

    if result == unsat:
        print("✅ 性质成立！")
        print("   找不到反例，说明数组理论的公理是正确的")
    else:
        print("❌ 找到反例（不应该发生）")

    print()


def array_initialization():
    """
    数组初始化模式

    演示如何初始化一个数组的多个元素
    """

    print("=" * 60)
    print("示例 4：数组初始化")
    print("=" * 60)
    print()

    arr = Array('arr', IntSort(), IntSort())

    solver = Solver()

    # 初始化数组的前 5 个元素
    initial_values = [10, 20, 30, 40, 50]

    print("📌 初始化数组：")
    for i, val in enumerate(initial_values):
        solver.add(Select(arr, i) == val)
        print(f"   arr[{i}] = {val}")

    print()

    # 添加一个约束：arr[2] + arr[3] = arr[4]
    solver.add(Select(arr, 2) + Select(arr, 3) == Select(arr, 4))

    print("📌 额外约束：")
    print("   arr[2] + arr[3] = arr[4]")
    print()

    print("🔍 检查约束是否一致...")
    result = solver.check()

    if result == sat:
        model = solver.model()
        print("✅ 约束一致！")
        print()
        print("🔬 验证：")
        val2 = model.eval(Select(arr, 2)).as_long()
        val3 = model.eval(Select(arr, 3)).as_long()
        val4 = model.eval(Select(arr, 4)).as_long()
        print(f"   arr[2] + arr[3] = {val2} + {val3} = {val2 + val3}")
        print(f"   arr[4] = {val4}")
        print(f"   是否相等：{val2 + val3 == val4} ✓")
    else:
        print("❌ 约束矛盾！")

    print()


def array_sorting_verification():
    """
    验证数组排序性质

    检查一个 3 元素数组是否已排序
    """

    print("=" * 60)
    print("示例 5：验证数组排序")
    print("=" * 60)
    print()

    arr = Array('arr', IntSort(), IntSort())

    solver = Solver()

    # 数组有 3 个元素
    # 假设：arr[0] <= arr[1] <= arr[2]（已排序）
    solver.add(Select(arr, 0) <= Select(arr, 1))
    solver.add(Select(arr, 1) <= Select(arr, 2))

    # 添加一些值约束
    solver.add(Select(arr, 0) >= 1)
    solver.add(Select(arr, 2) <= 10)

    print("📌 约束：")
    print("   - arr[0] <= arr[1] <= arr[2]（已排序）")
    print("   - arr[0] >= 1")
    print("   - arr[2] <= 10")
    print()

    print("🔍 查找满足条件的排序数组...")
    result = solver.check()

    if result == sat:
        model = solver.model()
        print("✅ 找到一个已排序的数组：")

        val0 = model.eval(Select(arr, 0)).as_long()
        val1 = model.eval(Select(arr, 1)).as_long()
        val2 = model.eval(Select(arr, 2)).as_long()

        print(f"   [{val0}, {val1}, {val2}]")
        print()
        print("🔬 验证排序：")
        print(f"   {val0} <= {val1}：{val0 <= val1} ✓")
        print(f"   {val1} <= {val2}：{val1 <= val2} ✓")

    print()


def main():
    """主函数"""

    # 示例 1：基础数组操作
    basic_array_operations()

    # 示例 2：Store 操作
    array_store_operation()

    # 示例 3：性质验证
    array_property_verification()

    # 示例 4：数组初始化
    array_initialization()

    # 示例 5：排序验证
    array_sorting_verification()

if __name__ == "__main__":
    main()
