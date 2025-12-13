import cvc5
from cvc5 import Kind

# 创建求解器
solver = cvc5.Solver()
solver.setLogic("QF_NRA")
solver.setOption("produce-models", "true")

# 定义实数变量
x = solver.mkConst(solver.getRealSort(), "x")
y = solver.mkConst(solver.getRealSort(), "y")
z = solver.mkConst(solver.getRealSort(), "z")

# 构造方程 x^2*y + y*z + 2*x*y*z + 4*x*y + 8*x*z + 16 = 0
term1 = solver.mkTerm(Kind.MULT, solver.mkTerm(Kind.MULT, x, x), y)  # x^2 * y
term2 = solver.mkTerm(Kind.MULT, y, z)                               # y*z
term3 = solver.mkTerm(Kind.MULT, solver.mkTerm(Kind.MULT, solver.mkReal(2), x), solver.mkTerm(Kind.MULT, y, z))  # 2*x*y*z
term4 = solver.mkTerm(Kind.MULT, solver.mkReal(4), solver.mkTerm(Kind.MULT, x, y))  # 4*x*y
term5 = solver.mkTerm(Kind.MULT, solver.mkReal(8), solver.mkTerm(Kind.MULT, x, z))  # 8*x*z
term6 = solver.mkReal(16)                                           # 16

# 构造等式
eq = solver.mkTerm(Kind.EQUAL,
                   solver.mkTerm(Kind.ADD, term1, term2, term3, term4, term5, term6),
                   solver.mkReal(0))

# 添加约束
solver.assertFormula(eq)

# 检查可满足性
result = solver.checkSat()
print("result:", result)

# 获取一个可行解
if result.isSat():
    val_x = solver.getValue(x)
    val_y = solver.getValue(y)
    val_z = solver.getValue(z)
    print(f"x = {val_x}, y = {val_y}, z = {val_z}")

