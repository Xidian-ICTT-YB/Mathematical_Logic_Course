from z3 import *

def demo_algebra():
    print("--- Demo 1: 基础代数求解 ---")

    x, y, z = Reals('x y z')

    solver = Solver()

    solver.add(3*x + 2*y - z == 1)
    solver.add(2*x - 2*y + 4*z == -2)
    solver.add(x + y + z == 20)

    if solver.check() == sat:
        print("找到解了！")
        model = solver.model()
        print(f"x = {model[x]}")
        print(f"y = {model[y]}")
        print(f"z = {model[z]}")
    else:
        print("无解 (unsat)")

demo_algebra()