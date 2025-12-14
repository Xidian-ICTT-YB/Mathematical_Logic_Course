from z3 import *
import ctypes  # 用于方便地展示 32 位循环位移


def rotate_left_32bit(value, shift):

    shift = shift % 32
    return ((value << shift) & 0xFFFFFFFF) | (value >> (32 - shift))


def solve_malware_key_obfuscation():

    print("---  Z3 SMT 求解器：恶意软件去混淆案例 ---")

    # 1. 初始化求解器
    s = Solver()

    # 2. 定义已知常量和符号变量
    KEY_SIZE = 32
    SHIFT_AMOUNT = 13

    # 已知密文 C (从恶意软件中提取的混淆数据)
    # 例如：0xDEADBEEF (十进制: 3735928559)
    CIPHERTEXT = 0xDEADBEEF
    C = BitVecVal(CIPHERTEXT, KEY_SIZE)

    # 已知目标明文 P (我们预期解密后会得到的字符串 'ABCD' 的 ASCII 值)
    # 0x41424344 (十进制: 1094861636)
    TARGET_PLAINTEXT = 0x41424344
    P = BitVecVal(TARGET_PLAINTEXT, KEY_SIZE)

    # 未知密钥 K (我们想找到的值，使用符号变量表示)
    K = BitVec('K', KEY_SIZE)

    print(f"\n[设定参数]")
    print(f"密文 C (已知): 0x{CIPHERTEXT:08X}")
    print(f"目标明文 P (已知): 0x{TARGET_PLAINTEXT:08X} ('ABCD')")
    print(f"混淆操作: ( (C XOR K) ROL {SHIFT_AMOUNT} ) == P")
    print("--------------------------------------------------")

    # 3. 构造 SMT 约束公式


    # 步骤 1: C XOR K
    Intermediate = C ^ K

    # 步骤 2: ROL 13
    Result = RotateLeft(Intermediate, SHIFT_AMOUNT)

    # 步骤 3: 最终等式约束
    # 要求混淆后的结果 Result 必须等于目标明文 P
    s.add(Result == P)

    # 4. 检查可满足性并求解
    print("正在调用 Z3 求解器...")
    if s.check() == sat:
        # 5. 如果可满足，提取模型 (即 K 的具体值)
        model = s.model()
        key_value = model[K].as_long()

        print("\n✅ 求解成功 (SAT)")
        print(f"恶意软件密钥 K: 0x{key_value:08X} (十进制: {key_value})")

        # --- 6. 验证结果 ---
        print("\n[结果验证]")
        # 验证步骤 1: C XOR K
        verify_intermediate = CIPHERTEXT ^ key_value
        # 验证步骤 2: ROL 13
        verify_result = rotate_left_32bit(verify_intermediate, SHIFT_AMOUNT)

        print(f"使用密钥 K: 0x{key_value:08X} 进行解密...")
        print(f"C XOR K 结果: 0x{verify_intermediate:08X}")
        print(f"(C XOR K) ROL {SHIFT_AMOUNT}: 0x{verify_result:08X}")

        if verify_result == TARGET_PLAINTEXT:
            print("校验通过：求解出的密钥 K 正确地导出了目标明文 P。")
        else:
            print("校验失败：Z3 求解结果与 Python 验证函数不一致。")

    else:
        print("\n❌ 求解失败 (UNSAT): 约束条件无法满足。")


if __name__ == "__main__":
    solve_malware_key_obfuscation()