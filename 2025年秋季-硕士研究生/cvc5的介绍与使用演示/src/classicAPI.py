import cvc5
from cvc5 import Kind

# 创建求解器
solver = cvc5.Solver()
solver.setLogic("ALL")

# 允许生成模型
solver.setOption("produce-models", "true")

# 定义变量
x = solver.mkConst(solver.getIntegerSort(), "x")
y = solver.mkConst(solver.getIntegerSort(), "y")

# 定义约束
c1 = solver.mkTerm(Kind.GEQ, x, solver.mkInteger(5))       # x >= 5
c2 = solver.mkTerm(Kind.LT, y, solver.mkInteger(10))       # y < 10
c3 = solver.mkTerm(Kind.EQUAL, solver.mkTerm(Kind.ADD, x, y), solver.mkInteger(12))  # x + y = 12

# 向模型中添加约束
solver.assertFormula(c1)
solver.assertFormula(c2)
solver.assertFormula(c3)

# 检查可满足性
result = solver.checkSat()
print("result:", result)

# 获取解
if result.isSat():
    print("x =", solver.getValue(x))
    print("y =", solver.getValue(y))


