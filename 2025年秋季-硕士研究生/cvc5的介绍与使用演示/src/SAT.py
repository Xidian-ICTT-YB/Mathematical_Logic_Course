import cvc5
from cvc5 import Kind

# 创建求解器
solver = cvc5.Solver()
solver.setLogic("ALL")
solver.setOption("produce-models", "true")

# 定义布尔变量
a = solver.mkConst(solver.getBooleanSort(), "a")
b = solver.mkConst(solver.getBooleanSort(), "b")
c = solver.mkConst(solver.getBooleanSort(), "c")
d = solver.mkConst(solver.getBooleanSort(), "d")
e = solver.mkConst(solver.getBooleanSort(), "e")

# 构造灵活析取公式
f1 = solver.mkTerm(Kind.OR, a, solver.mkTerm(Kind.NOT, b))
f2 = solver.mkTerm(Kind.OR, solver.mkTerm(Kind.NOT, a), b, d)
f3 = solver.mkTerm(Kind.OR, b, c, e, d)
f4 = solver.mkTerm(Kind.OR, solver.mkTerm(Kind.NOT, b), c, solver.mkTerm(Kind.NOT, d))
f5 = solver.mkTerm(Kind.OR, a, solver.mkTerm(Kind.NOT, d), e, b)
f6 = solver.mkTerm(Kind.OR, a, solver.mkTerm(Kind.NOT, c), d, e, b)
f7 = solver.mkTerm(Kind.OR, c, d, solver.mkTerm(Kind.NOT, e))

# 添加公式到求解器
solver.assertFormula(f1)
solver.assertFormula(f2)
solver.assertFormula(f3)
solver.assertFormula(f4)
solver.assertFormula(f5)
solver.assertFormula(f6)
solver.assertFormula(f7)

# 检查可满足性
result = solver.checkSat()
print("result:", result)

# 获取模型
if result.isSat():
    for var in [a, b, c, d, e]:
        print(f"{var} = {solver.getValue(var)}")
