import cvc5
from cvc5 import Kind

import time

tm = cvc5.TermManager()

solver = cvc5.Solver(tm)
solver.setOption("produce-models", "true")
solver.setOption("produce-unsat-cores", "true")
solver.setLogic("ALL")

realSort = tm.getRealSort()
intSort = tm.getIntegerSort()

x_var = tm.mkVar(intSort, 'x_var')
y_var = tm.mkVar(intSort, 'y_var')
x_var_list = tm.mkTerm(Kind.VARIABLE_LIST, x_var)
y_var_list = tm.mkTerm(Kind.VARIABLE_LIST, y_var)

a = 50
b = 50
alpha = tm.mkReal(a)
beta = tm.mkReal(b)
bool_True = tm.mkBoolean(1)

y_bigger_b = tm.mkTerm(Kind.GT, y_var, beta)
x_bigger_y = tm.mkTerm(Kind.GT, x_var, y_var)

exist_term = tm.mkTerm(Kind.AND, y_bigger_b, x_bigger_y)

exist = tm.mkTerm(Kind.EXISTS, y_var_list, exist_term)

x_bigger_a = tm.mkTerm(Kind.GT, x_var, alpha)

all_term = tm.mkTerm(Kind.IMPLIES, x_bigger_a, exist)

forall = tm.mkTerm(Kind.FORALL, x_var_list, all_term)

constraint = tm.mkTerm(Kind.EQUAL, forall, bool_True)

solver.assertFormula(constraint)

start_time = time.time()
result = solver.checkSat()
end_time = time.time()

if result.isSat():
    print(result)
else:
    unsatCore = solver.getUnsatCore()
    print("unsat core size:", len(unsatCore))
    print("unsat core:", unsatCore)

elapsed_time = end_time - start_time
print(f"运行时间: {elapsed_time:.6f} 秒")




