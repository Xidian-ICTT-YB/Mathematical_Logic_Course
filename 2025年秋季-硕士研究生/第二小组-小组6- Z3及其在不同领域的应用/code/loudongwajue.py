from z3 import *

# 创建 32 位 BitVec
len_input = BitVec('len_input', 32)

# 模拟 32 位溢出的 size 计算
size = len_input * 4

solver = Solver()

# 关键：使用 ULT (= unsigned less than)
# 避免 Z3 不同平台的默认行为导致无解
solver.add(size < BitVecVal(400, 32))


# 真实条件：len >= 100 会越界写
solver.add(len_input >= 100)

# 限制输入范围
solver.add(len_input >= 0)

print("求解中...")

if solver.check() == sat:
    model = solver.model()
    evil_len = model[len_input].as_long()
    evil_size = (evil_len * 4) & 0xffffffff

    print("[+] 找到可触发越界写入的恶意输入！")
    print(f"  用户输入 len = {evil_len}")
    print(f"  溢出后的 size = {evil_size}")
    print("  安全检查被绕过，导致越界写入！")

else:
    print("未找到满足条件的输入。")
