"""
cvc5 Python API 基础使用示例
演示基本的布尔逻辑和整数算术求解
"""

from cvc5 import Solver, Kind

def example_boolean_logic():
    """示例1: 布尔逻辑求解"""
    print("=" * 60)
    print("示例1: 布尔逻辑求解")
    print("=" * 60)
    
    # 创建求解器实例
    solver = Solver()
    solver.setOption("produce-models", "true")
    
    # 获取布尔类型
    bool_sort = solver.getBooleanSort()
    
    # 创建布尔变量 p, q, r
    p = solver.mkConst(bool_sort, "p")
    q = solver.mkConst(bool_sort, "q")
    r = solver.mkConst(bool_sort, "r")
    
    # 构建公式: (p AND q) OR (NOT r)
    # 使用 mkTerm 构建复合表达式
    p_and_q = solver.mkTerm(Kind.AND, p, q)
    not_r = solver.mkTerm(Kind.NOT, r)
    formula = solver.mkTerm(Kind.OR, p_and_q, not_r)
    
    print(f"公式: {formula}")
    
    # 添加断言
    solver.assertFormula(formula)
    
    # 检查可满足性
    result = solver.checkSat()
    print(f"结果: {result}")
    
    # 如果可满足，获取模型（变量赋值）
    if result.isSat():
        print("模型:")
        print(f"  p = {solver.getValue(p)}")
        print(f"  q = {solver.getValue(q)}")
        print(f"  r = {solver.getValue(r)}")
    print()


def example_integer_arithmetic():
    """示例2: 整数算术求解"""
    print("=" * 60)
    print("示例2: 整数算术求解")
    print("=" * 60)
    
    solver = Solver()
    solver.setOption("produce-models", "true")
    
    # 获取整数类型
    int_sort = solver.getIntegerSort()
    
    # 创建整数变量 x, y
    x = solver.mkConst(int_sort, "x")
    y = solver.mkConst(int_sort, "y")
    
    # 创建整数常量
    zero = solver.mkInteger(0)
    ten = solver.mkInteger(10)
    
    # 构建约束: x + y = 10 AND x > 0 AND y > 0
    x_plus_y = solver.mkTerm(Kind.ADD, x, y)
    constraint1 = solver.mkTerm(Kind.EQUAL, x_plus_y, ten)
    constraint2 = solver.mkTerm(Kind.GT, x, zero)
    constraint3 = solver.mkTerm(Kind.GT, y, zero)
    
    # 组合所有约束
    constraints = solver.mkTerm(Kind.AND, constraint1, constraint2, constraint3)
    
    print(f"约束: {constraints}")
    
    # 添加断言
    solver.assertFormula(constraints)
    
    # 求解
    result = solver.checkSat()
    print(f"结果: {result}")
    
    if result.isSat():
        print("找到一组解:")
        print(f"  x = {solver.getValue(x)}")
        print(f"  y = {solver.getValue(y)}")
    print()


def example_linear_arithmetic():
    """示例3: 线性算术求解"""
    print("=" * 60)
    print("示例3: 线性算术求解")
    print("=" * 60)
    
    solver = Solver()
    solver.setOption("produce-models", "true")
    
    # 实数类型
    real_sort = solver.getRealSort()
    
    # 创建实数变量
    x = solver.mkConst(real_sort, "x")
    y = solver.mkConst(real_sort, "y")
    
    # 创建实数常量
    two = solver.mkReal(2)
    three = solver.mkReal(3)
    twelve = solver.mkReal(12)
    
    # 构建约束: 2*x + 3*y = 12 AND x >= 0 AND y >= 0
    two_x = solver.mkTerm(Kind.MULT, two, x)
    three_y = solver.mkTerm(Kind.MULT, three, y)
    lhs = solver.mkTerm(Kind.ADD, two_x, three_y)
    
    constraint1 = solver.mkTerm(Kind.EQUAL, lhs, twelve)
    constraint2 = solver.mkTerm(Kind.GEQ, x, solver.mkReal(0))
    constraint3 = solver.mkTerm(Kind.GEQ, y, solver.mkReal(0))
    
    solver.assertFormula(constraint1)
    solver.assertFormula(constraint2)
    solver.assertFormula(constraint3)
    
    print(f"约束1: {constraint1}")
    print(f"约束2: {constraint2}")
    print(f"约束3: {constraint3}")
    
    result = solver.checkSat()
    print(f"结果: {result}")
    
    if result.isSat():
        print("找到一组解:")
        print(f"  x = {solver.getValue(x)}")
        print(f"  y = {solver.getValue(y)}")
    print()


def example_unsatisfiable():
    """示例4: 不可满足的公式"""
    print("=" * 60)
    print("示例4: 不可满足的公式")
    print("=" * 60)
    
    solver = Solver()
    solver.setOption("produce-models", "true")
    
    int_sort = solver.getIntegerSort()
    x = solver.mkConst(int_sort, "x")
    
    # 创建矛盾的约束: x > 5 AND x < 3
    five = solver.mkInteger(5)
    three = solver.mkInteger(3)
    
    constraint1 = solver.mkTerm(Kind.GT, x, five)
    constraint2 = solver.mkTerm(Kind.LT, x, three)
    
    solver.assertFormula(constraint1)
    solver.assertFormula(constraint2)
    
    print(f"约束1: {constraint1}")
    print(f"约束2: {constraint2}")
    
    result = solver.checkSat()
    print(f"结果: {result}")
    
    if result.isUnsat():
        print("这组约束不可满足（矛盾）")
    print()


def example_incremental_solving():
    """示例5: 增量求解"""
    print("=" * 60)
    print("示例5: 增量求解")
    print("=" * 60)
    
    solver = Solver()
    solver.setOption("incremental", "true")
    solver.setOption("produce-models", "true")
    
    int_sort = solver.getIntegerSort()
    x = solver.mkConst(int_sort, "x")
    
    # 第一个约束: x > 0
    constraint1 = solver.mkTerm(Kind.GT, x, solver.mkInteger(0))
    solver.assertFormula(constraint1)
    
    print(f"添加约束1: {constraint1}")
    result1 = solver.checkSat()
    print(f"结果1: {result1}")
    if result1.isSat():
        print(f"  x = {solver.getValue(x)}")
    
    # 添加第二个约束: x < 10
    constraint2 = solver.mkTerm(Kind.LT, x, solver.mkInteger(10))
    solver.assertFormula(constraint2)
    
    print(f"\n添加约束2: {constraint2}")
    result2 = solver.checkSat()
    print(f"结果2: {result2}")
    if result2.isSat():
        print(f"  x = {solver.getValue(x)}")
    
    # 添加第三个约束: x > 100 (与之前的约束矛盾)
    constraint3 = solver.mkTerm(Kind.GT, x, solver.mkInteger(100))
    solver.assertFormula(constraint3)
    
    print(f"\n添加约束3: {constraint3}")
    result3 = solver.checkSat()
    print(f"结果3: {result3}")
    print()


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("CVC5 Python API 基础使用示例")
    print("=" * 60 + "\n")
    
    example_boolean_logic()
    example_integer_arithmetic()
    example_linear_arithmetic()
    example_unsatisfiable()
    example_incremental_solving()
    
    print("=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
