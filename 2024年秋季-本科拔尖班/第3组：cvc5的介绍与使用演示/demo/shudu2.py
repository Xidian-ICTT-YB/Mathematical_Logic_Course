import cvc5
from cvc5 import Kind
import time

solver = cvc5.Solver()
solver.setOption("produce-models", "true")
solver.setLogic("QF_LIA")

intSort = solver.getIntegerSort()

# 定义 9x9 网格变量
grid = [[solver.mkConst(intSort, f"x_{r}_{c}") for c in range(9)] for r in range(9)]

initial_board = [
    [0,0,0, 0,7,0, 0,0,0],
    [6,0,0, 1,0,0, 0,0,0],
    [0,9,8, 0,0,0, 0,0,0],

    [8,0,0, 0,6,0, 0,0,0],
    [4,0,0, 8,0,3, 0,0,1],
    [7,0,0, 0,2,0, 0,0,6],

    [0,0,0, 0,0,0, 0,0,0],
    [0,0,0, 4,0,9, 0,0,0],
    [0,0,0, 0,0,0, 0,0,0]
]

# 基础域约束
for r in range(9):
    for c in range(9):
        solver.assertFormula(solver.mkTerm(Kind.GEQ, grid[r][c], solver.mkInteger(1)))
        solver.assertFormula(solver.mkTerm(Kind.LEQ, grid[r][c], solver.mkInteger(9)))

# 已知数字约束
for r in range(9):
    for c in range(9):
        val = initial_board[r][c]
        if val != 0:
            solver.assertFormula(solver.mkTerm(Kind.EQUAL, grid[r][c], solver.mkInteger(val)))

def allDifferent(vars):
    # pairwise 不等式
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

solution_count = 0

while True:
    start_time = time.time()
    result = solver.checkSat()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("解", str(solution_count+1), f"运行时间: {elapsed_time:.6f} 秒")

    if not result.isSat():
        print("没有更多解了。")
        break

    # 获取当前解
    solution_count += 1
    print(f"解 #{solution_count}:")
    current_solution = []
    for r in range(9):
        row_vals = []
        for c in range(9):
            val = solver.getValue(grid[r][c]).getIntegerValue()
            row_vals.append(val)
        current_solution.append(row_vals)
        print(row_vals)

    # 创建用于排除当前解的新约束
    # new_constraint = OR(x_{r,c} != val for all r,c)
    # 我们用 Distinct 来构建不等式，然后用 OR 连接
    distinct_terms = []
    for r in range(9):
        for c in range(9):
            # x_{r,c} != current_solution[r][c]
            neq = solver.mkTerm(Kind.DISTINCT, grid[r][c], solver.mkInteger(current_solution[r][c]))
            distinct_terms.append(neq)

    # 至少有一个格子与当前解不同
    if len(distinct_terms) == 1:
        exclude_current_solution = distinct_terms[0]
    else:
        exclude_current_solution = solver.mkTerm(Kind.OR, distinct_terms[0], *distinct_terms[1:])

    solver.assertFormula(exclude_current_solution)

print(f"总共找到 {solution_count} 个解。")
