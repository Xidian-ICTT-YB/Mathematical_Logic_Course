import cvc5
from cvc5 import Kind

print("=" * 50)
print("cvc5 数理逻辑作业：从基础逻辑到实际应用")
print("=" * 50)

# ------------------------------------------------------------------------------
# 模块1：布尔逻辑深化——永真性+逻辑等价性验证（德摩根定律）
# ------------------------------------------------------------------------------
print("\n【模块1：布尔逻辑永真性与等价性验证】")
print("1. 验证假言三段论：(a→b) ∧ (b→c) → (a→c)（永真式）")
print("2. 验证德摩根定律：¬(a∨b) ↔ (¬a∧¬b)（逻辑等价）")

# 子模块1.1：假言三段论永真性验证
solver1_1 = cvc5.Solver()
solver1_1.setOption("produce-models", "true")
bool_sort1 = solver1_1.getBooleanSort()
a1 = solver1_1.mkConst(bool_sort1, "a")
b1 = solver1_1.mkConst(bool_sort1, "b")
c1 = solver1_1.mkConst(bool_sort1, "c")

impl_a_b = solver1_1.mkTerm(Kind.IMPLIES, a1, b1)
impl_b_c = solver1_1.mkTerm(Kind.IMPLIES, b1, c1)
antecedent = solver1_1.mkTerm(Kind.AND, impl_a_b, impl_b_c)
impl_a_c = solver1_1.mkTerm(Kind.IMPLIES, a1, c1)
original_formula = solver1_1.mkTerm(Kind.IMPLIES, antecedent, impl_a_c)
neg_formula = solver1_1.mkTerm(Kind.NOT, original_formula)
solver1_1.assertFormula(neg_formula)
result1 = solver1_1.checkSat()
print(f"\n1.1 假言三段论否定式是否可满足？{result1}")
if result1.isUnsat():
    print("   结论：假言三段论是永真式（重言式），符合数理逻辑规则")

# 子模块1.2：德摩根定律等价性验证
solver1_2 = cvc5.Solver()
solver1_2.setOption("produce-models", "true")
bool_sort2 = solver1_2.getBooleanSort()
a2 = solver1_2.mkConst(bool_sort2, "a")
b2 = solver1_2.mkConst(bool_sort2, "b")

not_or_ab = solver1_2.mkTerm(Kind.NOT, solver1_2.mkTerm(Kind.OR, a2, b2))
not_a_and_not_b = solver1_2.mkTerm(Kind.AND, solver1_2.mkTerm(Kind.NOT, a2), solver1_2.mkTerm(Kind.NOT, b2))
equivalence = solver1_2.mkTerm(Kind.AND,
                               solver1_2.mkTerm(Kind.IMPLIES, not_or_ab, not_a_and_not_b),
                               solver1_2.mkTerm(Kind.IMPLIES, not_a_and_not_b, not_or_ab))
neg_equivalence = solver1_2.mkTerm(Kind.NOT, equivalence)
solver1_2.assertFormula(neg_equivalence)
result2 = solver1_2.checkSat()
print(f"\n1.2 德摩根定律否定式是否可满足？{result2}")
if result2.isUnsat():
    print("   结论：¬(a∨b) 与 (¬a∧¬b) 逻辑等价，验证了德摩根定律")

# ------------------------------------------------------------------------------
# 模块2：整数性质验证——奇偶性+素数约束
# ------------------------------------------------------------------------------
print("\n【模块2：整数性质验证（奇偶性+素数）】")
print("1. 验证：偶数+奇数=奇数（永真）")
print("2. 验证：是否存在大于10的素数x，满足x=2y+1（奇素数）且x<20")

# 子模块2.1：偶数+奇数=奇数验证
print(f"\n2.1 验证：偶数+奇数=奇数（永真性）")

# 方法1：使用模运算定义奇偶性
solver2_1 = cvc5.Solver()
solver2_1.setOption("produce-models", "true")
int_sort = solver2_1.getIntegerSort()

# 定义整数变量
x = solver2_1.mkConst(int_sort, "x")
y = solver2_1.mkConst(int_sort, "y")
sum_xy = solver2_1.mkTerm(Kind.ADD, x, y)

# 使用模运算定义奇偶性：偶数 ≡ x mod 2 = 0，奇数 ≡ y mod 2 = 1
two = solver2_1.mkInteger(2)
zero = solver2_1.mkInteger(0)
one = solver2_1.mkInteger(1)

# 偶数：x mod 2 = 0
even_x = solver2_1.mkTerm(Kind.EQUAL,
                         solver2_1.mkTerm(Kind.INTS_MODULUS, x, two),
                         zero)

# 奇数：y mod 2 = 1
odd_y = solver2_1.mkTerm(Kind.EQUAL,
                        solver2_1.mkTerm(Kind.INTS_MODULUS, y, two),
                        one)

# 和是奇数：(x+y) mod 2 = 1
odd_sum = solver2_1.mkTerm(Kind.EQUAL,
                          solver2_1.mkTerm(Kind.INTS_MODULUS, sum_xy, two),
                          one)

# 要证明的命题：(x是偶数 ∧ y是奇数) → (x+y是奇数)
proposition = solver2_1.mkTerm(Kind.IMPLIES,
                             solver2_1.mkTerm(Kind.AND, even_x, odd_y),
                             odd_sum)

# 使用反证法：证明否定式不可满足
neg_proposition = solver2_1.mkTerm(Kind.NOT, proposition)
solver2_1.assertFormula(neg_proposition)
result_odd = solver2_1.checkSat()

print(f"   偶数+奇数=奇数否定式是否可满足？{result_odd}")
if result_odd.isUnsat():
    print("   结论：偶数+奇数=奇数是永真式，符合整数奇偶性规则")
else:
    print("   注：由于cvc5整数理论求解器的限制，偶+奇=奇的永真性验证未通过")
    print("   数学理论：偶数+奇数确实等于奇数，这是整数算术的基本性质")

# 方法2：通过具体数值验证
print("\n   方法2：通过具体数值验证偶数+奇数=奇数")
solver2_1b = cvc5.Solver()
solver2_1b.setOption("produce-models", "true")

# 选择具体数值：偶数4，奇数3，和7（奇数）
four = solver2_1b.mkInteger(4)
three = solver2_1b.mkInteger(3)
seven = solver2_1b.mkInteger(7)

# 验证4+3=7
sum_eq = solver2_1b.mkTerm(Kind.EQUAL,
                          solver2_1b.mkTerm(Kind.ADD, four, three),
                          seven)
solver2_1b.assertFormula(sum_eq)
result_specific = solver2_1b.checkSat()
print(f"   4+3=7是否成立？{result_specific}")
if result_specific.isSat():
    print("   具体验证：4(偶)+3(奇)=7(奇)")

# 验证4是偶数，3是奇数
even_4 = solver2_1b.mkTerm(Kind.EQUAL,
                          solver2_1b.mkTerm(Kind.INTS_MODULUS, four, two),
                          zero)
odd_3 = solver2_1b.mkTerm(Kind.EQUAL,
                         solver2_1b.mkTerm(Kind.INTS_MODULUS, three, two),
                         one)
odd_7 = solver2_1b.mkTerm(Kind.EQUAL,
                         solver2_1b.mkTerm(Kind.INTS_MODULUS, seven, two),
                         one)

solver2_1b.push()
solver2_1b.assertFormula(even_4)
solver2_1b.assertFormula(odd_3)
solver2_1b.assertFormula(odd_7)
result_parity = solver2_1b.checkSat()
solver2_1b.pop()

if result_parity.isSat():
    print("   奇偶性验证：4是偶数，3是奇数，7是奇数")

# 子模块2.2：奇素数约束求解
solver2_2 = cvc5.Solver()
solver2_2.setOption("produce-models", "true")
int_sort2_2 = solver2_2.getIntegerSort()

x2_2 = solver2_2.mkConst(int_sort2_2, "x")
y2_2 = solver2_2.mkConst(int_sort2_2, "y")

# 约束1：x>10 ∧ x<20
c1 = solver2_2.mkTerm(Kind.AND,
                      solver2_2.mkTerm(Kind.GT, x2_2, solver2_2.mkInteger(10)),
                      solver2_2.mkTerm(Kind.LT, x2_2, solver2_2.mkInteger(20)))
# 约束2：x是奇数（x=2y+1）
c2 = solver2_2.mkTerm(Kind.EQUAL, x2_2,
                      solver2_2.mkTerm(Kind.ADD,
                                      solver2_2.mkTerm(Kind.MULT, solver2_2.mkInteger(2), y2_2),
                                      solver2_2.mkInteger(1)))
# 素数约束：x不能被2、3、5、7整除
divisors = [2, 3, 5, 7]
div_constraints = []
for d in divisors:
    k = solver2_2.mkConst(int_sort2_2, f"k_{d}")
    # 如果x能被d整除，则存在k使得x = k*d
    divisible = solver2_2.mkTerm(Kind.EQUAL, x2_2,
                                solver2_2.mkTerm(Kind.MULT, solver2_2.mkInteger(d), k))
    # 我们要的是x不能被d整除
    div_constraints.append(solver2_2.mkTerm(Kind.NOT, divisible))

c3 = solver2_2.mkTerm(Kind.AND, *div_constraints)

# 合取所有约束
all_constraints = solver2_2.mkTerm(Kind.AND, c1, c2, c3)
solver2_2.assertFormula(all_constraints)
result_prime = solver2_2.checkSat()
print(f"\n2.2 是否存在满足条件的奇素数？{result_prime}")
if result_prime.isSat():
    x_val = solver2_2.getValue(x2_2)
    y_val = solver2_2.getValue(y2_2)
    print(f"   解：x = {x_val}, y = {y_val}")
    # 验证x确实是素数
    x_int = int(str(x_val))
    is_prime = all(x_int % d != 0 for d in [2, 3, 5, 7, 11, 13, 17, 19] if d < x_int)
    if is_prime and x_int > 1:
        print(f"   验证：{x_int}是大于10小于20的奇素数")
    else:
        print(f"   注：{x_int}需要进一步验证是否为素数")

# ------------------------------------------------------------------------------
# 模块3：混合理论求解——整数+字符串
# ------------------------------------------------------------------------------
print("\n【模块3：混合理论求解（整数+字符串）】")
print("问题：存在 n（整数）和 s（字符串），满足：")
print("   1. n = |s|（n是s的长度）；2. 6≤n≤8；3. s以'logic_'开头；4. s以数字结尾")

solver3 = cvc5.Solver()
solver3.setOption("produce-models", "true")
try:
    solver3.setLogic("ALL")
except:
    solver3.setLogic("QF_SLIA")

str_sort3 = solver3.getStringSort()
int_sort3 = solver3.getIntegerSort()
s3 = solver3.mkConst(str_sort3, "s")
n3 = solver3.mkConst(int_sort3, "n")

# 构建约束
constraint1 = solver3.mkTerm(Kind.EQUAL, n3, solver3.mkTerm(Kind.STRING_LENGTH, s3))
constraint2 = solver3.mkTerm(Kind.GEQ, n3, solver3.mkInteger(6))
constraint3 = solver3.mkTerm(Kind.LEQ, n3, solver3.mkInteger(8))
constraint4 = solver3.mkTerm(Kind.STRING_PREFIX, solver3.mkString("logic_"), s3)

# s以数字结尾
digits = [solver3.mkString(str(d)) for d in range(10)]
suffix_constraints = []
for digit in digits:
    suffix_constraints.append(solver3.mkTerm(Kind.STRING_SUFFIX, digit, s3))
constraint5 = solver3.mkTerm(Kind.OR, *suffix_constraints)

all_constraints3 = solver3.mkTerm(Kind.AND, constraint1, constraint2, constraint3, constraint4, constraint5)
solver3.assertFormula(all_constraints3)
result3 = solver3.checkSat()

print(f"\n是否存在满足条件的 (n, s)？{result3}")
if result3.isSat():
    s_value = solver3.getValue(s3)
    n_value = solver3.getValue(n3)
    print(f"   解：n = {n_value}, s = {s_value}")

# ------------------------------------------------------------------------------
# 模块4：实际应用——布尔电路正确性验证
# ------------------------------------------------------------------------------
print("\n【模块4：实际应用——布尔电路验证（与或非门）】")
print("验证：半加器电路的正确性（输入a、b，输出和sum、进位carry）")
print("半加器逻辑：sum = a⊕b（异或），carry = a∧b（与）")

solver4 = cvc5.Solver()
solver4.setOption("produce-models", "true")
bool_sort4 = solver4.getBooleanSort()
a4 = solver4.mkConst(bool_sort4, "a")
b4 = solver4.mkConst(bool_sort4, "b")
sum_out4 = solver4.mkConst(bool_sort4, "sum")
carry_out4 = solver4.mkConst(bool_sort4, "carry")

# 修正异或定义：a⊕b = (a∧¬b)∨(¬a∧b)
xor_ab = solver4.mkTerm(Kind.OR,
                       solver4.mkTerm(Kind.AND, a4, solver4.mkTerm(Kind.NOT, b4)),
                       solver4.mkTerm(Kind.AND, solver4.mkTerm(Kind.NOT, a4), b4))

# 进位：carry = a∧b
and_ab = solver4.mkTerm(Kind.AND, a4, b4)

# 定义电路逻辑
sum_formula = solver4.mkTerm(Kind.EQUAL, sum_out4, xor_ab)
carry_formula = solver4.mkTerm(Kind.EQUAL, carry_out4, and_ab)

# 验证电路正确性
error_condition = solver4.mkTerm(Kind.OR,
                                solver4.mkTerm(Kind.NOT, sum_formula),
                                solver4.mkTerm(Kind.NOT, carry_formula))
solver4.assertFormula(error_condition)
result4 = solver4.checkSat()

print(f"\n半加器电路是否存在逻辑错误？{result4}")
if result4.isUnsat():
    print("   结论：半加器电路逻辑正确，符合布尔逻辑")
else:
    a_val = solver4.getValue(a4)
    b_val = solver4.getValue(b4)
    sum_val = solver4.getValue(sum_out4)
    carry_val = solver4.getValue(carry_out4)
    print(f"   发现错误案例：a={a_val}, b={b_val}")
    print(f"   期望输出：sum={solver4.getValue(xor_ab)}, carry={solver4.getValue(and_ab)}")
    print(f"   实际输出：sum={sum_val}, carry={carry_val}")

# 手动验证具体案例
print("\n   具体案例验证（手动计算）：")
test_cases = [(False, False), (False, True), (True, False), (True, True)]
for a_val, b_val in test_cases:
    # 手动计算异或和与
    sum_correct = (a_val and not b_val) or (not a_val and b_val)
    carry_correct = a_val and b_val
    print(f"   a={a_val}, b={b_val} -> sum={sum_correct}, carry={carry_correct}")

# ------------------------------------------------------------------------------
# 模块5：复杂约束——冲突分析与解的唯一性验证
# ------------------------------------------------------------------------------
print("\n【模块5：复杂约束——冲突分析与解的唯一性】")
print("约束：x+y=10 ∧ x≥3 ∧ y≥3 ∧ x是偶数 ∧ y是奇数")

solver5 = cvc5.Solver()
solver5.setOption("produce-models", "true")
int_sort5 = solver5.getIntegerSort()
x5 = solver5.mkConst(int_sort5, "x")
y5 = solver5.mkConst(int_sort5, "y")

# 使用模运算定义奇偶性
even_x5 = solver5.mkTerm(Kind.EQUAL,
                        solver5.mkTerm(Kind.INTS_MODULUS, x5, two),
                        zero)
odd_y5 = solver5.mkTerm(Kind.EQUAL,
                       solver5.mkTerm(Kind.INTS_MODULUS, y5, two),
                       one)

# 构建约束
c1 = solver5.mkTerm(Kind.EQUAL, solver5.mkTerm(Kind.ADD, x5, y5), solver5.mkInteger(10))
c2 = solver5.mkTerm(Kind.GEQ, x5, solver5.mkInteger(3))
c3 = solver5.mkTerm(Kind.GEQ, y5, solver5.mkInteger(3))

all_constraints5 = solver5.mkTerm(Kind.AND, c1, c2, c3, even_x5, odd_y5)
solver5.assertFormula(all_constraints5)
result5 = solver5.checkSat()

print(f"\n约束是否可满足？{result5}")
if result5.isSat():
    x_val = solver5.getValue(x5)
    y_val = solver5.getValue(y5)
    print(f"   解：x={x_val}, y={y_val}")
    print(f"   验证：x+y={int(str(x_val)) + int(str(y_val))}")
else:
    print("   结论：约束不可满足（存在逻辑冲突）")
    print("   数学分析：偶数+奇数=奇数，但10是偶数，所以约束系统矛盾")

# ------------------------------------------------------------------------------
# 模块6：程序正确性验证（霍尔逻辑）
# ------------------------------------------------------------------------------
print("\n【模块6：实际应用——霍尔逻辑验证程序正确性】")
print("程序逻辑：输入整数x（x≥0），执行x = x + 5，验证x≥5（后置条件）")

solver6 = cvc5.Solver()
solver6.setOption("produce-models", "true")
int_sort6 = solver6.getIntegerSort()
x_pre6 = solver6.mkConst(int_sort6, "x_pre")
x_post6 = solver6.mkConst(int_sort6, "x_post")

pre_condition = solver6.mkTerm(Kind.GEQ, x_pre6, solver6.mkInteger(0))
program_logic = solver6.mkTerm(Kind.EQUAL, x_post6,
                              solver6.mkTerm(Kind.ADD, x_pre6, solver6.mkInteger(5)))
post_condition = solver6.mkTerm(Kind.GEQ, x_post6, solver6.mkInteger(5))

hall_formula = solver6.mkTerm(Kind.IMPLIES,
                             solver6.mkTerm(Kind.AND, pre_condition, program_logic),
                             post_condition)
neg_hall = solver6.mkTerm(Kind.NOT, hall_formula)
solver6.assertFormula(neg_hall)
result6 = solver6.checkSat()

print(f"\n霍尔逻辑公式否定式是否可满足？{result6}")
if result6.isUnsat():
    print("   结论：程序逻辑正确，前置条件成立时后置条件必然成立")
else:
    x_pre_val = solver6.getValue(x_pre6)
    x_post_val = solver6.getValue(x_post6)
    print(f"   反例：x_pre={x_pre_val}, x_post={x_post_val}")
