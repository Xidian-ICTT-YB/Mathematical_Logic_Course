#!/usr/bin/env python3
"""
位向量操作验证
"""
from cvc5 import Solver, Kind

def bitvector_verification():
    slv = Solver()
    slv.setLogic("QF_BV") 
    bv_sort = slv.mkBitVectorSort(8)
    a = slv.mkConst(bv_sort, "a")
    b = slv.mkConst(bv_sort, "b")
    zero = slv.mkBitVector(8, 0)
    and_zero = slv.mkTerm(Kind.BITVECTOR_AND, a, zero)
    prop1 = slv.mkTerm(Kind.EQUAL, and_zero, zero)
    xor_self = slv.mkTerm(Kind.BITVECTOR_XOR, a, a)
    prop2 = slv.mkTerm(Kind.EQUAL, xor_self, zero)
    not_prop1 = slv.mkTerm(Kind.NOT, prop1)
    not_prop2 = slv.mkTerm(Kind.NOT, prop2)
    slv.push()
    slv.assertFormula(not_prop1)
    result1 = slv.checkSat()
    print(f"性质 a AND 0 = 0 总是成立吗: {'是' if result1.isUnsat() else '否'}")
    slv.pop()
    slv.push()
    slv.assertFormula(not_prop2)
    result2 = slv.checkSat()
    print(f"性质 a XOR a = 0 总是成立吗: {'是' if result2.isUnsat() else '否'}")
    slv.pop()

if __name__ == "__main__":
    bitvector_verification()