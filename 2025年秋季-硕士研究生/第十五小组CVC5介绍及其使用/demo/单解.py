# 拉丁方阵
import cvc5
from cvc5 import Kind
import time

solver = cvc5.Solver()
solver.setOption("produce-models", "true")
solver.setLogic("QF_LIA")

intSort = solver.getIntegerSort()

# 定义 4x4 矩阵
N = 4
grid = [[solver.mkConst(intSort, f"x_{r}_{c}") for c in range(N)] for r in range(N)]

# 预设几个数字 (题目)
# 0 表示空
puzzle = [
    [1, 0, 0, 0],
    [0, 2, 0, 0],
    [0, 0, 3, 0],
    [4, 0, 0, 0]
]

# 1. 范围约束 1-4
one = solver.mkInteger(1)
four = solver.mkInteger(4)
for r in range(N):
    for c in range(N):
        solver.assertFormula(solver.mkTerm(Kind.GEQ, grid[r][c], one))
        solver.assertFormula(solver.mkTerm(Kind.LEQ, grid[r][c], four))

        # 填入预设值
        if puzzle[r][c] != 0:
            val = solver.mkInteger(puzzle[r][c])
            solver.assertFormula(solver.mkTerm(Kind.EQUAL, grid[r][c], val))


# 辅助函数: 互不相同
def allDifferent(vars):
    for i in range(len(vars)):
        for j in range(i + 1, len(vars)):
            solver.assertFormula(solver.mkTerm(Kind.DISTINCT, vars[i], vars[j]))


# 2. 行约束
for r in range(N):
    allDifferent(grid[r])

# 3. 列约束
for c in range(N):
    col_vars = [grid[r][c] for r in range(N)]
    allDifferent(col_vars)

print("求解 4x4 拉丁方阵...")
result = solver.checkSat()
print("结果:", result)

if result.isSat():
    for r in range(N):
        row_vals = []
        for c in range(N):
            row_vals.append(solver.getValue(grid[r][c]).getIntegerValue())
        print(row_vals)