import cvc5
from cvc5 import Kind
import time

# 初始化求解器
solver = cvc5.Solver()
solver.setOption("produce-models", "true")
solver.setOption("produce-unsat-cores", "true")
solver.setLogic("ALL")

boolSort = solver.getBooleanSort()

# 创建布尔变量 a, b, c, d, e
a = solver.mkConst(boolSort, "a")
b = solver.mkConst(boolSort, "b")
c = solver.mkConst(boolSort, "c")
d = solver.mkConst(boolSort, "d")
e = solver.mkConst(boolSort, "e")

# 定义辅助函数简化逻辑表达
def OR(*args):
    return solver.mkTerm(Kind.OR, *args)

def NOT(x):
    return solver.mkTerm(Kind.NOT, x)

def assert_clause(*lits):
    clause = OR(*lits)
    solver.assertFormula(clause)

# 添加子句
# 1. (a ∨ b)
assert_clause(a, b)

# 2. (¬a ∨ c)
assert_clause(NOT(a), c)

# 3. (¬b ∨ ¬c ∨ d)
assert_clause(NOT(b), NOT(c), d)

# 4. (¬d ∨ e)
assert_clause(NOT(d), e)

# 5. (a ∨ ¬e)
assert_clause(a, NOT(e))

# 6. (b ∨ c ∨ d ∨ ¬e)
assert_clause(b, c, d, NOT(e))

# 7. (¬a ∨ ¬b ∨ ¬c ∨ e)
assert_clause(NOT(a), NOT(b), NOT(c), e)

# 强制所有变量都为 True
# 8. (a)
solver.assertFormula(a)

# 9. (b)
solver.assertFormula(b)

# 10. (c)
solver.assertFormula(c)

# 11. (d)
solver.assertFormula(d)

# 12. (e)
solver.assertFormula(e)

# 要求至少有一个变量为 False
# 13. (¬a ∨ ¬b ∨ ¬c ∨ ¬d ∨ ¬e)
assert_clause(NOT(a), NOT(b), NOT(c), NOT(d), NOT(e))

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

    print("a =", a_val)
    print("b =", b_val)
    print("c =", c_val)
    print("d =", d_val)
    print("e =", e_val)
else:
    unsatCore = solver.getUnsatCore()
    print("unsat core size:", len(unsatCore))
    print("unsat core:", unsatCore)

elapsed_time = end_time - start_time
print(f"运行时间: {elapsed_time:.6f} 秒")
