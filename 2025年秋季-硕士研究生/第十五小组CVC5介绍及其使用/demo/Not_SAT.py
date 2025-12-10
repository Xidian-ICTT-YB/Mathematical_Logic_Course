# 鸽巢原理:尝试将 3 只鸽子放进 2 个笼子，要求每个笼子最多 1 只，必然无解。
import cvc5
from cvc5 import Kind
import time

solver = cvc5.Solver()
solver.setOption("produce-models", "true")
solver.setOption("produce-unsat-cores", "true") # 核心功能
solver.setLogic("ALL")

boolSort = solver.getBooleanSort()

# 定义 3 只鸽子 (p1, p2, p3) 在 2 个笼子 (h1, h2) 的位置
# p1_h1 表示：鸽子1 在 笼子1
p1_h1 = solver.mkConst(boolSort, "p1_in_h1")
p1_h2 = solver.mkConst(boolSort, "p1_in_h2")
p2_h1 = solver.mkConst(boolSort, "p2_in_h1")
p2_h2 = solver.mkConst(boolSort, "p2_in_h2")
p3_h1 = solver.mkConst(boolSort, "p3_in_h1")
p3_h2 = solver.mkConst(boolSort, "p3_in_h2")

def OR(*args): return solver.mkTerm(Kind.OR, *args)
def NOT(x): return solver.mkTerm(Kind.NOT, x)
def AND(*args): return solver.mkTerm(Kind.AND, *args)

# 约束 1: 每只鸽子必须至少在一个笼子里
solver.assertFormula(OR(p1_h1, p1_h2))
solver.assertFormula(OR(p2_h1, p2_h2))
solver.assertFormula(OR(p3_h1, p3_h2))

# 约束 2: 笼子 1 只能容纳 1 只鸽子 (两两互斥)
# 不能 (p1和p2都在 h1) AND 不能 (p1和p3都在 h1) ...
c1 = NOT(AND(p1_h1, p2_h1))
c2 = NOT(AND(p1_h1, p3_h1))
c3 = NOT(AND(p2_h1, p3_h1))

# 约束 3: 笼子 2 只能容纳 1 只鸽子
c4 = NOT(AND(p1_h2, p2_h2))
c5 = NOT(AND(p1_h2, p3_h2))
c6 = NOT(AND(p2_h2, p3_h2))

# 将冲突约束加入，并给予命名以便观察 Core（可选，这里直接加）
solver.assertFormula(c1)
solver.assertFormula(c2)
solver.assertFormula(c3)
solver.assertFormula(c4)
solver.assertFormula(c5)
solver.assertFormula(c6)

print("尝试将 3 只鸽子放入 2 个单间...")
result = solver.checkSat()

print("结果:", result)
if result.isSat():
    print("居然有解？")
else:
    print("无法满足 (符合预期)。")
    unsatCore = solver.getUnsatCore()
    print("矛盾核心大小:", len(unsatCore))
    print("造成矛盾的约束 (Unsat Core):", unsatCore)