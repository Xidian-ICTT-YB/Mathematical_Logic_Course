import cvc5
from cvc5 import Kind
import time

# 初始化求解器
solver = cvc5.Solver()
solver.setOption("produce-models", "true")
solver.setOption("produce-unsat-cores", "true")
# 设置逻辑为纯布尔逻辑（QF_UF也可行，这里使用ALL也没问题）
solver.setLogic("ALL")

# 定义布尔类型
boolSort = solver.getBooleanSort()

# 创建布尔变量 a, b, c, d, e
a = solver.mkConst(boolSort, "a")
b = solver.mkConst(boolSort, "b")
c = solver.mkConst(boolSort, "c")
d = solver.mkConst(boolSort, "d")
e = solver.mkConst(boolSort, "e")

# 为方便使用，定义辅助函数：
def OR(*args):
    return solver.mkTerm(Kind.OR, *args)

def AND(*args):
    return solver.mkTerm(Kind.AND, *args)

def NOT(x):
    return solver.mkTerm(Kind.NOT, x)

def IMPLIES(x, y):
    return solver.mkTerm(Kind.IMPLIES, x, y)

def EQ(x, y):
    return solver.mkTerm(Kind.EQUAL, x, y)

# (a ∨ b)
clause1 = OR(a, b)
solver.assertFormula(clause1)

# (¬a ∨ c)
clause2 = OR(NOT(a), c)
solver.assertFormula(clause2)

# (¬b ∨ ¬c ∨ d)
clause3 = OR(NOT(b), NOT(c), d)
solver.assertFormula(clause3)

# (¬d ∨ e)
clause4 = OR(NOT(d), e)
solver.assertFormula(clause4)

# (a ∨ ¬e)
clause5 = OR(a, NOT(e))
solver.assertFormula(clause5)

# (b ∨ c ∨ d ∨ ¬e)
clause6 = OR(b, c, d, NOT(e))
solver.assertFormula(clause6)

# (¬a ∨ ¬b ∨ ¬c ∨ e)
clause7 = OR(NOT(a), NOT(b), NOT(c), e)
solver.assertFormula(clause7)


start_time = time.time()
result = solver.checkSat()
end_time = time.time()

print("结果:", result)
if result.isSat():
    a_val = solver.getValue(a).getBooleanValue()
    b_val = solver.getValue(b).getBooleanValue()
    c_val = solver.getValue(c).getBooleanValue()
    d_val = solver.getValue(d).getBooleanValue()
    e_val = solver.getValue(e).getBooleanValue()

    print("满足解:")
    print("a =", a_val)
    print("b =", b_val)
    print("c =", c_val)
    print("d =", d_val)
    print("e =", e_val)
else:
    print("公式不可满足。")
    unsatCore = solver.getUnsatCore()
    print("unsat core size:", len(unsatCore))
    print("unsat core:", unsatCore)


elapsed_time = end_time - start_time
print(f"运行时间: {elapsed_time:.6f} 秒")
