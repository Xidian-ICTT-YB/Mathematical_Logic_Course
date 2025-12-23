"""
简单程序验证示例
验证程序前后条件
[(x > 0) → (y = x + 1)] ∧ [(x ≤ 0) → (y = x - 1)]
也就是(if x > 0 then y = x + 1 else y = x - 1)
"""
from cvc5 import Solver, Kind

def program_verification():
    slv = Solver()
    slv.setLogic("QF_LIA")
    x = slv.mkConst(slv.getIntegerSort(), "x")
    y = slv.mkConst(slv.getIntegerSort(), "y")
    condition = slv.mkTerm(Kind.GT, x, slv.mkInteger(0))
    then_branch = slv.mkTerm(Kind.EQUAL, y, slv.mkTerm(Kind.ADD, x, slv.mkInteger(1)))
    else_branch = slv.mkTerm(Kind.EQUAL, y, slv.mkTerm(Kind.SUB, x, slv.mkInteger(1)))
    program = slv.mkTerm(Kind.IMPLIES, condition, then_branch)
    program = slv.mkTerm(Kind.AND, program, 
                        slv.mkTerm(Kind.IMPLIES, slv.mkTerm(Kind.NOT, condition), else_branch))
    postcondition = slv.mkTerm(Kind.NOT, slv.mkTerm(Kind.EQUAL, y, x))
    verification_condition = slv.mkTerm(Kind.IMPLIES, program, postcondition)
    negation = slv.mkTerm(Kind.NOT, verification_condition)
    slv.assertFormula(negation)
    result = slv.checkSat()
    if result.isSat():
        print("找到反例！程序不满足规范")
        print(f"x = {slv.getValue(x)}")
        print(f"y = {slv.getValue(y)}")
    else:
        print("验证成功！程序总是满足后置条件 y ≠ x")
if __name__ == "__main__":
    program_verification()