# Z3 在 程序合成领域的一个基础但极具代表性的应用：基于范例的归纳合成（只看输入输出，写出代码逻辑）
from z3 import *


def run():
    # 1. 定义 IO 样例 (Spec)
    examples = [
        (2, 5),  # f(2) = 5
        (4, 11),  # f(4) = 11
        (10, 29)  # f(10) = 29
    ]
    print(f"观察到的样例: {examples}")

    # 2. 定义程序模板
    # 假设是一个线性函数: f(x) = a * x + b
    # 目标是求出系数 a 和 b
    a = Int('coeff_a')
    b = Int('coeff_b')

    solver = Solver()

    # 3. 为每个样例添加约束
    for val_in, val_out in examples:
        solver.add(a * val_in + b == val_out)

    if solver.check() == sat:
        m = solver.model()
        res_a = m[a].as_long()
        res_b = m[b].as_long()
        print(f"推导出的函数逻辑为: f(x) = {res_a} * x + {res_b}")
    else:
        print("合成失败：现有模板无法拟合给定数据。")


if __name__ == "__main__":
    run()