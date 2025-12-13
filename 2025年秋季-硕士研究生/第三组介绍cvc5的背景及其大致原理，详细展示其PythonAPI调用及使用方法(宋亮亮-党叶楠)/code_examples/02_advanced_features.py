"""
cvc5 Python API 高级特性示例
演示数组、位向量、量词、数据类型等高级功能
"""

from cvc5 import Solver, Kind

def example_arrays():
    """示例1: 数组理论"""
    print("=" * 60)
    print("示例1: 数组理论")
    print("=" * 60)
    
    solver = Solver()
    solver.setOption("produce-models", "true")
    
    # 创建数组类型: Array[Int -> Int]
    int_sort = solver.getIntegerSort()
    array_sort = solver.mkArraySort(int_sort, int_sort)
    
    # 创建数组变量
    arr = solver.mkConst(array_sort, "arr")
    
    # 创建索引变量
    i = solver.mkConst(int_sort, "i")
    j = solver.mkConst(int_sort, "j")
    
    # 数组操作: arr[i] = 5
    five = solver.mkInteger(5)
    arr_store = solver.mkTerm(Kind.STORE, arr, i, five)
    
    # 约束: arr[i] = 5 AND arr[j] = 10 AND i != j
    ten = solver.mkInteger(10)
    arr_i = solver.mkTerm(Kind.SELECT, arr, i)
    arr_j = solver.mkTerm(Kind.SELECT, arr, j)
    
    constraint1 = solver.mkTerm(Kind.EQUAL, arr_i, five)
    constraint2 = solver.mkTerm(Kind.EQUAL, arr_j, ten)
    constraint3 = solver.mkTerm(Kind.DISTINCT, i, j)
    
    solver.assertFormula(constraint1)
    solver.assertFormula(constraint2)
    solver.assertFormula(constraint3)
    
    print("约束:")
    print(f"  arr[i] = 5")
    print(f"  arr[j] = 10")
    print(f"  i != j")
    
    result = solver.checkSat()
    print(f"\n结果: {result}")
    
    if result.isSat():
        print("模型:")
        print(f"  i = {solver.getValue(i)}")
        print(f"  j = {solver.getValue(j)}")
        print(f"  arr = {solver.getValue(arr)}")
    print()


def example_bitvectors():
    """示例2: 位向量"""
    print("=" * 60)
    print("示例2: 位向量")
    print("=" * 60)
    
    solver = Solver()
    solver.setOption("produce-models", "true")
    
    # 创建8位位向量类型
    bv8_sort = solver.mkBitVectorSort(8)
    
    # 创建位向量变量
    x = solver.mkConst(bv8_sort, "x")
    y = solver.mkConst(bv8_sort, "y")
    
    # 创建位向量常量
    five = solver.mkBitVector(8, 5)
    three = solver.mkBitVector(8, 3)
    
    # 位向量运算: x & y = 5 AND x | y = 15
    x_and_y = solver.mkTerm(Kind.BITVECTOR_AND, x, y)
    x_or_y = solver.mkTerm(Kind.BITVECTOR_OR, x, y)
    fifteen = solver.mkBitVector(8, 15)
    
    constraint1 = solver.mkTerm(Kind.EQUAL, x_and_y, five)
    constraint2 = solver.mkTerm(Kind.EQUAL, x_or_y, fifteen)
    
    solver.assertFormula(constraint1)
    solver.assertFormula(constraint2)
    
    print("约束:")
    print(f"  x & y = 5")
    print(f"  x | y = 15")
    
    result = solver.checkSat()
    print(f"\n结果: {result}")
    
    if result.isSat():
        print("模型:")
        x_val = solver.getValue(x)
        y_val = solver.getValue(y)
        print(f"  x = {x_val} (十进制: {x_val.toPythonObj()})")
        print(f"  y = {y_val} (十进制: {y_val.toPythonObj()})")
    print()


def example_bitvector_arithmetic():
    """示例3: 位向量算术"""
    print("=" * 60)
    print("示例3: 位向量算术")
    print("=" * 60)
    
    solver = Solver()
    solver.setOption("produce-models", "true")
    
    # 32位位向量
    bv32 = solver.mkBitVectorSort(32)
    
    x = solver.mkConst(bv32, "x")
    y = solver.mkConst(bv32, "y")
    
    # 创建常量
    two = solver.mkBitVector(32, 2)
    ten = solver.mkBitVector(32, 10)
    
    # 约束: x * 2 = 10
    x_mult_2 = solver.mkTerm(Kind.BITVECTOR_MULT, x, two)
    constraint = solver.mkTerm(Kind.EQUAL, x_mult_2, ten)
    
    solver.assertFormula(constraint)
    
    print(f"约束: x * 2 = 10")
    
    result = solver.checkSat()
    print(f"结果: {result}")
    
    if result.isSat():
        x_val = solver.getValue(x)
        print(f"x = {x_val.toPythonObj()}")
    print()


def example_quantifiers():
    """示例4: 量词"""
    print("=" * 60)
    print("示例4: 量词")
    print("=" * 60)
    
    solver = Solver()
    solver.setOption("produce-models", "true")
    
    int_sort = solver.getIntegerSort()
    
    # 创建绑定变量（用于量词）
    x = solver.mkVar(int_sort, "x")
    
    # 创建自由变量
    y = solver.mkConst(int_sort, "y")
    
    # 构建公式: forall x. (x > 0 => x > y)
    zero = solver.mkInteger(0)
    x_gt_0 = solver.mkTerm(Kind.GT, x, zero)
    x_gt_y = solver.mkTerm(Kind.GT, x, y)
    implication = solver.mkTerm(Kind.IMPLIES, x_gt_0, x_gt_y)
    
    # 创建变量列表
    bound_vars = solver.mkTerm(Kind.VARIABLE_LIST, x)
    
    # 创建全称量词
    forall_formula = solver.mkTerm(Kind.FORALL, bound_vars, implication)
    
    print(f"公式: ∀x. (x > 0 ⇒ x > y)")
    
    # 这个公式可满足当且仅当 y <= 0
    solver.assertFormula(forall_formula)
    
    result = solver.checkSat()
    print(f"结果: {result}")
    
    if result.isSat():
        print(f"y = {solver.getValue(y)}")
    print()


def example_uninterpreted_functions():
    """示例5: 未解释函数"""
    print("=" * 60)
    print("示例5: 未解释函数")
    print("=" * 60)
    
    solver = Solver()
    solver.setOption("produce-models", "true")
    
    int_sort = solver.getIntegerSort()
    
    # 创建未解释函数 f: Int -> Int
    f = solver.mkConst(solver.mkFunctionSort(int_sort, int_sort), "f")
    
    # 创建变量
    x = solver.mkConst(int_sort, "x")
    y = solver.mkConst(int_sort, "y")
    
    # 创建函数应用
    fx = solver.mkTerm(Kind.APPLY_UF, f, x)
    fy = solver.mkTerm(Kind.APPLY_UF, f, y)
    
    # 约束: f(x) = x + 1 AND f(y) = 5
    one = solver.mkInteger(1)
    five = solver.mkInteger(5)
    
    x_plus_1 = solver.mkTerm(Kind.ADD, x, one)
    constraint1 = solver.mkTerm(Kind.EQUAL, fx, x_plus_1)
    constraint2 = solver.mkTerm(Kind.EQUAL, fy, five)
    
    solver.assertFormula(constraint1)
    solver.assertFormula(constraint2)
    
    print("约束:")
    print(f"  f(x) = x + 1")
    print(f"  f(y) = 5")
    
    result = solver.checkSat()
    print(f"\n结果: {result}")
    
    if result.isSat():
        print("模型:")
        print(f"  x = {solver.getValue(x)}")
        print(f"  y = {solver.getValue(y)}")
        print(f"  f(x) = {solver.getValue(fx)}")
        print(f"  f(y) = {solver.getValue(fy)}")
    print()


def example_datatypes():
    """示例6: 数据类型（代数数据类型）"""
    print("=" * 60)
    print("示例6: 数据类型")
    print("=" * 60)
    
    solver = Solver()
    solver.setOption("produce-models", "true")
    
    # 创建链表数据类型
    # datatype List = nil | cons(head: Int, tail: List)
    int_sort = solver.getIntegerSort()
    
    list_decl = solver.mkDatatypeDecl("List")
    
    # nil 构造器
    nil_cons = solver.mkDatatypeConstructorDecl("nil")
    list_decl.addConstructor(nil_cons)
    
    # cons 构造器
    cons_cons = solver.mkDatatypeConstructorDecl("cons")
    cons_cons.addSelector("head", int_sort)
    # 使用自引用（稍后解析）
    cons_cons.addSelectorSelf("tail")
    list_decl.addConstructor(cons_cons)
    
    # 创建数据类型
    list_sort = solver.mkDatatypeSort(list_decl)
    list_dt = list_sort.getDatatype()
    
    # 获取构造器和选择器
    nil = list_dt.getConstructor("nil").getTerm()
    cons = list_dt.getConstructor("cons").getTerm()
    head = list_dt["cons"].getSelector("head").getTerm()
    tail = list_dt["cons"].getSelector("tail").getTerm()
    
    # 创建列表: cons(1, cons(2, nil))
    nil_term = solver.mkTerm(Kind.APPLY_CONSTRUCTOR, nil)
    list2 = solver.mkTerm(Kind.APPLY_CONSTRUCTOR, cons, solver.mkInteger(2), nil_term)
    list1 = solver.mkTerm(Kind.APPLY_CONSTRUCTOR, cons, solver.mkInteger(1), list2)
    
    # 创建变量
    x = solver.mkConst(list_sort, "x")
    
    # 约束: x = cons(1, cons(2, nil))
    constraint = solver.mkTerm(Kind.EQUAL, x, list1)
    solver.assertFormula(constraint)
    
    print("数据类型定义:")
    print("  datatype List = nil | cons(head: Int, tail: List)")
    print("\n约束:")
    print("  x = cons(1, cons(2, nil))")
    
    result = solver.checkSat()
    print(f"\n结果: {result}")
    
    if result.isSat():
        print(f"x = {solver.getValue(x)}")
    print()


def example_strings():
    """示例7: 字符串理论"""
    print("=" * 60)
    print("示例7: 字符串理论")
    print("=" * 60)
    
    solver = Solver()
    solver.setOption("produce-models", "true")
    
    string_sort = solver.getStringSort()
    
    # 创建字符串变量
    x = solver.mkConst(string_sort, "x")
    y = solver.mkConst(string_sort, "y")
    
    # 创建字符串常量
    hello = solver.mkString("Hello")
    world = solver.mkString("World")
    
    # 字符串拼接: x ++ y = "HelloWorld"
    x_concat_y = solver.mkTerm(Kind.STRING_CONCAT, x, y)
    helloworld = solver.mkTerm(Kind.STRING_CONCAT, hello, world)
    
    constraint1 = solver.mkTerm(Kind.EQUAL, x_concat_y, helloworld)
    
    # 字符串长度约束: len(x) = 5
    len_x = solver.mkTerm(Kind.STRING_LENGTH, x)
    five = solver.mkInteger(5)
    constraint2 = solver.mkTerm(Kind.EQUAL, len_x, five)
    
    solver.assertFormula(constraint1)
    solver.assertFormula(constraint2)
    
    print("约束:")
    print(f"  x ++ y = 'HelloWorld'")
    print(f"  len(x) = 5")
    
    result = solver.checkSat()
    print(f"\n结果: {result}")
    
    if result.isSat():
        print("模型:")
        print(f"  x = {solver.getValue(x)}")
        print(f"  y = {solver.getValue(y)}")
    print()


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("CVC5 Python API 高级特性示例")
    print("=" * 60 + "\n")
    
    example_arrays()
    example_bitvectors()
    example_bitvector_arithmetic()
    example_quantifiers()
    example_uninterpreted_functions()
    example_datatypes()
    example_strings()
    
    print("=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
