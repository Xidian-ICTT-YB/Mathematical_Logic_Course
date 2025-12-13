"""
使用 cvc5 的 pythonic 接口求解一个基本的算数问题：
是否存在两个正整数 x、y，满足 2x + y = 20 且 y - x = 0
"""

from cvc5.pythonic import Add, Gt, Int, IntVal, Mult, Solver, Sub, sat


def main():
    solver = Solver()  # 创建求解器

    x, y = Int("x"), Int("y")  # 创建两个整数符号 x、y
    zero, two, twenty = IntVal(0), IntVal(2), IntVal(20)  # 创建三个整数常量 0、2、20

    solver.add(Gt(x, zero))  # x > 0
    solver.add(Gt(y, zero))  # y > 0
    solver.add(Add(Mult(two, x), y) == twenty)  # 2x + y = 20
    solver.add(Sub(y, x) == two)  # y - x = 0

    if solver.check() == sat:
        model = solver.model()  # 用来获取符号的值
        print(f"有解，其中 x = {model[x]}, y = {model[y]}")
    else:
        print("无解")


if __name__ == "__main__":
    main()
