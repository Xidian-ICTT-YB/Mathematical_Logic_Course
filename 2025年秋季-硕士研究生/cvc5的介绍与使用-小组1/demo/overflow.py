"""
使用 cvc5 的 pythonic 接口求解一个位向量溢出问题：
是否存在一个宽度为 8 的位向量 x，其加 1 后产生溢出。
"""

from cvc5.pythonic import ULT, BitVec, BitVecVal, BVAdd, Solver, sat


def main():
    solver = Solver()  # 创建求解器

    x = BitVec("x", 8)  # 创建一个位长为 8 的位向量符号 x
    one = BitVecVal(1, 8)  # 创建一个值为 1 的 8 位位向量

    # x + 1 u< x
    solver.add(ULT(BVAdd(x, one), x))

    if solver.check() == sat:
        model = solver.model()  # 用于获取符号的值
        print("有解，x =", bin(int(str(model[x]))))
    else:
        print("无解")


if __name__ == "__main__":
    main()
