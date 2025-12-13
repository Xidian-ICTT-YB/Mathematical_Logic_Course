import cvc5
from cvc5 import Kind

# 创建求解器
solver = cvc5.Solver()
solver.setLogic("ALL")
solver.setOption("produce-models", "true")

# 布尔变量 p1..p12
p = {}
for k in range(1, 13):
    p[k] = solver.mkConst(solver.getBooleanSort(), f"p{k}")

# 字符串变量 x1..x5
x = {}
for k in range(1, 6):
    x[k] = solver.mkConst(solver.getStringSort(), f"x{k}")

# 中间字符串 i1..i6
i = {}
for k in range(1, 7):
    i[k] = solver.mkConst(solver.getStringSort(), f"i{k}")

# 目标字符串
result = solver.mkString("abbaabb")

# 长度约束：x1, x2 <= 2
solver.assertFormula(
    solver.mkTerm(
        Kind.AND,
        solver.mkTerm(Kind.LEQ,
            solver.mkTerm(Kind.STRING_LENGTH, x[1]),
                solver.mkInteger(2)),
        solver.mkTerm(Kind.LEQ,
            solver.mkTerm(Kind.STRING_LENGTH, x[2]),
                solver.mkInteger(2))
    )
)

# i1 = If(p1, x1, x2)
solver.assertFormula(
    solver.mkTerm(Kind.EQUAL, i[1], solver.mkTerm(Kind.ITE, p[1], x[1], x[2]))
)

# i2 = If(p2, x1, x2)
solver.assertFormula(
    solver.mkTerm(Kind.EQUAL, i[2], solver.mkTerm(Kind.ITE, p[2], x[1], x[2]))
)

# x3 = i1 + i2
solver.assertFormula(
    solver.mkTerm(Kind.EQUAL, x[3], solver.mkTerm(Kind.STRING_CONCAT, i[1], i[2]))
)

# i3 = If(p3, x1, If(p4, x2, x3))
solver.assertFormula(
    solver.mkTerm(Kind.EQUAL, i[3],
        solver.mkTerm(Kind.ITE, p[3], x[1],
            solver.mkTerm(Kind.ITE, p[4], x[2], x[3])
        ),
    )
)

# i4 = If(p5, x1, If(p6, x2, x3))
solver.assertFormula(
    solver.mkTerm(Kind.EQUAL, i[4],
        solver.mkTerm(Kind.ITE, p[5], x[1],
            solver.mkTerm(Kind.ITE, p[6], x[2], x[3])
        ),
    )
)

# x4 = i3 + i4
solver.assertFormula(
    solver.mkTerm(Kind.EQUAL, x[4],
        solver.mkTerm(Kind.STRING_CONCAT, i[3], i[4]))
)

# i5 = If(p7, x1, If(p8, x2, If(p9, x3, x4)))
solver.assertFormula(
    solver.mkTerm(Kind.EQUAL, i[5],
        solver.mkTerm(Kind.ITE, p[7], x[1],
            solver.mkTerm(Kind.ITE, p[8], x[2],
                solver.mkTerm(Kind.ITE, p[9], x[3], x[4])),
        ),
    )
)

# i6 = If(p10, x1, If(p11, x2, If(p12, x3, x4)))
solver.assertFormula(
    solver.mkTerm(Kind.EQUAL, i[6],
        solver.mkTerm(Kind.ITE, p[10], x[1],
            solver.mkTerm(Kind.ITE, p[11], x[2],
                solver.mkTerm(Kind.ITE, p[12], x[3], x[4])),
        ),
    )
)

# x5 = i5 + i6
solver.assertFormula(
    solver.mkTerm(Kind.EQUAL, x[5],
        solver.mkTerm(Kind.STRING_CONCAT, i[5], i[6]))
)

# 最终目标 x5 = "abbaabb"
solver.assertFormula(
    solver.mkTerm(Kind.EQUAL, x[5], result)
)

# 求解
res = solver.checkSat()
print("result:", res)

if res.isSat():
    print("SAT\n")

    # 打印布尔变量（选择路径）
    print("=== Boolean Choices (p1..p12) ===")
    for k in range(1, 13):
        print(f"p{k} = {solver.getValue(p[k])}")
    print()

    # 打印初始字符串变量
    print("=== Initial Strings (x1, x2) ===")
    print(f"x1 = {solver.getValue(x[1])}")
    print(f"x2 = {solver.getValue(x[2])}")
    print()

    # 打印中间选择结果 i1..i6
    print("=== Intermediate ITE Outputs (i1..i6) ===")
    for k in range(1, 7):
        print(f"i{k} = {solver.getValue(i[k])}")
    print()

    # 打印中间字符串和最终字符串
    print("=== Constructed Strings ===")
    print(f"x3 = {solver.getValue(x[3])}")
    print(f"x4 = {solver.getValue(x[4])}")
    print(f"x5 = {solver.getValue(x[5])}")
    print()

    # 更直观：打印构建链条
    print("=== Full Concatenation Trace ===")
    print(f"x3 = i1 + i2 = {solver.getValue(i[1])} + {solver.getValue(i[2])}")
    print(f"x4 = i3 + i4 = {solver.getValue(i[3])} + {solver.getValue(i[4])}")
    print(f"x5 = i5 + i6 = {solver.getValue(i[5])} + {solver.getValue(i[6])}")
    print()

else:
    print("UNSAT")