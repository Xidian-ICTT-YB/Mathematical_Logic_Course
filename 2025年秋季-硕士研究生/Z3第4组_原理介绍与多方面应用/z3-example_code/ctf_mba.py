# Z3 在二进制安全和形式化验证领域的一个经典应用：等价性证明

from z3 import *


def run():
    # 定义 32位 寄存器
    x = BitVec('eax', 32)
    y = BitVec('ebx', 32)

    # 1. 原始的简单逻辑 (Spec)
    # 汇编: add eax, ebx
    simple_expr = x + y

    # 2. 混淆后的复杂逻辑 (Obfuscated)
    # 这是一个经典的 MBA 恒等式：x + y = (x ^ y) + 2 * (x & y)
    # 汇编：
    #   mov ecx, eax    （备份 eax）
    #   xor ecx, ebx    （计算本位和）
    #   and eax, ebx    （计算进位）
    #   shl eax, 1      （左移，即 *2）
    #   add eax, ecx    （本位 + 进位）
    obfuscated_expr = (x ^ y) + 2 * (x & y)

    print(f"待证明公式: (x + y) == (x ^ y) + 2 * (x & y)")

    # 3. 构造证明（反证法）
    solver = Solver()
    solver.add(simple_expr != obfuscated_expr)

    result = solver.check()

    if result == unsat:
        print("未找到反例！")
        print("结论: (x + y) == (x ^ y) + 2 * (x & y) 等式成立！")
    else:
        print("找到反例！")
        print(solver.model())
        print("结论: (x + y) == (x ^ y) + 2 * (x & y) 等式不成立！")


if __name__ == "__main__":
    run()