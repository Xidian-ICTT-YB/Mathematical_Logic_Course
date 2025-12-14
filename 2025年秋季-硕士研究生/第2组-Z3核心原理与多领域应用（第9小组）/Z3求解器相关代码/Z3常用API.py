# 导入Z3求解器
from z3 import *

# 一、变量声明
# 1. 声明单个整数变量（Int类型）
x_int = Int('x_int')
y_int = Int('y_int')
# 2. 声明单个实数变量（Real类型）
x_real = Real('x_real')
z_real = Real('z_real')
# 3. 声明单个布尔变量（Bool类型）
x_bool = Bool('x_bool')
flag_bool = Bool('flag_bool')
# 4. 声明位向量变量（BitVec类型）
x_bitvec = BitVec('x_bitvec', 8)
y_bitvec = BitVec('y_bitvec', 16)
# 5. 批量声明变量（以Real类型为例）
a_real, b_real, c_real = Reals('a_real b_real c_real')
m_int, n_int = Ints('m_int n_int')


# 二、常用API综合演示
# 场景：多类型变量联合约束求解，覆盖所有指定API

# 1. 创建约束求解器实例（API：Solver()）
solver = Solver()

# 2. 添加约束条件（API：solver.add()）
solver.add()
# 3. 判断约束是否可满足（API：solver.check()）
if solver.check() == sat:

# 4. 求解并获取模型（API：solver.model()）
    model = solver.model()

