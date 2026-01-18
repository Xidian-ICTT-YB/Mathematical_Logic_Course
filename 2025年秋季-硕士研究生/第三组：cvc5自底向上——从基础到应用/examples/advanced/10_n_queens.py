#!/usr/bin/env python3
"""
cvc5 高级应用：N 皇后问题
============================

经典的 N 皇后问题：在 N×N 的棋盘上放置 N 个皇后，
使得任意两个皇后都不能互相攻击。

约束：
- 每行恰好一个皇后
- 每列恰好一个皇后
- 每条对角线最多一个皇后

"""

from cvc5.pythonic import *


def print_board(solution, n):
    """
    打印棋盘

    Args:
        solution: 列表，solution[i] 表示第 i 行皇后所在的列
        n: 棋盘大小
    """
    print()
    print("  " + "─" * (n * 2 + 1))
    for i in range(n):
        row = "  │"
        for j in range(n):
            if solution[i] == j:
                row += "♛ "
            else:
                row += "· "
        row += "│"
        print(row)
    print("  " + "─" * (n * 2 + 1))
    print()


def solve_n_queens(n, verbose=True):
    """
    求解 N 皇后问题

    Args:
        n: 棋盘大小
        verbose: 是否打印详细信息

    Returns:
        solution: 解（如果存在）
        elapsed: 求解时间
    """
    import time

    if verbose:
        print(f"\n{'='*60}")
        print(f"求解 {n}×{n} 棋盘的 {n} 皇后问题")
        print(f"{'='*60}\n")

    # 创建求解器
    solver = Solver()

    # 变量：queens[i] 表示第 i 行的皇后在第几列
    # 范围：0 到 n-1
    queens = [Int(f'q_{i}') for i in range(n)]

    if verbose:
        print("📌 建模策略：")
        print(f"   使用 {n} 个整数变量 q[0], q[1], ..., q[{n-1}]")
        print(f"   q[i] = j 表示第 i 行的皇后在第 j 列")
        print()

    # 约束 1：域约束 - 每个皇后的列号在 0 到 n-1 之间
    for i in range(n):
        solver.add(queens[i] >= 0)
        solver.add(queens[i] < n)

    if verbose:
        print(f"📌 约束 1：域约束（{n*2} 个）")
        print(f"   每个皇后的列号在 [0, {n-1}] 范围内")
        print()

    # 约束 2：列约束 - 不同行的皇后不能在同一列
    # 等价于：所有 queens[i] 的值互不相同
    solver.add(Distinct(*queens))

    if verbose:
        print("📌 约束 2：列约束（1 个 Distinct）")
        print("   所有皇后的列号互不相同")
        print()

    # 约束 3：对角线约束
    # 两个皇后 (i, queens[i]) 和 (j, queens[j]) 在同一对角线上
    # 当且仅当 |i - j| = |queens[i] - queens[j]|

    diagonal_constraints = 0
    for i in range(n):
        for j in range(i + 1, n):
            # 主对角线：row_diff != col_diff
            # 即：i - j != queens[i] - queens[j]
            # 且：i - j != queens[j] - queens[i]

            row_diff = i - j
            # 因为 i < j，所以 row_diff < 0

            # 约束：queens[i] - queens[j] != row_diff
            solver.add(queens[i] - queens[j] != row_diff)

            # 约束：queens[j] - queens[i] != row_diff (即 queens[i] - queens[j] != -row_diff)
            solver.add(queens[i] - queens[j] != -row_diff)

            diagonal_constraints += 2

    if verbose:
        print(f"📌 约束 3：对角线约束（{diagonal_constraints} 个）")
        print("   任意两个皇后不在同一对角线上")
        print()
        print(f"🔢 总约束数：{n*2 + 1 + diagonal_constraints}")
        print()

    # 求解
    if verbose:
        print("🚀 开始求解...")

    start_time = time.time()
    result = solver.check()
    elapsed = time.time() - start_time

    if verbose:
        print(f"⏱️  求解时间：{elapsed:.6f} 秒")
        print()

    if result == sat:
        model = solver.model()
        solution = [model[queens[i]].as_long() for i in range(n)]

        if verbose:
            print("✅ 找到解！")
            print_board(solution, n)

            # 验证解
            print("🔬 验证解的正确性：")

            # 检查列
            if len(set(solution)) == n:
                print("   ✓ 列约束：所有皇后在不同列")
            else:
                print("   ✗ 列约束：有皇后在同一列")

            # 检查对角线
            diagonal_ok = True
            for i in range(n):
                for j in range(i + 1, n):
                    if abs(i - j) == abs(solution[i] - solution[j]):
                        diagonal_ok = False
                        break
                if not diagonal_ok:
                    break

            if diagonal_ok:
                print("   ✓ 对角线约束：无皇后在同一对角线")
            else:
                print("   ✗ 对角线约束：有皇后在同一对角线")

        return solution, elapsed
    else:
        if verbose:
            print("❌ 无解")
        return None, elapsed


def find_all_solutions(n, max_solutions=10):
    """
    找到 N 皇后问题的多个解

    Args:
        n: 棋盘大小
        max_solutions: 最多找多少个解
    """
    print(f"\n{'='*60}")
    print(f"寻找 {n}×{n} 棋盘的多个解（最多 {max_solutions} 个）")
    print(f"{'='*60}\n")

    solver = Solver()
    queens = [Int(f'q_{i}') for i in range(n)]

    # 添加基本约束
    for i in range(n):
        solver.add(queens[i] >= 0, queens[i] < n)

    solver.add(Distinct(*queens))

    for i in range(n):
        for j in range(i + 1, n):
            solver.add(queens[i] - queens[j] != i - j)
            solver.add(queens[i] - queens[j] != j - i)

    solutions = []

    for count in range(1, max_solutions + 1):
        result = solver.check()

        if result == sat:
            model = solver.model()
            solution = [model[queens[i]].as_long() for i in range(n)]
            solutions.append(solution)

            print(f"解 {count}：{solution}")

            # 排除这个解
            solver.add(Or([queens[i] != solution[i] for i in range(n)]))
        else:
            print(f"\n总共找到 {len(solutions)} 个不同的解")
            break

    return solutions


def performance_test():
    """
    性能测试：测试不同规模的 N 皇后问题
    """
    print(f"\n{'='*60}")
    print("性能测试：不同规模的 N 皇后问题")
    print(f"{'='*60}\n")

    test_sizes = [4, 6, 8, 10, 12]

    print(f"{'N':>4} | {'求解时间':>12} | {'结果':>8}")
    print("-" * 32)

    for n in test_sizes:
        _, elapsed = solve_n_queens(n, verbose=False)
        print(f"{n:>4} | {elapsed:>10.6f}s | {'成功':>8}")

    print()


def main():
    """主函数"""

    # 示例 1：求解 8 皇后问题
    solve_n_queens(8)

    # 示例 2：寻找多个解（4 皇后）
    find_all_solutions(4, max_solutions=3)

    # 示例 3：性能测试
    performance_test()



if __name__ == "__main__":
    main()
