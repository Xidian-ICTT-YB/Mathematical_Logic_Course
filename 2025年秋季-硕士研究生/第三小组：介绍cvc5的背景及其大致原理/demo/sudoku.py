import cvc5
from cvc5 import Kind # 导入Kind枚举，它代表了SMT求解器中所有可用的操作符类型（如等于、大于、加法等）。后续构建约束时，需要用它来指明具体的逻辑操作
import time

# 初始化 solver
tm = cvc5.TermManager()
solver = cvc5.Solver(tm) # 创建求解器实例
solver.setOption("produce-models", "true") # 要求求解器在问题可满足（SAT）时，输出一个具体的赋值模型（即数独的答案）。
solver.setOption("produce-unsat-cores", "true") # 要求求解器在问题不可满足（UNSAT）时，输出一个不可满足核心，这有助于定位矛盾的约束。
solver.setLogic("QF_LIA") # 设置求解的理论背景，QF代表量词自由，即没有全称量词和存在量词，LIA代表线性整数算数

intSort = tm.getIntegerSort() # 获取整数类型

# 定义 9x9 的矩阵变量
grid = [[tm.mkConst(intSort, f"x_{r}_{c}") for c in range(9)] for r in range(9)] # 创建变量来表示问题状态
# 为每个格子创建一个整数类型的常量符号，并命名为 x_r_c（如 x_0_0 代表第0行第0列）。求解的本质就是为这81个变量找到满足所有约束的整数值

# 新设计的数独题目（中等难度，有唯一解）
new_sudoku = [
    [0, 0, 0, 2, 0, 0, 0, 6, 3],
    [3, 0, 0, 0, 0, 5, 4, 0, 1],
    [0, 0, 1, 0, 0, 3, 9, 8, 0],
    [0, 0, 0, 0, 0, 0, 0, 9, 0],
    [0, 0, 0, 5, 3, 8, 0, 0, 0],
    [0, 3, 0, 0, 0, 0, 0, 0, 0],
    [0, 2, 6, 7, 0, 0, 5, 0, 0],
    [5, 0, 3, 8, 0, 0, 0, 0, 7],
    [7, 8, 0, 0, 0, 6, 0, 0, 0]
]

print("题目：")
for row in new_sudoku:
    print(row)
print()

'''这部分将所有数独规则转化为逻辑断言（assertFormula），告诉求解器必须满足的条件'''
# 基础域约束：每个变量在 1 到 9 之间
for r in range(9):
    for c in range(9):
        solver.assertFormula(tm.mkTerm(Kind.GEQ, grid[r][c], tm.mkInteger(1))) # 81个整数必须大于等于1，GEQ为'Greatr than or EQual to'
        solver.assertFormula(tm.mkTerm(Kind.LEQ, grid[r][c], tm.mkInteger(9))) # 81个整数必须小于等于9，LEA为'Less than or EQual to'

# 已知格子约束，将题目中预先给定的数字作为固定约束，遍历题目矩阵，如果值不为0，就断言该位置的变量等于该固定值
for r in range(9):
    for c in range(9):
        val = new_sudoku[r][c]
        if val != 0:
            solver.assertFormula(tm.mkTerm(Kind.EQUAL, grid[r][c],tm.mkInteger(val)))


# 辅助函数：创建 all-different 约束，对列表中的变量进行两两组合，为每一对变量断言 DISTINCT（不相等）关系
def allDifferent(vars):
    for i in range(len(vars)):
        for j in range(i + 1, len(vars)):
            solver.assertFormula(tm.mkTerm(Kind.DISTINCT, vars[i], vars[j]))


# 行约束
for r in range(9):
    allDifferent(grid[r])

# 列约束
for c in range(9):
    col_vars = [grid[r][c] for r in range(9)]
    allDifferent(col_vars)

# 3x3 box 约束，外层遍历9个宫，内层遍历每个宫的9个元素，并约束每个宫中的数互异
for box_r in range(3):
    for box_c in range(3):
        box_vars = []
        for rr in range(3):
            for cc in range(3):
                box_vars.append(grid[3 * box_r + rr][3 * box_c + cc])
        allDifferent(box_vars)

# 求解
start_time = time.time()
result = solver.checkSat() # 启动求解过程，核心调用
end_time = time.time()

print("求解结果:", result)

if result.isSat():
    print("\n数独的解：")
    solution = [[0] * 9 for _ in range(9)]
    for r in range(9):
        for c in range(9):
            val = solver.getValue(grid[r][c]).getIntegerValue() # 获取求解器为每个变量赋予的具体值
            solution[r][c] = val

    # 美化输出
    print("+" + "---+" * 9)
    for i, row in enumerate(solution):
        print("| " + " | ".join(str(x) if x != 0 else " " for x in row) + " |")
        if (i + 1) % 3 == 0:
            print("+" + "---+" * 9)
        else:
            print("|" + "---|" * 9)
else:
    print("无解")
    unsatCore = solver.getUnsatCore()
    print("不可满足核心大小:", len(unsatCore))

elapsed_time = end_time - start_time
print(f"\n求解时间: {elapsed_time:.6f} 秒")