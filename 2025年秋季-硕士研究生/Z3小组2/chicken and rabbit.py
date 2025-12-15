# 演示 Z3 的基础约束求解能力：鸡兔同笼问题
# 假设笼子里有鸡（2条腿）和兔（4条腿）。

from z3 import *

# 1. 创建求解器实例
s = Solver()

# 2. 定义变量：鸡的数量 (c) 和兔的数量 (r)
# 它们必须是整数且大于等于 0
c = Int('c')
r = Int('r')

# 3. 添加约束条件

# 约束 A: 头的总数是 35
# c + r = 35
heads_constraint = (c + r == 35)

# 约束 B: 脚的总数是 94
# 2*c + 4*r = 94
feet_constraint = (2 * c + 4 * r == 94)

# 约束 C: 数量必须是非负数
non_negative_c = (c >= 0)
non_negative_r = (r >= 0)

# 将所有约束添加到求解器
s.add(heads_constraint, feet_constraint, non_negative_c, non_negative_r)

# 4. 求解
print("--- 约束求解演示 (鸡兔同笼) ---")
print(f"约束条件: c + r = 35, 2c + 4r = 94 (c, r >= 0)")

if s.check() == sat:
    # 5. 输出模型（解）
    m = s.model()
    num_chickens = m[c]
    num_rabbits = m[r]

    print("\n结果: 找到满足约束的解 (sat)")
    print(f"鸡的数量 (c): {num_chickens}")
    print(f"兔的数量 (r): {num_rabbits}")
    print(f"\n验证: 鸡头 ({num_chickens}) + 兔头 ({num_rabbits}) = {num_chickens.as_long() + num_rabbits.as_long()}")
    print(f"验证: 鸡脚 ({num_chickens}*2) + 兔脚 ({num_rabbits}*4) = {num_chickens.as_long() * 2 + num_rabbits.as_long() * 4}")
else:
    print("\n结果: 无解 (unsat)")