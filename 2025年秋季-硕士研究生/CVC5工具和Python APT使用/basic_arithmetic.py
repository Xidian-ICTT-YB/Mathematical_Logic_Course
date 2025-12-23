#!/usr/bin/env python3
"""
基础算术验证
"""
from cvc5 import Solver, Kind

def basic_arithmetic():
    slv = Solver()
    slv.setLogic("QF_LIA")
    slv.setOption("produce-models", "true")
    x = slv.mkConst(slv.getIntegerSort(), "x")
    y = slv.mkConst(slv.getIntegerSort(), "y")
    
    print("===基础算术验证===")
    print("\n1. 验证加法交换律 x + y = y + x")
    left = slv.mkTerm(Kind.ADD, x, y)
    right = slv.mkTerm(Kind.ADD, y, x)
    commutative = slv.mkTerm(Kind.EQUAL, left, right)
    slv.assertFormula(commutative)
    result = slv.checkSat()
    print(f"   结果: {result}")
    if result.isSat():
        print("加法交换律成立")
    print("\n2. 验证矛盾条件 x > 10 且 x < 5")
    slv.push()  
    contradiction = slv.mkTerm(Kind.AND,
                              slv.mkTerm(Kind.GT, x, slv.mkInteger(10)),
                              slv.mkTerm(Kind.LT, x, slv.mkInteger(5)))
    slv.assertFormula(contradiction)
    result = slv.checkSat()
    print(f"   结果: {result}")
    if result.isUnsat():
        print("正确检测到矛盾")
    else:
        print("预期应该是不可满足")
    slv.pop()
    print("\n3. 验证等式 x + 1 = 5")
    slv.push()
    equation = slv.mkTerm(Kind.EQUAL,
                         slv.mkTerm(Kind.ADD, x, slv.mkInteger(1)),
                         slv.mkInteger(5))
    slv.assertFormula(equation)
    result = slv.checkSat()
    print(f"   结果: {result}")
    if result.isSat():
        model = slv.getModel([], [])
        x_val = slv.getValue(x)
        print(f"   解: x = {x_val}")
        x_int = int(str(x_val))
        print(f"   验证: {x_int} + 1 = {x_int + 1}")
    slv.pop()
if __name__ == "__main__":
    basic_arithmetic()
    print("\n验证完成！")