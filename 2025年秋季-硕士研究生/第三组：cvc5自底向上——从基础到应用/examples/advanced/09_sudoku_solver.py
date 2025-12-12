#!/usr/bin/env python3
"""
cvc5 高级应用：数独求解器（优化版）
=========================================

这个示例展示如何使用 cvc5 SMT 求解器来求解数独问题。


"""

from cvc5.pythonic import *
import time


def print_sudoku(grid, title="数独谜题"):
    """
    漂亮地打印数独网格

    Args:
        grid: 9x9 的数独网格，0 表示空格
        title: 标题文字
    """
    print()
    print("=" * 37)
    print(f"  {title}")
    print("=" * 37)
    print()

    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("  " + "-" * 33)

        row_str = "  "
        for j in range(9):
            if j % 3 == 0 and j != 0:
                row_str += "| "

            cell = grid[i][j]
            if cell == 0:
                row_str += "· "
            else:
                row_str += str(cell) + " "

        print(row_str)

    print()


def solve_sudoku(initial_board, verbose=True):
    """
    使用 cvc5 求解数独

    Args:
        initial_board: 9x9 列表，0 表示空格
        verbose: 是否打印详细信息

    Returns:
        solution: 9x9 的解（如果存在）
        elapsed: 求解时间
    """

    if verbose:
        print_sudoku(initial_board, "初始谜题")

    # 创建求解器
    solver = Solver()

    # 步骤 1：创建 9x9 的整数变量矩阵
    grid = [[Int(f'cell_{i}_{j}') for j in range(9)] for i in range(9)]

    # 步骤 2：域约束 - 每个格子的值在 1-9 之间
    for i in range(9):
        for j in range(9):
            solver.add(grid[i][j] >= 1, grid[i][j] <= 9)

    # 步骤 3：已知格子约束
    known_cells = 0
    for i in range(9):
        for j in range(9):
            val = initial_board[i][j]
            if val != 0:
                solver.add(grid[i][j] == val)
                known_cells += 1

    # 步骤 4：行约束 - 每行的 9 个数字互不相同
    for i in range(9):
        row = [grid[i][j] for j in range(9)]
        solver.add(Distinct(*row))

    # 步骤 5：列约束 - 每列的 9 个数字互不相同
    for j in range(9):
        col = [grid[i][j] for i in range(9)]
        solver.add(Distinct(*col))

    # 步骤 6：3x3 宫约束 - 每个 3x3 宫的 9 个数字互不相同
    for box_row in range(3):
        for box_col in range(3):
            box_cells = []
            for i in range(3):
                for j in range(3):
                    row = 3 * box_row + i
                    col = 3 * box_col + j
                    box_cells.append(grid[row][col])
            solver.add(Distinct(*box_cells))

    if verbose:
        print(f"📌 已知数字：{known_cells} 个")
        print(f"📌 总约束数：{162 + known_cells + 27}")
        print()

    # 步骤 7：调用求解器
    if verbose:
        print("🚀 开始求解...")

    start_time = time.time()
    result = solver.check()
    elapsed = time.time() - start_time

    if verbose:
        print(f"⏱️  求解时间：{elapsed:.6f} 秒")
        print()

    # 步骤 8：提取解
    if result == sat:
        model = solver.model()
        solution = [[0] * 9 for _ in range(9)]

        for i in range(9):
            for j in range(9):
                solution[i][j] = model[grid[i][j]].as_long()

        if verbose:
            print("✅ 求解成功！")
            print_sudoku(solution, "解")

        return solution, elapsed
    else:
        if verbose:
            print("❌ 无解（可能谜题有误）")
        return None, elapsed


def verify_solution(solution):
    """
    验证数独解是否正确

    Returns:
        bool: 是否正确
    """
    if solution is None:
        return False

    # 检查行
    for row in solution:
        if len(set(row)) != 9 or min(row) < 1 or max(row) > 9:
            return False

    # 检查列
    for j in range(9):
        col = [solution[i][j] for i in range(9)]
        if len(set(col)) != 9:
            return False

    # 检查 3x3 宫
    for box_row in range(3):
        for box_col in range(3):
            box = []
            for i in range(3):
                for j in range(3):
                    box.append(solution[3*box_row + i][3*box_col + j])
            if len(set(box)) != 9:
                return False

    return True


def main():
    """主函数 - 演示数独求解"""

    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "cvc5 数独求解器演示" + " " * 19 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    # 示例：中等难度的数独
    puzzle = [
        [5,3,0, 0,7,0, 0,0,0],
        [6,0,0, 1,9,5, 0,0,0],
        [0,9,8, 0,0,0, 0,6,0],

        [8,0,0, 0,6,0, 0,0,3],
        [4,0,0, 8,0,3, 0,0,1],
        [7,0,0, 0,2,0, 0,0,6],

        [0,6,0, 0,0,0, 2,8,0],
        [0,0,0, 4,1,9, 0,0,5],
        [0,0,0, 0,8,0, 0,7,9]
    ]

    # 求解数独
    solution, elapsed = solve_sudoku(puzzle, verbose=True)

    # 验证解
    if verify_solution(solution):
        print("✅ 验证通过：解是正确的！")
    else:
        print("❌ 验证失败：解有问题")

    print()


if __name__ == "__main__":
    main()
