import cvc5
from cvc5 import Kind
import time

# 初始化 solver
solver = cvc5.Solver()
solver.setOption("produce-models", "true")
solver.setOption("produce-unsat-cores", "true")
solver.setLogic("QF_LIA")  # 无量词线性整数算术足够用于此问题

intSort = solver.getIntegerSort()

# 定义一个 9x9 的矩阵变量 grid[row][col]
grid = [[solver.mkConst(intSort, f"x_{r}_{c}") for c in range(9)] for r in range(9)]

# 初始棋盘

initial_board = [
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

# 基础域约束：每个变量在 1 到 9 之间
for r in range(9):
    for c in range(9):
        # 1 <= x_rc <= 9
        solver.assertFormula(solver.mkTerm(Kind.GEQ, grid[r][c], solver.mkInteger(1)))
        solver.assertFormula(solver.mkTerm(Kind.LEQ, grid[r][c], solver.mkInteger(9)))

# 已知格子约束
for r in range(9):
    for c in range(9):
        val = initial_board[r][c]
        if val != 0:
            # x_rc = val
            solver.assertFormula(solver.mkTerm(Kind.EQUAL, grid[r][c], solver.mkInteger(val)))

# 辅助函数：创建 all-different 约束
def allDifferent(vars):
    # allDifferent 通常需要对每对变量添加不相等约束
    # 这里手动实现一组 pairwise inequality 约束
    for i in range(len(vars)):
        for j in range(i+1, len(vars)):
            solver.assertFormula(solver.mkTerm(Kind.DISTINCT, vars[i], vars[j]))

# 行约束
for r in range(9):
    allDifferent(grid[r])

# 列约束
for c in range(9):
    col_vars = [grid[r][c] for r in range(9)]
    allDifferent(col_vars)

# 3x3 box 约束
for box_r in range(3):
    for box_c in range(3):
        box_vars = []
        for rr in range(3):
            for cc in range(3):
                box_vars.append(grid[3*box_r+rr][3*box_c+cc])
        allDifferent(box_vars)

start_time = time.time()
result = solver.checkSat()
end_time = time.time()

print("结果:", result)

if result.isSat():
    print("求解出的数独解：")
    solution = [[0]*9 for _ in range(9)]
    for r in range(9):
        for c in range(9):
            val = solver.getValue(grid[r][c]).getIntegerValue()
            solution[r][c] = val

    for row in solution:
        print(row)
else:
    print("无解或未知。")
    unsatCore = solver.getUnsatCore()
    print("unsat core size:", len(unsatCore))
    print("unsat core:", unsatCore)

elapsed_time = end_time - start_time
print(f"运行时间: {elapsed_time:.6f} 秒")

