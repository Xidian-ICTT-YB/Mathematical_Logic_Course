# Z3 在运筹学和人工智能领域的一个经典应用：约束满足问题（任务调度）
from z3 import *


def run():
    solver = Solver()

    # 1. 定义变量：4个任务 (Task A, B, C, D) 对应的时刻
    # 使用 Int 整数类型
    t_a, t_b, t_c, t_d = Ints('Task_A Task_B Task_C Task_D')

    # 2. 设置定义域约束
    # 假设时间槽为 1 到 4
    tasks = [t_a, t_b, t_c, t_d]
    for t in tasks:
        solver.add(t >= 1, t <= 4)

    # 3. 设置系统约束
    # 约束 A: 同一时刻只能做一个任务
    solver.add(Distinct(tasks))

    # 约束 B: 时序逻辑
    solver.add(t_c > t_a)  # C 必须在 A 之后
    solver.add(t_b != 4)  # B 不能安排在最后
    solver.add(t_d == t_a + 1)  # D 必须紧接在 A 之后

    # 4. 求解与结果分析
    if solver.check() == sat:
        model = solver.model()
        print("求解成功！最优调度方案如下：")
        results = sorted(
            [(model[t].as_long(), name) for t, name in zip(tasks, ['Task A', 'Task B', 'Task C', 'Task D'])])
        for time_slot, name in results:
            print(f"  时间片 {time_slot}: {name}")
    else:
        print("无解！")


if __name__ == '__main__':
    run()