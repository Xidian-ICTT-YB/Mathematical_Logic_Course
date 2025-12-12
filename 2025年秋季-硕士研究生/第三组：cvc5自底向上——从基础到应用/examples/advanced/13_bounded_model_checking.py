#!/usr/bin/env python3
"""
cvc5 高级应用：有界模型检查（Bounded Model Checking, BMC）
================================================================

什么是有界模型检查（BMC）？
    BMC 是一种形式化验证技术，用于验证系统是否满足某些性质。
    "有界"指的是在有限步数（k步）内检查性质是否被违反。

核心思想：
    1. 将系统建模为符号转换系统（Symbolic Transition System）
    2. 定义初始状态 I 和转换关系 T
    3. 定义要验证的性质 P（不变量）
    4. 展开系统 k 步，检查是否存在违反性质的执行路径
"""

from cvc5.pythonic import *
import time


def traffic_light_bmc():
    """
    示例 1：交通灯系统的有界模型检查

    系统建模：
        状态：Red, Yellow, Green
        转换：Red → Green → Yellow → Red
        性质：永远不会从 Red 直接跳到 Yellow

    我们将用 BMC 验证这个性质
    """

    print("=" * 70)
    print("示例 1：交通灯系统的有界模型检查")
    print("=" * 70)
    print()

    print("📌 系统描述：")
    print("   状态：Red (0), Green (1), Yellow (2)")
    print("   转换：Red → Green → Yellow → Red")
    print()

    print("📌 要验证的性质（不变量）：")
    print("   \"永远不会从 Red 直接转换到 Yellow\"")
    print()

    # 定义常量
    RED = 0
    GREEN = 1
    YELLOW = 2

    # 设置检查的步数
    K = 10

    print(f"📌 有界模型检查参数：k = {K} 步")
    print()

    # 创建求解器
    solver = Solver()

    # 创建状态变量序列 s[0], s[1], ..., s[k]
    states = [Int(f's_{i}') for i in range(K + 1)]

    # 约束 1：初始状态为 Red
    solver.add(states[0] == RED)

    print("🔧 构建 BMC 公式...")
    print()

    # 约束 2：转换关系
    # s'（下一状态）的定义
    def transition(s_current, s_next):
        """
        定义状态转换关系
        Red → Green → Yellow → Red
        """
        return Or(
            And(s_current == RED, s_next == GREEN),      # Red 转 Green
            And(s_current == GREEN, s_next == YELLOW),   # Green 转 Yellow
            And(s_current == YELLOW, s_next == RED)      # Yellow 转 Red
        )

    # 添加所有转换约束
    for i in range(K):
        solver.add(transition(states[i], states[i + 1]))

    print(f"   ✓ 添加初始状态约束：s[0] = Red")
    print(f"   ✓ 添加 {K} 个转换关系约束")
    print()

    # 约束 3：性质的否定（寻找反例）
    # 性质：永远不会从 Red 直接到 Yellow
    # 否定：存在某一步从 Red 到 Yellow
    property_violations = []
    for i in range(K):
        # 检查是否存在 Red → Yellow 的转换
        violation = And(states[i] == RED, states[i + 1] == YELLOW)
        property_violations.append(violation)

    # 如果任何一步违反性质，就是反例
    solver.add(Or(*property_violations))

    print("   ✓ 添加性质的否定（寻找反例）")
    print()

    # 求解
    print("🚀 开始检查...")
    start_time = time.time()
    result = solver.check()
    elapsed = time.time() - start_time

    print(f"⏱️  检查时间：{elapsed:.6f} 秒")
    print()

    # 分析结果
    if result == sat:
        print("❌ 性质被违反！找到反例：")
        model = solver.model()

        print()
        print("   执行路径：")
        state_names = ["Red", "Green", "Yellow"]
        for i in range(K + 1):
            state_val = model[states[i]].as_long()
            print(f"   步骤 {i}: {state_names[state_val]}")

        print()
        print("💡 这说明系统设计有问题，存在 Red → Yellow 的转换")
    else:
        print("✅ 性质成立！")
        print(f"   在 {K} 步内，系统不会从 Red 直接跳到 Yellow")
        print()
        print("💡 这验证了交通灯系统的正确性")

    print()


def counter_bmc():
    """
    示例 2：计数器的有界模型检查

    系统：一个简单的计数器
    - 初始值：0
    - 操作：每步 +1 或 +2
    - 性质：计数器值永远 <= 20

    BMC 验证：在 15 步内是否可能超过 20
    """

    print("=" * 70)
    print("示例 2：计数器系统的有界模型检查")
    print("=" * 70)
    print()

    print("📌 系统描述：")
    print("   初始值：counter = 0")
    print("   操作：每步 counter += 1 或 counter += 2")
    print()

    print("📌 要验证的性质：")
    print("   \"计数器值永远不超过 20\"")
    print()

    K = 15
    print(f"📌 有界模型检查参数：k = {K} 步")
    print()

    solver = Solver()

    # 创建计数器状态序列
    counters = [Int(f'counter_{i}') for i in range(K + 1)]

    # 初始状态
    solver.add(counters[0] == 0)

    # 转换关系：每步 +1 或 +2
    for i in range(K):
        solver.add(
            Or(
                counters[i + 1] == counters[i] + 1,
                counters[i + 1] == counters[i] + 2
            )
        )

    print("🔧 构建 BMC 公式...")
    print(f"   ✓ 初始状态：counter[0] = 0")
    print(f"   ✓ 转换关系：counter[i+1] = counter[i] + 1 或 +2")
    print()

    # 性质的否定：存在某一步 counter > 20
    violations = []
    for i in range(K + 1):
        violations.append(counters[i] > 20)

    solver.add(Or(*violations))

    print("   ✓ 寻找性质违反：counter > 20")
    print()

    print("🚀 开始检查...")
    result = solver.check()

    if result == sat:
        model = solver.model()
        print("❌ 性质被违反！反例：")
        print()
        print("   执行路径：")

        for i in range(K + 1):
            val = model[counters[i]].as_long()
            marker = " ← 违反性质！" if val > 20 else ""
            print(f"   步骤 {i:2d}: counter = {val:2d}{marker}")

            if i < K:
                next_val = model[counters[i + 1]].as_long()
                increment = next_val - val
                print(f"            ↓ +{increment}")

        print()
        print(f"💡 在第 {[i for i in range(K+1) if model[counters[i]].as_long() > 20][0]} 步违反性质")
    else:
        print(f"✅ 性质成立！在 {K} 步内，counter 不会超过 20")

    print()


def adder_verification():
    """
    示例 3：硬件加法器的正确性验证

    验证一个 4 位加法器的正确性：
        输入：a (4位), b (4位)
        输出：sum (4位), carry (进位)
        性质：sum + carry*16 == a + b（考虑进位）
    """

    print("=" * 70)
    print("示例 3：4 位加法器的正确性验证")
    print("=" * 70)
    print()

    print("📌 硬件描述：")
    print("   输入：a (4位), b (4位)")
    print("   输出：sum (4位), carry_out (1位)")
    print()

    print("📌 要验证的性质：")
    print("   \"sum + carry_out×16 == a + b\"")
    print()

    # 使用位向量理论（更适合硬件）
    # 注意：这里我们用整数简化，实际硬件验证会用 BitVec

    solver = Solver()

    # 输入
    a = Int('a')
    b = Int('b')

    # 输出
    sum_out = Int('sum')
    carry_out = Int('carry')

    # 约束：输入范围 0-15（4位）
    solver.add(a >= 0, a < 16)
    solver.add(b >= 0, b < 16)

    # 约束：输出范围
    solver.add(sum_out >= 0, sum_out < 16)
    solver.add(carry_out >= 0, carry_out <= 1)

    # 加法器的行为定义
    solver.add(sum_out == (a + b) % 16)
    solver.add(carry_out == If(a + b >= 16, 1, 0))

    print("🔧 构建验证公式...")
    print("   ✓ 定义输入范围（4位）")
    print("   ✓ 定义加法器行为")
    print()

    # 性质：正确性
    # 检查是否存在反例：sum + carry*16 != a + b
    property_holds = (sum_out + carry_out * 16 == a + b)
    solver.add(Not(property_holds))

    print("   ✓ 检查性质的否定（寻找反例）")
    print()

    print("🚀 开始验证...")
    result = solver.check()

    if result == sat:
        model = solver.model()
        a_val = model[a].as_long()
        b_val = model[b].as_long()
        sum_val = model[sum_out].as_long()
        carry_val = model[carry_out].as_long()

        print("❌ 加法器实现有误！反例：")
        print(f"   输入：a = {a_val}, b = {b_val}")
        print(f"   输出：sum = {sum_val}, carry = {carry_val}")
        print(f"   期望：{a_val + b_val}")
        print(f"   实际：{sum_val + carry_val * 16}")
    else:
        print("✅ 加法器正确！")
        print("   对于所有 4 位输入，加法器都能产生正确的结果")
        print()
        print("💡 这是形式化验证的威力：")
        print("   - 不需要测试所有 256×256 = 65536 种组合")
        print("   - SMT 求解器自动检查所有可能性")
        print("   - 提供数学级别的正确性保证")

    print()


def main():
    """主函数"""

    # 示例 1：交通灯系统
    traffic_light_bmc()

    # 示例 2：计数器系统
    counter_bmc()

    # 示例 3：加法器验证
    adder_verification()

if __name__ == "__main__":
    main()
