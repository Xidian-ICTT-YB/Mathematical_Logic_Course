import cvc5
from cvc5 import Kind

import time

tm = cvc5.TermManager()                                 # Term  项  （一阶逻辑的基本组成）

solver = cvc5.Solver(tm)                                # 创建一个求解器对象
solver.setOption("produce-models", "true")          # 请求求解器在可满足时生成模型（变量的赋值）
solver.setOption("produce-unsat-cores", "true")     # 请求生成不可满足核心（若问题不可满足）

solver.setLogic("ALL")                                      # 使用所有支持的逻辑

intSort = tm.getIntegerSort()                           # 定义整数

x = tm.mkConst(intSort, 'x')                    # 定义整数 静态变量
y = tm.mkConst(intSort, 'y')
z = tm.mkConst(intSort, 'z')

zero = tm.mkInteger(0)                              # 定义常数
one = tm.mkInteger(1)
two = tm.mkInteger(2)
three = tm.mkInteger(3)
ten = tm.mkInteger(10)
fifteen = tm.mkInteger(15)

x_2 = tm.mkTerm(Kind.MULT, x, x)                    # 定义一些项
y_2 = tm.mkTerm(Kind.MULT, y, y)
z_2 = tm.mkTerm(Kind.MULT, z, z)

third_y = tm.mkTerm(Kind.MULT, y, three)
twice_z = tm.mkTerm(Kind.MULT, z, two)

x_add_y_add_z = tm.mkTerm(Kind.ADD, x, y, z)
constraint1 = tm.mkTerm(Kind.LT, x_add_y_add_z, fifteen)
#less than
x_add_3y_add_2z = tm.mkTerm(Kind.ADD, x, third_y, twice_z)
constraint2 = tm.mkTerm(Kind.GT, x_add_3y_add_2z, ten)

solver.assertFormula(constraint1)                   # 添加约束
solver.assertFormula(constraint2)

target_func = tm.mkTerm(Kind.ADD, x_2, y_2, z_2)

for i in range(500):                                # 循环 观察求解整数规划的效率
    temp_constraint = tm.mkTerm(Kind.EQUAL, target_func, tm.mkInteger(i))
    solver.push()
    solver.assertFormula(temp_constraint)

    start_time = time.time()
    result = solver.checkSat()                      # 求解
    end_time = time.time()

    elapsed_time = end_time - start_time
    print("target function", i, f" 运行时间: {elapsed_time:.6f} 秒")

    if result.isSat():
        xVal = solver.getValue(x)
        xPy = xVal.getRealValue()
        print("value for x: ", xPy)

        yVal = solver.getValue(y)
        yPy = yVal.getRealValue()
        print("value for y: ", yPy)

        zVal = solver.getValue(z)
        zPy = zVal.getRealValue()
        print("value for z: ", zPy)

        print("value for target function: ", i, " available")
    else:
        unsatCore = solver.getUnsatCore()          # 返回不可解的core
        print("unsat core size:", len(unsatCore))
        print("unsat core:", unsatCore)
        print("value for target function: ", i, " not available")
    solver.pop()  # 恢复约束状态
    print("-"*50)

end_time = time.time()

elapsed_time = end_time - start_time
print(f"运行时间: {elapsed_time:.6f} 秒")




