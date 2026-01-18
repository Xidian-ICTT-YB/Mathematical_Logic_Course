#!/usr/bin/env python3
"""
08. UNSAT Core 分析 - 冲突诊断

演示内容：
1. UNSAT Core 概念
2. 冲突定位
3. 排班系统冲突诊断
4. 最小不可满足子集

"""

from cvc5.pythonic import *
import time


def example_simple_unsat():
    """简单的 UNSAT 示例"""
    print("=" * 60)
    print("示例 1：简单的 UNSAT 情况")
    print("=" * 60)
    print()

    x = Int('x')
    solver = Solver()

    # 矛盾约束
    solver.add(x > 10)
    solver.add(x < 5)

    print("约束：")
    print("  C1: x > 10")
    print("  C2: x < 5")
    print()

    result = solver.check()
    print(f"结果: {result}")
    print()

    if result == unsat:
        print("分析：")
        print("  这两个约束是矛盾的")
        print("  不存在同时大于 10 且小于 5 的整数")
        print()
        print("UNSAT Core: {C1, C2}")
    print()


def example_scheduling_conflict():
    """排班系统冲突诊断"""
    print("=" * 60)
    print("示例 2：排班系统冲突诊断")
    print("=" * 60)
    print()

    # 3 个员工：Alice, Bob, Charlie
    alice, bob, charlie = Ints('alice bob charlie')

    # 班次：1=早班, 2=中班, 3=晚班, 4=夜班
    MORNING, AFTERNOON, EVENING, NIGHT = 1, 2, 3, 4

    print("设定：")
    print("  员工：Alice, Bob, Charlie")
    print("  班次：1=早班, 2=中班, 3=晚班, 4=夜班")
    print()

    # 逐步添加约束，观察何时 UNSAT
    print("逐步添加约束：")
    print()

    # 阶段 1：基础约束
    print("[阶段 1] 基础域约束")
    solver1 = Solver()
    solver1.add(alice >= 1, alice <= 4)
    solver1.add(bob >= 1, bob <= 4)
    solver1.add(charlie >= 1, charlie <= 4)

    result1 = solver1.check()
    print(f"  结果: {result1}")
    if result1 == sat:
        model = solver1.model()
        print(f"  示例解: Alice={model[alice]}, Bob={model[bob]}, Charlie={model[charlie]}")
    print()

    # 阶段 2：互斥约束
    print("[阶段 2] + 互斥约束（不同员工不同班次）")
    solver2 = Solver()
    solver2.add(alice >= 1, alice <= 4)
    solver2.add(bob >= 1, bob <= 4)
    solver2.add(charlie >= 1, charlie <= 4)
    solver2.add(alice != bob)
    solver2.add(bob != charlie)
    solver2.add(alice != charlie)

    result2 = solver2.check()
    print(f"  结果: {result2}")
    if result2 == sat:
        model = solver2.model()
        print(f"  示例解: Alice={model[alice]}, Bob={model[bob]}, Charlie={model[charlie]}")
    print()

    # 阶段 3：Alice 的要求
    print("[阶段 3] + Alice 只要早班或中班 (alice <= 2)")
    solver3 = Solver()
    solver3.add(alice >= 1, alice <= 4)
    solver3.add(bob >= 1, bob <= 4)
    solver3.add(charlie >= 1, charlie <= 4)
    solver3.add(alice != bob, bob != charlie, alice != charlie)
    solver3.add(alice <= 2)

    result3 = solver3.check()
    print(f"  结果: {result3}")
    if result3 == sat:
        model = solver3.model()
        print(f"  示例解: Alice={model[alice]}, Bob={model[bob]}, Charlie={model[charlie]}")
    print()

    # 阶段 4：Bob 的要求
    print("[阶段 4] + Bob 也只要早班或中班 (bob <= 2)")
    solver4 = Solver()
    solver4.add(alice >= 1, alice <= 4)
    solver4.add(bob >= 1, bob <= 4)
    solver4.add(charlie >= 1, charlie <= 4)
    solver4.add(alice != bob, bob != charlie, alice != charlie)
    solver4.add(alice <= 2)
    solver4.add(bob <= 2)

    result4 = solver4.check()
    print(f"  结果: {result4}")
    if result4 == sat:
        model = solver4.model()
        print(f"  示例解: Alice={model[alice]}, Bob={model[bob]}, Charlie={model[charlie]}")
    print()

    # 阶段 5：Charlie 的要求 → UNSAT!
    print("[阶段 5] + Charlie 也只要早班或中班 (charlie <= 2)")
    solver5 = Solver()
    solver5.add(alice >= 1, alice <= 4)
    solver5.add(bob >= 1, bob <= 4)
    solver5.add(charlie >= 1, charlie <= 4)
    solver5.add(alice != bob, bob != charlie, alice != charlie)
    solver5.add(alice <= 2)
    solver5.add(bob <= 2)
    solver5.add(charlie <= 2)

    result5 = solver5.check()
    print(f"  结果: {result5}")
    print()

    if result5 == unsat:
        print("冲突分析：")
        print()
        print("  导致矛盾的约束子集：")
        print("  - alice != bob != charlie (互斥)")
        print("  - alice <= 2")
        print("  - bob <= 2")
        print("  - charlie <= 2")
        print()
        print("  根本原因：")
        print("  ┌────────────────────────────────────────┐")
        print("  │ 3 个人都想要早班(1)或中班(2)           │")
        print("  │ 但必须分配到不同班次                   │")
        print("  │                                        │")
        print("  │ 只有 2 个可选班次，无法分配 3 个人     │")
        print("  │ → 鸽巢原理：3 只鸽子，2 个巢 = 矛盾！ │")
        print("  └────────────────────────────────────────┘")
        print()
        print("  解决方案：")
        print("  • 方案 1: 放宽某人的班次限制")
        print("  • 方案 2: 允许某两人同班")
        print("  • 方案 3: 增加班次容量")
    print()


def example_overconstrained_system():
    """过度约束系统"""
    print("=" * 60)
    print("示例 3：过度约束系统")
    print("=" * 60)
    print()

    x, y, z = Ints('x y z')
    solver = Solver()

    # 添加多个约束
    constraints = [
        x + y + z == 10,
        x > 5,
        y > 5,
        z > 5,
        x < 10,
        y < 10,
        z < 10
    ]

    print("约束列表：")
    for i, c in enumerate(constraints, 1):
        print(f"  C{i}: {c}")
    print()

    for c in constraints:
        solver.add(c)

    result = solver.check()
    print(f"结果: {result}")
    print()

    if result == unsat:
        print("冲突分析：")
        print()
        print("  核心矛盾：")
        print("  C1: x + y + z = 10")
        print("  C2: x > 5")
        print("  C3: y > 5")
        print("  C4: z > 5")
        print()
        print("  推理：")
        print("  如果 x > 5, y > 5, z > 5")
        print("  则 x + y + z > 15")
        print("  但 C1 要求 x + y + z = 10")
        print("  矛盾！")
        print()
        print("  最小 UNSAT Core: {C1, C2, C3, C4}")
        print("  (C5, C6, C7 不是必需的)")
    print()


def example_incremental_diagnosis():
    """增量式冲突诊断"""
    print("=" * 60)
    print("示例 4：增量式冲突诊断")
    print("=" * 60)
    print()

    x = Int('x')
    solver = Solver()

    constraints = [
        ("C1", x > 0),
        ("C2", x < 100),
        ("C3", x % 2 == 0),
        ("C4", x % 3 == 0),
        ("C5", x % 5 == 0),
        ("C6", x > 50),
        ("C7", x < 60),
        ("C8", x != 60),
    ]

    print("逐步添加约束，直到 UNSAT：")
    print()

    for name, constraint in constraints:
        solver.push()
        solver.add(constraint)

        result = solver.check()

        if result == sat:
            model = solver.model()
            x_val = model[x].as_long()
            print(f"  + {name}: {constraint}")
            print(f"    结果: SAT, 示例解: x = {x_val}")
        else:
            print(f"  + {name}: {constraint}")
            print(f"    结果: UNSAT")
            print()
            print(f"  冲突发现！{name} 导致系统不可满足")
            solver.pop()
            break

        solver.pop()
        solver.add(constraint)

    print()


def main():
    """主函数"""
    print()
    print("=" * 60)
    print("UNSAT Core 分析：冲突诊断")
    print("=" * 60)
    print()

    start_time = time.time()

    example_simple_unsat()
    example_scheduling_conflict()
    example_overconstrained_system()
    example_incremental_diagnosis()

    elapsed = time.time() - start_time

    print(f"总耗时: {elapsed:.3f} 秒")
    print()


if __name__ == "__main__":
    main()
