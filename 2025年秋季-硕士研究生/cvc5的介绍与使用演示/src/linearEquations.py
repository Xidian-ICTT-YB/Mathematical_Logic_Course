import cvc5
from cvc5 import Kind

solver = cvc5.Solver()
solver.setLogic("QF_LRA")  # 无量词线性实数算术
solver.setOption("produce-models", "true")

# 定义变量
x1 = solver.mkConst(solver.getRealSort(), "x1")
x2 = solver.mkConst(solver.getRealSort(), "x2")
x3 = solver.mkConst(solver.getRealSort(), "x3")
x4 = solver.mkConst(solver.getRealSort(), "x4")
x5 = solver.mkConst(solver.getRealSort(), "x5")

# 构造方程
eq1 = solver.mkTerm(Kind.EQUAL,
                    solver.mkTerm(Kind.ADD,
                                  solver.mkTerm(Kind.MULT, solver.mkReal(2), x1),
                                  solver.mkTerm(Kind.MULT, solver.mkReal(-1), x2),
                                  solver.mkTerm(Kind.MULT, solver.mkReal(3), x3),
                                  solver.mkTerm(Kind.MULT, solver.mkReal(-1), x4),
                                  solver.mkTerm(Kind.MULT, solver.mkReal(2), x5)),
                    solver.mkReal(7))

eq2 = solver.mkTerm(Kind.EQUAL,
                    solver.mkTerm(Kind.ADD,
                                  solver.mkTerm(Kind.MULT, solver.mkReal(-1), x1),
                                  solver.mkTerm(Kind.MULT, solver.mkReal(4), x2),
                                  solver.mkTerm(Kind.MULT, solver.mkReal(-2), x3),
                                  x4,
                                  x5),
                    solver.mkReal(3))

eq3 = solver.mkTerm(Kind.EQUAL,
                    solver.mkTerm(Kind.ADD,
                                  solver.mkTerm(Kind.MULT, solver.mkReal(3), x1),
                                  solver.mkTerm(Kind.MULT, solver.mkReal(-1), x2),
                                  x3,
                                  solver.mkTerm(Kind.MULT, solver.mkReal(2), x4),
                                  solver.mkTerm(Kind.MULT, solver.mkReal(-1), x5)),
                    solver.mkReal(4))

eq4 = solver.mkTerm(Kind.EQUAL,
                    solver.mkTerm(Kind.ADD, x1, x2, x3, x4, x5),
                    solver.mkReal(10))

eq5 = solver.mkTerm(Kind.EQUAL,
                    solver.mkTerm(Kind.ADD,
                                  solver.mkTerm(Kind.MULT, solver.mkReal(2), x1),
                                  solver.mkTerm(Kind.MULT, solver.mkReal(-3), x2),
                                  x3,
                                  solver.mkTerm(Kind.MULT, solver.mkReal(-1), x4),
                                  solver.mkTerm(Kind.MULT, solver.mkReal(4), x5)),
                    solver.mkReal(5))

# 添加方程
solver.assertFormula(eq1)
solver.assertFormula(eq2)
solver.assertFormula(eq3)
solver.assertFormula(eq4)
solver.assertFormula(eq5)

# 检查可满足性
result = solver.checkSat()
print("result:", result)

# 获取解
if result.isSat():
    for var in [x1, x2, x3, x4, x5]:
        print(f"{var} = {solver.getValue(var)}")

