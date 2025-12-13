import cvc5
from cvc5 import Kind

solver = cvc5.Solver()
solver.setLogic("ALL")
solver.setOption("produce-models", "true")

# 创建整数变量
j11 = solver.mkConst(solver.getIntegerSort(), "j11")
j12 = solver.mkConst(solver.getIntegerSort(), "j12")
j21 = solver.mkConst(solver.getIntegerSort(), "j21")
j22 = solver.mkConst(solver.getIntegerSort(), "j22")
j31 = solver.mkConst(solver.getIntegerSort(), "j31")
j32 = solver.mkConst(solver.getIntegerSort(), "j32")

# 非负约束
for x in [j11, j12, j21, j22, j31, j32]:
    solver.assertFormula(solver.mkTerm(Kind.GEQ, x, solver.mkInteger(0)))

# 作业阶段顺序约束
solver.assertFormula(solver.mkTerm(Kind.GEQ, solver.mkTerm(Kind.SUB, j12, j11), solver.mkInteger(10)))
solver.assertFormula(solver.mkTerm(Kind.GEQ, solver.mkTerm(Kind.SUB, j22, j21), solver.mkInteger(20)))
solver.assertFormula(solver.mkTerm(Kind.GEQ, solver.mkTerm(Kind.SUB, j32, j31), solver.mkInteger(5)))

# 机器 1 互斥
solver.assertFormula(
    solver.mkTerm(Kind.AND,
                  solver.mkTerm(Kind.OR,
                                solver.mkTerm(Kind.GEQ, solver.mkTerm(Kind.SUB, j22, j11), solver.mkInteger(10)),
                                solver.mkTerm(Kind.GEQ, solver.mkTerm(Kind.SUB, j11, j22), solver.mkInteger(5))),
                  solver.mkTerm(Kind.OR,
                                solver.mkTerm(Kind.GEQ, solver.mkTerm(Kind.SUB, j31, j11), solver.mkInteger(10)),
                                solver.mkTerm(Kind.GEQ, solver.mkTerm(Kind.SUB, j11, j31), solver.mkInteger(5))),
                  solver.mkTerm(Kind.OR,
                                solver.mkTerm(Kind.GEQ, solver.mkTerm(Kind.SUB, j31, j22), solver.mkInteger(5)),
                                solver.mkTerm(Kind.GEQ, solver.mkTerm(Kind.SUB, j22, j31), solver.mkInteger(5)))
                  )
)

# 机器 2 互斥
solver.assertFormula(
    solver.mkTerm(Kind.AND,
                  solver.mkTerm(Kind.OR,
                                solver.mkTerm(Kind.GEQ, solver.mkTerm(Kind.SUB, j21, j12), solver.mkInteger(5)),
                                solver.mkTerm(Kind.GEQ, solver.mkTerm(Kind.SUB, j12, j21), solver.mkInteger(20))),
                  solver.mkTerm(Kind.OR,
                                solver.mkTerm(Kind.GEQ, solver.mkTerm(Kind.SUB, j32, j12), solver.mkInteger(5)),
                                solver.mkTerm(Kind.GEQ, solver.mkTerm(Kind.SUB, j12, j32), solver.mkInteger(5))),
                  solver.mkTerm(Kind.OR,
                                solver.mkTerm(Kind.GEQ, solver.mkTerm(Kind.SUB, j32, j21), solver.mkInteger(20)),
                                solver.mkTerm(Kind.GEQ, solver.mkTerm(Kind.SUB, j21, j32), solver.mkInteger(5)))
                  )
)

# 总时长约束（设定为所有作业顺序完成的时间）
solver.assertFormula(solver.mkTerm(Kind.LEQ, j12, solver.mkInteger(45)))
solver.assertFormula(solver.mkTerm(Kind.LEQ, j22, solver.mkInteger(45)))
solver.assertFormula(solver.mkTerm(Kind.LEQ, j32, solver.mkInteger(45)))

# 查找最优完成时间
best = None
# 创建新的约束层
solver.push()
result = solver.checkSat()

# 重复求解，
while result.isSat():
    a = int(str(solver.getValue(j12)))
    b = int(str(solver.getValue(j22)))
    c = int(str(solver.getValue(j32)))

    solver.pop()
    best = max(a, b, c) + 5  # 直接用内置 max
    print("Best solution so far:", best, "minutes")

    new_threshold = best - 5
    solver.push()
    solver.assertFormula(
        solver.mkTerm(Kind.AND,
                      # 每个(j12, j22, j32) < max(a, b, c) 也即(j12, j22, j32) <= max(j12, j22, j32) - 1
                      solver.mkTerm(Kind.LT, j12, solver.mkInteger(new_threshold)),
                      solver.mkTerm(Kind.LT, j22, solver.mkInteger(new_threshold)),
                      solver.mkTerm(Kind.LT, j32, solver.mkInteger(new_threshold))
                      )
    )
    # 检查是否sat有解
    result = solver.checkSat()

solver.pop()
print(best, "minutes is the best solution")


