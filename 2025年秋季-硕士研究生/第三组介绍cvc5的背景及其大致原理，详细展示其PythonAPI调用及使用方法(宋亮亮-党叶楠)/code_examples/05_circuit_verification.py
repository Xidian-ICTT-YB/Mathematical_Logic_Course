"""
实际应用示例3: 逻辑电路验证
使用 cvc5 验证逻辑电路的等价性和正确性
"""

from cvc5 import Solver, Kind

def example_circuit_equivalence():
    """示例1: 验证两个电路是否等价"""
    print("=" * 60)
    print("示例1: 电路等价性验证")
    print("=" * 60)
    
    solver = Solver()
    solver.setOption("produce-models", "true")
    
    # 获取布尔类型
    bool_sort = solver.getBooleanSort()
    
    # 输入变量
    a = solver.mkConst(bool_sort, "a")
    b = solver.mkConst(bool_sort, "b")
    c = solver.mkConst(bool_sort, "c")
    
    # 电路1: (a AND b) OR (a AND c)
    a_and_b = solver.mkTerm(Kind.AND, a, b)
    a_and_c = solver.mkTerm(Kind.AND, a, c)
    circuit1 = solver.mkTerm(Kind.OR, a_and_b, a_and_c)
    
    # 电路2: a AND (b OR c) - 根据分配律，应该等价
    b_or_c = solver.mkTerm(Kind.OR, b, c)
    circuit2 = solver.mkTerm(Kind.AND, a, b_or_c)
    
    print("电路1: (a AND b) OR (a AND c)")
    print("电路2: a AND (b OR c)")
    
    # 验证等价性：检查是否存在使得两个电路输出不同的输入
    not_equivalent = solver.mkTerm(Kind.DISTINCT, circuit1, circuit2)
    solver.assertFormula(not_equivalent)
    
    result = solver.checkSat()
    
    if result.isUnsat():
        print("\n结果: 两个电路等价！")
    else:
        print("\n结果: 两个电路不等价！")
        print("反例:")
        print(f"  a = {solver.getValue(a)}")
        print(f"  b = {solver.getValue(b)}")
        print(f"  c = {solver.getValue(c)}")
        print(f"  电路1输出 = {solver.getValue(circuit1)}")
        print(f"  电路2输出 = {solver.getValue(circuit2)}")
    print()


def example_full_adder():
    """示例2: 验证全加器的正确性"""
    print("=" * 60)
    print("示例2: 全加器验证")
    print("=" * 60)
    
    solver = Solver()
    solver.setOption("produce-models", "true")
    
    # 1位位向量类型
    bv1 = solver.mkBitVectorSort(1)
    
    # 输入: a, b, cin (进位输入)
    a = solver.mkConst(bv1, "a")
    b = solver.mkConst(bv1, "b")
    cin = solver.mkConst(bv1, "cin")
    
    # 全加器逻辑
    # sum = a XOR b XOR cin
    # cout = (a AND b) OR (cin AND (a XOR b))
    
    # 使用位向量操作
    a_xor_b = solver.mkTerm(Kind.BITVECTOR_XOR, a, b)
    sum_bit = solver.mkTerm(Kind.BITVECTOR_XOR, a_xor_b, cin)
    
    a_and_b = solver.mkTerm(Kind.BITVECTOR_AND, a, b)
    cin_and_axorb = solver.mkTerm(Kind.BITVECTOR_AND, cin, a_xor_b)
    cout = solver.mkTerm(Kind.BITVECTOR_OR, a_and_b, cin_and_axorb)
    
    # 验证: sum + 2*cout = a + b + cin
    # 转换为2位进行计算
    bv2 = solver.mkBitVectorSort(2)
    
    # 零扩展到2位 (需要使用 mkOp 创建带参数的操作符)
    zero_extend_op = solver.mkOp(Kind.BITVECTOR_ZERO_EXTEND, 1)
    a_ext = solver.mkTerm(zero_extend_op, a)
    b_ext = solver.mkTerm(zero_extend_op, b)
    cin_ext = solver.mkTerm(zero_extend_op, cin)
    sum_ext = solver.mkTerm(zero_extend_op, sum_bit)
    cout_ext = solver.mkTerm(zero_extend_op, cout)
    
    # 计算右侧: a + b + cin
    rhs = solver.mkTerm(Kind.BITVECTOR_ADD, a_ext, b_ext)
    rhs = solver.mkTerm(Kind.BITVECTOR_ADD, rhs, cin_ext)
    
    # 计算左侧: sum + 2*cout
    two = solver.mkBitVector(2, 2)
    cout_times_2 = solver.mkTerm(Kind.BITVECTOR_MULT, cout_ext, two)
    lhs = solver.mkTerm(Kind.BITVECTOR_ADD, sum_ext, cout_times_2)
    
    # 验证不等式（寻找反例）
    verification = solver.mkTerm(Kind.DISTINCT, lhs, rhs)
    solver.assertFormula(verification)
    
    result = solver.checkSat()
    
    if result.isUnsat():
        print("全加器实现正确！")
    else:
        print("全加器实现错误！")
        print("反例:")
        print(f"  a = {solver.getValue(a)}")
        print(f"  b = {solver.getValue(b)}")
        print(f"  cin = {solver.getValue(cin)}")
        print(f"  sum = {solver.getValue(sum_bit)}")
        print(f"  cout = {solver.getValue(cout)}")
    print()


def example_multiplexer():
    """示例3: 多路选择器验证"""
    print("=" * 60)
    print("示例3: 2-to-1 多路选择器验证")
    print("=" * 60)
    
    solver = Solver()
    solver.setOption("produce-models", "true")
    
    # 8位位向量
    bv8 = solver.mkBitVectorSort(8)
    bv1 = solver.mkBitVectorSort(1)
    
    # 输入
    input0 = solver.mkConst(bv8, "input0")
    input1 = solver.mkConst(bv8, "input1")
    select = solver.mkConst(bv1, "select")
    
    # 多路选择器逻辑: output = select ? input1 : input0
    # 使用位向量操作实现
    # output = (select AND input1) OR ((NOT select) AND input0)
    
    # 首先将 select 扩展到 8 位 (需要使用 mkOp 创建带参数的操作符)
    repeat_op = solver.mkOp(Kind.BITVECTOR_REPEAT, 8)
    select_ext = solver.mkTerm(repeat_op, select)
    
    # 计算
    not_select = solver.mkTerm(Kind.BITVECTOR_NOT, select_ext)
    
    select_and_input1 = solver.mkTerm(Kind.BITVECTOR_AND, select_ext, input1)
    notselect_and_input0 = solver.mkTerm(Kind.BITVECTOR_AND, not_select, input0)
    
    output = solver.mkTerm(Kind.BITVECTOR_OR, select_and_input1, notselect_and_input0)
    
    # 验证属性1: 当 select = 0 时，output = input0
    zero = solver.mkBitVector(1, 0)
    select_is_zero = solver.mkTerm(Kind.EQUAL, select, zero)
    output_is_input0 = solver.mkTerm(Kind.EQUAL, output, input0)
    property1 = solver.mkTerm(Kind.IMPLIES, select_is_zero, output_is_input0)
    
    # 验证属性2: 当 select = 1 时，output = input1
    one = solver.mkBitVector(1, 1)
    select_is_one = solver.mkTerm(Kind.EQUAL, select, one)
    output_is_input1 = solver.mkTerm(Kind.EQUAL, output, input1)
    property2 = solver.mkTerm(Kind.IMPLIES, select_is_one, output_is_input1)
    
    # 检查是否存在违反属性的情况
    not_property1 = solver.mkTerm(Kind.NOT, property1)
    solver.assertFormula(not_property1)
    
    result1 = solver.checkSat()
    
    if result1.isUnsat():
        print("属性1验证通过: select=0 时 output=input0")
    else:
        print("属性1验证失败!")
    
    # 重置求解器检查属性2
    solver2 = Solver()
    solver2.setOption("produce-models", "true")
    
    # 重新创建类型（每个求解器需要自己的类型）
    bv8_2 = solver2.mkBitVectorSort(8)
    bv1_2 = solver2.mkBitVectorSort(1)
    
    # 重新创建变量和电路（因为不能直接复用）
    input0_2 = solver2.mkConst(bv8_2, "input0")
    input1_2 = solver2.mkConst(bv8_2, "input1")
    select_2 = solver2.mkConst(bv1_2, "select")
    
    repeat_op_2 = solver2.mkOp(Kind.BITVECTOR_REPEAT, 8)
    select_ext_2 = solver2.mkTerm(repeat_op_2, select_2)
    not_select_2 = solver2.mkTerm(Kind.BITVECTOR_NOT, select_ext_2)
    
    select_and_input1_2 = solver2.mkTerm(Kind.BITVECTOR_AND, select_ext_2, input1_2)
    notselect_and_input0_2 = solver2.mkTerm(Kind.BITVECTOR_AND, not_select_2, input0_2)
    output_2 = solver2.mkTerm(Kind.BITVECTOR_OR, select_and_input1_2, notselect_and_input0_2)
    
    # 重新创建常量
    one_2 = solver2.mkBitVector(1, 1)
    
    select_is_one_2 = solver2.mkTerm(Kind.EQUAL, select_2, one_2)
    output_is_input1_2 = solver2.mkTerm(Kind.EQUAL, output_2, input1_2)
    property2_2 = solver2.mkTerm(Kind.IMPLIES, select_is_one_2, output_is_input1_2)
    
    not_property2 = solver2.mkTerm(Kind.NOT, property2_2)
    solver2.assertFormula(not_property2)
    
    result2 = solver2.checkSat()
    
    if result2.isUnsat():
        print("属性2验证通过: select=1 时 output=input1")
    else:
        print("属性2验证失败!")
    
    print("\n多路选择器验证完成！")
    print()


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("逻辑电路验证 - 使用 CVC5")
    print("=" * 60 + "\n")
    
    example_circuit_equivalence()
    example_full_adder()
    example_multiplexer()
    
    print("=" * 60)
    print("验证完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
