# 无最大整数验证:对于任意整数 x，都存在一个 y，使得 y > x。
import cvc5
from cvc5 import Kind
import time

tm = cvc5.TermManager()
solver = cvc5.Solver(tm)
solver.setOption("produce-models", "true")
solver.setLogic("ALL") # 量词需要 ALL 或特定的 Quantifier 逻辑

intSort = tm.getIntegerSort()

# 定义变量
x = tm.mkVar(intSort, 'x')
y = tm.mkVar(intSort, 'y')

x_list = tm.mkTerm(Kind.VARIABLE_LIST, x)
y_list = tm.mkTerm(Kind.VARIABLE_LIST, y)

# 构造公式: Forall x. (Exists y. y > x)
y_gt_x = tm.mkTerm(Kind.GT, y, x)

exists_y = tm.mkTerm(Kind.EXISTS, y_list, y_gt_x)
forall_x = tm.mkTerm(Kind.FORALL, x_list, exists_y)

# 我们想验证这个命题是否为真
# 在 SMT 中，通常检查 (NOT 命题) 是否 UNSAT。
# 如果 (NOT 命题) 无解，说明原命题恒真。
negation = tm.mkTerm(Kind.NOT, forall_x)

solver.assertFormula(negation)

print("命题: 对于所有整数 x，存在 y > x")
print("正在尝试寻找反例 (证明命题为假)...")

start_time = time.time()
result = solver.checkSat()
end_time = time.time()

if result.isSat():
    print("找到反例，命题为假！(这在整数域不应该发生)")
else:
    print("Result: UNSAT")
    print("找不到反例 -> 命题得证 (True)。")

print(f"运行时间: {end_time - start_time:.6f} 秒")