"""
使用 cvc5 的 pythonic 接口执行定理证明：
已知整数 x > 5，证明 2x > 10。
"""

from cvc5.pythonic import Gt, Int, IntVal, Mult, Not, Solver, sat


def main():
    solver = Solver()  # 创建求解器

    x = Int("x")  # 创建一个整形符号 x
    two, five, ten = IntVal(2), IntVal(5), IntVal(10)  # 创建三个整形常量 2、5、10

    solver.add(Gt(x, five))  # x > 5

    conclusion = Gt(Mult(two, x), ten)  # 2x > 10

    # 验证 (x > 5) && !(2x > 10) 是否可满足
    solver.add(Not(conclusion))

    if solver.check() == sat:
        print("有解，定理不成立")
    else:
        print("无解，定理成立")


if __name__ == "__main__":
    main()
