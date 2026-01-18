# 演示 Z3 的位向量 (Bit-Vectors) 求解能力
# 目标：找到一个 4 字节的密钥 (key)，使得它满足特定的加密校验公式。

from z3 import *

# 1. 创建求解器
s = Solver()

# 2. 定义变量
# 'key' 是一个 32 位的位向量 (4 字节)
key = BitVec('key', 32)

# 3. 设定目标校验公式 (模拟加密/哈希校验)
# 假设校验公式为：(key XOR 0xDEADBEEF) + 0xCAFEBABE == 0x1337C0DE
TARGET_HASH = 0x1337C0DE
XOR_MASK = 0xDEADBEEF
ADD_CONST = 0xCAFEBABE

# 约束：(key ^ XOR_MASK) + ADD_CONST == TARGET_HASH
constraint = ((key ^ XOR_MASK) + ADD_CONST == TARGET_HASH)

# 将约束添加到求解器
s.add(constraint)

# 4. 求解
print("--- 位向量校验演示 (逆向工程) ---")
print(f"目标校验: (key XOR {hex(XOR_MASK)}) + {hex(ADD_CONST)} = {hex(TARGET_HASH)}")

if s.check() == sat:
    # 5. 输出模型（找到的密钥）
    m = s.model()
    found_key = m[key].as_long()

    # 验证步骤
    check_val = (found_key ^ XOR_MASK) + ADD_CONST

    print("\n结果: 找到满足校验的密钥 (sat)")
    print(f"找到的 32 位密钥: {hex(found_key)}")
    print(f"验证计算结果: {hex(check_val)}")

    if check_val == TARGET_HASH:
        print("验证成功: 密钥正确！")
    else:
        print("验证失败: Z3 求解错误 (通常不会发生)")

else:
    print("\n结果: 无满足条件的密钥 (unsat)")