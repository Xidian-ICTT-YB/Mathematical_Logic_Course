# 真话假话逻辑题:三个箱子，只有一个有宝藏。箱子上有字条，只有一句是真话。
import cvc5
from cvc5 import Kind

tm = cvc5.TermManager()
solver = cvc5.Solver(tm)

solver.setOption("produce-models", "true")
solver.setOption("produce-unsat-cores", "true")
solver.setLogic("ALL")

boolSort = tm.getBooleanSort()
bool_True = tm.mkBoolean(True)

# 变量：Gold_in_1 表示金子在箱子1
g1 = tm.mkConst(boolSort, "Gold_in_1")
g2 = tm.mkConst(boolSort, "Gold_in_2")
g3 = tm.mkConst(boolSort, "Gold_in_3")

# 物理事实：金子只能在一个箱子里 (g1, g2, g3 恰好一个为真)
# (g1 & !g2 & !g3) OR (!g1 & g2 & !g3) OR ...
fact1 = tm.mkTerm(Kind.AND, g1, tm.mkTerm(Kind.NOT, g2), tm.mkTerm(Kind.NOT, g3))
fact2 = tm.mkTerm(Kind.AND, tm.mkTerm(Kind.NOT, g1), g2, tm.mkTerm(Kind.NOT, g3))
fact3 = tm.mkTerm(Kind.AND, tm.mkTerm(Kind.NOT, g1), tm.mkTerm(Kind.NOT, g2), g3)
phy_constraint = tm.mkTerm(Kind.OR, fact1, fact2, fact3)
solver.assertFormula(phy_constraint)

# 箱子上的字条 (Statement)
# 箱子1说：“金子在这个箱子里” (s1 = g1)
s1 = g1
# 箱子2说：“金子不在这个箱子里” (s2 = !g2)
s2 = tm.mkTerm(Kind.NOT, g2)
# 箱子3说：“金子不在箱子1里” (s3 = !g1)
s3 = tm.mkTerm(Kind.NOT, g1)

# 规则：只有一句真话 (s1, s2, s3 恰好一个为真)
true_1 = tm.mkTerm(Kind.AND, s1, tm.mkTerm(Kind.NOT, s2), tm.mkTerm(Kind.NOT, s3))
true_2 = tm.mkTerm(Kind.AND, tm.mkTerm(Kind.NOT, s1), s2, tm.mkTerm(Kind.NOT, s3))
true_3 = tm.mkTerm(Kind.AND, tm.mkTerm(Kind.NOT, s1), tm.mkTerm(Kind.NOT, s2), s3)
rule_constraint = tm.mkTerm(Kind.OR, true_1, true_2, true_3)

solver.assertFormula(rule_constraint)

print("正在破解宝箱谜题...")
result = solver.checkSat()
print("结果:", result)

if result.isSat():
    print("箱子1有金子?", solver.getValue(g1))
    print("箱子2有金子?", solver.getValue(g2))
    print("箱子3有金子?", solver.getValue(g3))