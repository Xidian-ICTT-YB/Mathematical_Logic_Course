import cvc5
from cvc5 import Kind

# 初始化TermManager和Solver
tm = cvc5.TermManager() # 创建求解器实例
solver = cvc5.Solver(tm) # 初始化

# 设置选项
solver.setOption("produce-models", "true")
solver.setOption("produce-unsat-cores", "true")
solver.setLogic("ALL")

# 获取布尔排序
boolSort = tm.getBooleanSort()

# 创建四个布尔变量，表示A、B、C、D是否说真话
a = tm.mkConst(boolSort, "a")
b = tm.mkConst(boolSort, "b")
c = tm.mkConst(boolSort, "c")
d = tm.mkConst(boolSort, "d")

# 创建否定项：not_b, not_c
not_b = tm.mkTerm(Kind.NOT, b) # ¬b
not_c = tm.mkTerm(Kind.NOT, c) # ¬c

# 构建A的陈述：B和C都是说谎者，即 (not_b and not_c)
a_statement = tm.mkTerm(Kind.AND, not_b, not_c)

# 约束1: a等价于a的陈述（如果a说真话，则陈述为真）
constraint1 = tm.mkTerm(Kind.EQUAL, a, a_statement)

# 约束2: b等价于a（b说"A是说真话的"）
constraint2 = tm.mkTerm(Kind.EQUAL, b, a)

# 约束3: c等价于not_b（c说"B在说谎"）
constraint3 = tm.mkTerm(Kind.EQUAL, c, not_b)

# 约束4: d等价于c（d说"C在说真话"）
constraint4 = tm.mkTerm(Kind.EQUAL, d, c)

# 将所有约束合取为一个公式
conjunction = tm.mkTerm(Kind.AND, constraint1, constraint2, constraint3, constraint4)

# 断言合取公式为真
solver.assertFormula(conjunction)

# 检查可满足性
result = solver.checkSat()

print("可满足性结果:", result)

# 如果可满足，获取每个人的值
if result.isSat():
    a_val = solver.getValue(a)
    b_val = solver.getValue(b)
    c_val = solver.getValue(c)
    d_val = solver.getValue(d)

    print("A 说真话?", a_val)
    print("B 说真话?", b_val)
    print("C 说真话?", c_val)
    print("D 说真话?", d_val)

    # 修正：正确获取布尔值的方法
    # 方法1：将Term转换为字符串后比较
    a_bool = str(a_val) == "true"
    b_bool = str(b_val) == "true"
    c_bool = str(c_val) == "true"
    d_bool = str(d_val) == "true"

    # 方法2：或者使用getBooleanValue()方法（如果可用）
    # 如果上面的方法不行，可以尝试这个：
    # a_bool = a_val.getBooleanValue()
    # b_bool = b_val.getBooleanValue()
    # c_bool = c_val.getBooleanValue()
    # d_bool = d_val.getBooleanValue()

    print("\n结论:")
    print("A 是", "真理者" if a_bool else "说谎者")
    print("B 是", "真理者" if b_bool else "说谎者")
    print("C 是", "真理者" if c_bool else "说谎者")
    print("D 是", "真理者" if d_bool else "说谎者")

    # 额外的验证：检查逻辑一致性
    print("\n验证:")
    print(f"A的陈述: B和C都是说谎者 -> B说谎: {not b_bool}, C说谎: {not c_bool}")
    print(f"B的陈述: A说真话 -> A说真话: {a_bool}")
    print(f"C的陈述: B在说谎 -> B说谎: {not b_bool}")
    print(f"D的陈述: C在说真话 -> C说真话: {c_bool}")
else:
    print("问题无解")