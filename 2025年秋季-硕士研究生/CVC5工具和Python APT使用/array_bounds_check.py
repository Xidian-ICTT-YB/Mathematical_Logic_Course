#!/usr/bin/env python3
"""
数组边界检查验证,验证数组访问的安全性
"""
from cvc5 import Solver, Kind

def array_bounds_check():
    slv = Solver()
    slv.setLogic("QF_AUFLIA")  
    slv.setOption("produce-models", "true") 
    array_sort = slv.mkArraySort(slv.getIntegerSort(), slv.getIntegerSort())
    arr = slv.mkConst(array_sort, "arr")
    index = slv.mkConst(slv.getIntegerSort(), "i")
    safe_access = slv.mkTerm(Kind.AND,
                            slv.mkTerm(Kind.GEQ, index, slv.mkInteger(0)),
                            slv.mkTerm(Kind.LEQ, index, slv.mkInteger(9)))
    out_of_bounds = slv.mkTerm(Kind.NOT, safe_access)
    slv.assertFormula(out_of_bounds)
    result = slv.checkSat()
    if result.isSat():
        print("找到越界访问的例子:")
        idx_val = slv.getValue(index)
        print(f"索引 i = {idx_val}")
        idx_str = str(idx_val)
        if idx_str.startswith('(') and idx_str.endswith(')'):
            idx_str = idx_str[1:-1] 
            idx_str =  idx_str.replace(" ","")
        idx_int = int(idx_str) 
        if idx_int < 0:
            print("负索引访问！")
        else:
            print("索引超出上界！")
    else:
        print("无法找到越界访问的例子（这通常不会发生）")

if __name__ == "__main__":
    array_bounds_check()