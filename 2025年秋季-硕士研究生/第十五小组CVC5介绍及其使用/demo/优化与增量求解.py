# 文工厂生产规划:
# 两种产品 A 和 B。最大化利润。
# 约束：原材料、工时限制。
import cvc5
from cvc5 import Kind
import time

tm = cvc5.TermManager()
solver = cvc5.Solver(tm)
solver.setOption("produce-models", "true")
solver.setLogic("QF_LIA")

intSort = tm.getIntegerSort()

# 变量：生产数量 A 和 B
a = tm.mkConst(intSort, 'Product_A')
b = tm.mkConst(intSort, 'Product_B')

zero = tm.mkInteger(0)

# 约束1: 数量非负
solver.assertFormula(tm.mkTerm(Kind.GEQ, a, zero))
solver.assertFormula(tm.mkTerm(Kind.GEQ, b, zero))

# 约束2: 原材料限制 (2*A + 1*B <= 10)
term_mat = tm.mkTerm(Kind.ADD, tm.mkTerm(Kind.MULT, tm.mkInteger(2), a), b)
solver.assertFormula(tm.mkTerm(Kind.LEQ, term_mat, tm.mkInteger(10)))

# 约束3: 工时限制 (1*A + 2*B <= 8)
term_time = tm.mkTerm(Kind.ADD, a, tm.mkTerm(Kind.MULT, tm.mkInteger(2), b))
solver.assertFormula(tm.mkTerm(Kind.LEQ, term_time, tm.mkInteger(8)))

# 目标函数: 利润 = 3*A + 4*B
# profit = 3a + 4b
val_a = tm.mkTerm(Kind.MULT, tm.mkInteger(3), a)
val_b = tm.mkTerm(Kind.MULT, tm.mkInteger(4), b)
profit = tm.mkTerm(Kind.ADD, val_a, val_b)

print("开始计算最大利润...")
max_profit = -1

# 简单线性扫描寻找最大值 (仿照原文件的 loop 结构)
# 假设利润上限 50
for i in range(50):
    # 创建临时上下文
    solver.push()

    # 询问: 利润能否 >= i ?
    target = tm.mkInteger(i)
    can_reach = tm.mkTerm(Kind.GEQ, profit, target)
    solver.assertFormula(can_reach)

    result = solver.checkSat()

    if result.isSat():
        # 如果能达到，记录下来，并打印方案
        max_profit = i
        val_A = solver.getValue(a).getIntegerValue()
        val_B = solver.getValue(b).getIntegerValue()
        # 并不是每次都打印，为了整洁，只更新状态
        # print(f"利润 {i} 可达: A={val_A}, B={val_B}")
    else:
        # 一旦达不到，说明上一个是最大值，直接退出循环
        solver.pop()  # 恢复堆栈
        print(f"利润 {i} 无法达到。")
        break

    solver.pop()  # 准备下一次询问

print("-" * 30)
print(f"最大利润为: {max_profit}")

# 最后重新求解一次获取最优方案
solver.assertFormula(tm.mkTerm(Kind.EQUAL, profit, tm.mkInteger(max_profit)))
solver.checkSat()
print("最优生产方案:")
print("Product A:", solver.getValue(a).getIntegerValue())
print("Product B:", solver.getValue(b).getIntegerValue())