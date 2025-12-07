# Z3 在形式化验证领域的一个极其经典且具有深度的应用：浮点数运算不满足结合律
from z3 import *


def run():
    # 1. 定义 32位 浮点数变量 (IEEE 754：1位符号，8位指数，23位尾数)
    x = FP('x', Float32())
    y = FP('y', Float32())
    z = FP('z', Float32())

    # 2. 设定舍入模式 (向最接近的偶数舍入)
    rm = RNE()

    # 3. 定义结合律公式
    # lhs: (x + y) + z
    lhs = fpAdd(rm, fpAdd(rm, x, y), z)
    # rhs: x + (y + z)
    rhs = fpAdd(rm, x, fpAdd(rm, y, z))

    solver = Solver()

    # 4. 寻找反例：让 lhs != rhs
    # 排除掉 NaN 和 Infinity 这种特殊情况
    solver.add(lhs != rhs)
    solver.add(Not(fpIsNaN(x)), Not(fpIsNaN(y)), Not(fpIsNaN(z)))
    solver.add(Not(fpIsInf(x)), Not(fpIsInf(y)), Not(fpIsInf(z)))

    print("验证 32 位浮点数的结合律")
    if solver.check() == sat:
        print("验证结果：计算机中 32 位浮点数的结合律不成立！")
        print("反例如下")
        m = solver.model()
        # 获取具体的浮点数值
        vx = m[x]
        vy = m[y]
        vz = m[z]
        print(f"    x = {vx}")
        print(f"    y = {vy}")
        print(f"    z = {vz}")
    else:
        print("未找到反例！")


if __name__ == "__main__":
    run()