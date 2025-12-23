"""
布尔逻辑验证示例
验证逻辑等价性和重言式
"""
from cvc5 import Solver, Kind
def boolean_logic():
    slv = Solver()
    slv.setLogic("QF_LIA")
    p = slv.mkConst(slv.getBooleanSort(), "p")
    q = slv.mkConst(slv.getBooleanSort(), "q")
    not_p = slv.mkTerm(Kind.NOT, p)
    excluded_middle = slv.mkTerm(Kind.OR, p, not_p)
    negation = slv.mkTerm(Kind.NOT, excluded_middle)
    slv.assertFormula(negation)
    result = slv.checkSat()
    print(f"排中律 p ∨ ¬p 的否定可满足吗: {result}")
    slv.push()
    left_side = slv.mkTerm(Kind.NOT, slv.mkTerm(Kind.AND, p, q))
    right_side = slv.mkTerm(Kind.OR, slv.mkTerm(Kind.NOT, p), slv.mkTerm(Kind.NOT, q))
    demorgan_eq = slv.mkTerm(Kind.EQUAL, left_side, right_side)
    negation_demorgan = slv.mkTerm(Kind.NOT, demorgan_eq)
    slv.assertFormula(negation_demorgan)
    result = slv.checkSat()
    print(f"德摩根定律 ¬(p∧q) = ¬p∨¬q 总是成立吗: {result}")
    slv.pop()

if __name__ == "__main__":
    boolean_logic()