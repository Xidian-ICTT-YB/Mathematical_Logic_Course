# 用 z3 解决一个结合了密码学的问题（在没有密钥的情况下，利用已知明文推出密钥，并破译密文）
from z3 import *
import time


def run():
    # --- 1. 场景准备 ---
    REAL_SECRET_KEY = 0xDEADBEEF # 原始未知的密钥
    print(f"未知的密钥: {hex(REAL_SECRET_KEY)}")
    plaintext_msg = b"FLAG{Z3_Solver_1s_Turing_Complete}" # 原始的明文
    print(f"原始的明文: {plaintext_msg}")

    # 定义弱加密类
    class WeakStreamCipher:
        def __init__(self, seed):
            self.state = seed & 0xFFFFFFFF # 切去高位，保留32位

        def next_byte(self):
            # LCG（线性同余生成器），生成伪随机数，作为密钥流生成器
            self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
            # LCG算法中，低位非常不随机，高位比较随机，所以这里右移24位，输出高8位
            return (self.state >> 24) & 0xFF

        def encrypt(self, data): # 加密：明文 xor 密钥流 = 密文
            res = bytearray()
            temp = WeakStreamCipher(self.state)
            for b in data: res.append(b ^ temp.next_byte())
            return bytes(res)

    # 生成密文
    cipher = WeakStreamCipher(REAL_SECRET_KEY)
    ciphertext = cipher.encrypt(plaintext_msg)

    print(f"获取的密文: {ciphertext.hex()}")

    # --- 2. 反推密钥流 ---
    known_prefix = b"FLAG"
    print(f"已知的明文: {known_prefix}")

    derived_keystream = []
    for i in range(len(known_prefix)): # 已知的明文 ^ 密文 = 密钥流
        derived_keystream.append(ciphertext[i] ^ known_prefix[i])

    print(f"反推得到的密钥流: {[hex(x) for x in derived_keystream]}")

    # --- 3. Z3 建模 ---
    # 使用位向量专用策略，防止通用求解器卡死
    s = SolverFor("QF_BV")

    # 定义 32位 常量
    A = BitVecVal(1664525, 32)
    C = BitVecVal(1013904223, 32)

    # 定义初始 Seed
    seed = BitVec('seed', 32)
    current_state = seed

    # 已知密钥流和得到密钥流的方式，倒推原始的密钥
    for i, k_val in enumerate(derived_keystream):
        # 状态更新
        current_state = current_state * A + C

        # 提取高8位并约束
        s.add(Extract(31, 24, current_state) == BitVecVal(k_val, 8))

    # --- 4. 求解 ---
    print("\nz3开始求解...")
    start_time = time.time()

    result = s.check()

    elapsed = time.time() - start_time
    print(f"耗时: {elapsed:.4f} 秒")

    if result == sat:
        print("\n破解成功！")
        m = s.model()
        recovered_seed = m[seed].as_long()
        print(f"恢复的密钥: {hex(recovered_seed)}")

        # 验证
        if recovered_seed == REAL_SECRET_KEY:
            print("验证成功！")

        # 解密完整内容
        cracker = WeakStreamCipher(recovered_seed)
        decrypted = cracker.encrypt(ciphertext)
        print(f"完整解密内容: {decrypted}")

    elif result == unsat:
        print("\n无解！")


if __name__ == "__main__":
    run()