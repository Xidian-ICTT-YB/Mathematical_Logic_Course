import cvc5
from cvc5 import Kind

tm = cvc5.TermManager()

solver = cvc5.Solver(tm)

solver.setOption("produce-models", "true")
solver.setOption("produce-unsat-cores", "true")
solver.setLogic("ALL")

boolSort = tm.getBooleanSort()

bool_True = tm.mkBoolean(1)

a = tm.mkConst(boolSort, "a")
b = tm.mkConst(boolSort, "b")
c = tm.mkConst(boolSort, "c")

not_a = tm.mkTerm(Kind.NOT, a)
not_b = tm.mkTerm(Kind.NOT, b)
not_c = tm.mkTerm(Kind.NOT, c)

term1 = tm.mkTerm(Kind.OR, not_a, not_b)
term2 = tm.mkTerm(Kind.OR, a, b)
term3 = tm.mkTerm(Kind.OR, not_b, not_c)
term4 = tm.mkTerm(Kind.OR, b, c)
term5 = tm.mkTerm(Kind.OR, not_a, not_c)
term6 = tm.mkTerm(Kind.OR, not_b, not_c)
term7 = tm.mkTerm(Kind.OR, a, b, c)

term0 = tm.mkTerm(Kind.AND, term1, term2, term3, term4, term5, term6, term7)

constraint = tm.mkTerm(Kind.EQUAL, term0, bool_True)

solver.assertFormula(constraint)

result = solver.checkSat()

print("结果: ", result)

if result.isSat():
    a_val = solver.getValue(a)
    print("a 的值: ", a_val)

    b_val = solver.getValue(b)
    print("b 的值: ", b_val)

    c_val = solver.getValue(c)
    print("c 的值: ", c_val)



