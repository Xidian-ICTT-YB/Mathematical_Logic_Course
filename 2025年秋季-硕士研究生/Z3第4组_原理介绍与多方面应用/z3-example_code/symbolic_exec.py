# Z3 在软件工程和程序分析领域的核心应用：自动化漏洞挖掘（通过逻辑推理来判断某段代码是否会被执行）
from z3 import *


def run():
    solver = Solver()

    # 定义符号输入
    x, y = Ints('input_x input_y')

    # 模拟待验证的代码逻辑路径：
    # if (x > 100) and (y < 0) and (x + y == 50):
    #     raise Error("Boundary Error")

    # 将路径条件转化为逻辑公式
    path_condition = And(x > 100, y < 0, x + y == 50)

    print(f"待验证路径条件: {path_condition}")
    solver.add(path_condition)

    # 求解
    if solver.check() == sat:
        print("验证结果：路径可达 (存在潜在Bug)")
        model = solver.model()
        val_x = model[x].as_long()
        val_y = model[y].as_long()
        print(f"反例输入: x = {val_x}, y = {val_y}")
        print(f"验算检查: {val_x} + ({val_y}) = {val_x + val_y}")
    else:
        print("验证结果：路径不可达 (代码安全)")


if __name__ == '__main__':
    run()