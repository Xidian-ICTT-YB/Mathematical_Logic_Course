# 演示 Z3 解决数字谜题（Cryptarithmetic），模拟大模型将自然语言问题转化为 Z3 逻辑
# 谜题：SEND + MORE = MONEY

from z3 import *

# 1. 创建求解器
s = Solver()

# 2. 定义变量
# S, E, N, D, M, O, R, Y 必须是 0-9 的整数
char_names = 'SENDMORY'  # 存储原始字符名称
vars = [Int(c) for c in char_names]
S, E, N, D, M, O, R, Y = vars

# 3. 添加约束条件

# 约束 A: 每个字母都必须是 0 到 9 之间的数字
for v in vars:
    s.add(v >= 0, v <= 9)

# 约束 B: 每个字母代表的数字必须唯一 (Distinctness)
s.add(Distinct(vars))

# 约束 C: 首位字母不能为 0
# M 和 S 必须大于 0
s.add(M > 0, S > 0)

# 约束 D: 算术等式 (转化为代数表达式)
# 1000*S + 100*E + 10*N + D  +  1000*M + 100*O + 10*R + E  =  10000*M + 1000*O + 100*N + 10*E + Y
equation = (
        1000 * S + 100 * E + 10 * N + D +
        1000 * M + 100 * O + 10 * R + E
        ==
        10000 * M + 1000 * O + 100 * N + 10 * E + Y
)
s.add(equation)

# 4. 求解
print("--- 逻辑推理演示 (数字谜题) ---")
print("求解: SEND + MORE = MONEY")

if s.check() == sat:
    # 5. 输出模型
    m = s.model()

    # 修复：使用原始字符名称作为字典键，并使用 Z3 变量对象 (v) 访问模型 m
    solution = {name: m[v].as_long() for name, v in zip(char_names, vars)}

    S_val = solution['S']
    E_val = solution['E']
    N_val = solution['N']
    D_val = solution['D']
    M_val = solution['M']
    O_val = solution['O']
    R_val = solution['R']
    Y_val = solution['Y']

    SEND = S_val * 1000 + E_val * 100 + N_val * 10 + D_val
    MORE = M_val * 1000 + O_val * 100 + R_val * 10 + E_val
    MONEY = M_val * 10000 + O_val * 1000 + N_val * 100 + E_val * 10 + Y_val

    print("\n结果: 找到唯一解 (sat)")
    print(f"数字分配: {solution}")
    print("\n验证:")
    print(f"  {SEND}")
    print(f"+ {MORE}")
    print(f"-----")
    print(f"= {MONEY}")
    print(f"验证结果: {SEND + MORE == MONEY}")
else:
    print("\n结果: 无解 (unsat)")