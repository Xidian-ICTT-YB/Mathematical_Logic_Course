# 导入Z3求解器库
from z3 import *

# 1. 定义整数变量（对应数学中的三个未知整数）
square = Int('square')
triangle = Int('triangle')
circle = Int('circle')

# 2. 创建求解器实例
solver = Solver()

# 3. 添加约束条件（与数学方程一一对应）
# 约束1：square² + circle = 16
solver.add(square * square + circle == 16)
# 约束2：triangle³ = 27
solver.add(triangle * triangle * triangle == 27)
# 约束3：triangle * square = 6
solver.add(triangle * square == 6)

# 4. 检查约束是否可满足
if solver.check() == sat:
    # 若可满足，获取求解模型
    model = solver.model()

    # 5. 提取变量的整数取值
    square_val = model.eval(square).as_long()
    triangle_val = model.eval(triangle).as_long()
    circle_val = model.eval(circle).as_long()

    # 6. 计算目标表达式结果
    target_result = square_val * circle_val * triangle_val

    # 7. 输出结果
    print("===== 变量求解结果 =====")
    print(f"square（正方形）的取值：{square_val}")
    print(f"triangle（三角形）的取值：{triangle_val}")
    print(f"circle（圆形）的取值：{circle_val}")
    print("\n===== 目标表达式计算结果 =====")
    print(f"square * circle * triangle = {square_val} * {circle_val} * {triangle_val} = {target_result}")
else:
    # 若约束不可满足
    print("该约束条件无整数解")