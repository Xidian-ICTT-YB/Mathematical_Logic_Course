import cvc5
from cvc5 import Kind
import time


def solve_integer_programming():
    # 初始化cvc5
    tm = cvc5.TermManager() # 创建一个 TermManager对象来统一管理所有逻辑项（Term）的生命周期
    solver = cvc5.Solver(tm) # 使用这个管理器来初始化求解器

    # 设置选项
    solver.setOption("produce-models", "true")
    solver.setOption("produce-unsat-cores", "true")
    solver.setLogic("ALL") # 表示允许使用求解器支持的所有理论

    # 定义整数排序
    intSort = tm.getIntegerSort()

    # 创建变量
    x = tm.mkConst(intSort, 'x') # 创建自由整数变量 x, y, z
    y = tm.mkConst(intSort, 'y')
    z = tm.mkConst(intSort, 'z')

    # 定义常数
    zero = tm.mkInteger(0) # 创建整数常量
    one = tm.mkInteger(1)
    two = tm.mkInteger(2)
    three = tm.mkInteger(3)
    twelve = tm.mkInteger(12)
    fifteen = tm.mkInteger(15)
    ten = tm.mkInteger(10)

    # 添加约束1: x + y + z < 15
    x_add_y_add_z = tm.mkTerm(Kind.ADD, x, y, z)
    constraint1 = tm.mkTerm(Kind.LT, x_add_y_add_z, fifteen)
    solver.assertFormula(constraint1) # 将此约束添加到求解器的上下文

    # 添加约束2: x + 3y + 2z > 10
    three_y = tm.mkTerm(Kind.MULT, y, three)
    two_z = tm.mkTerm(Kind.MULT, z, two)
    x_add_3y_add_2z = tm.mkTerm(Kind.ADD, x, three_y, two_z)
    constraint2 = tm.mkTerm(Kind.GT, x_add_3y_add_2z, ten)
    solver.assertFormula(constraint2)

    # 添加约束3: x, y, z ≥ 0
    constraint3_x = tm.mkTerm(Kind.GEQ, x, zero)
    constraint3_y = tm.mkTerm(Kind.GEQ, y, zero)
    constraint3_z = tm.mkTerm(Kind.GEQ, z, zero)
    solver.assertFormula(constraint3_x)
    solver.assertFormula(constraint3_y)
    solver.assertFormula(constraint3_z)

    # 添加约束4: x + 2y ≤ 12
    two_y = tm.mkTerm(Kind.MULT, y, two)
    x_add_2y = tm.mkTerm(Kind.ADD, x, two_y)
    constraint4 = tm.mkTerm(Kind.LEQ, x_add_2y, twelve)
    solver.assertFormula(constraint4)

    # 添加约束5: 2x - z ≥ 1
    two_x = tm.mkTerm(Kind.MULT, x, two)
    two_x_sub_z = tm.mkTerm(Kind.SUB, two_x, z)
    constraint5 = tm.mkTerm(Kind.GEQ, two_x_sub_z, one)
    solver.assertFormula(constraint5)

    # 定义目标函数: f = x² + y² + z²
    x_sq = tm.mkTerm(Kind.MULT, x, x)
    y_sq = tm.mkTerm(Kind.MULT, y, y)
    z_sq = tm.mkTerm(Kind.MULT, z, z)
    target_func = tm.mkTerm(Kind.ADD, x_sq, y_sq, z_sq)

    # 使用二分搜索找到最小目标函数值
    print("使用二分搜索寻找最小目标函数值...")

    # 确定搜索范围
    low, high = 0, 500
    best_solution = None
    best_value = float('inf')
    # 使用二分搜索找到最小目标函数值
    while low <= high:
        mid = (low + high) // 2
        print(f"尝试目标值: {mid}")

        # 临时约束：目标函数 ≤ mid
        temp_constraint = tm.mkTerm(Kind.LEQ, target_func, tm.mkInteger(mid))

        # 保存当前状态并添加临时约束
        solver.push() # 在添加临时约束前，保存当前求解器的全部状态（即之前的所有约束）
        solver.assertFormula(temp_constraint)

        # 检查可满足性
        result = solver.checkSat()

        if result.isSat():
            # 找到可行解，尝试更小的目标值
            x_val = solver.getValue(x) # 如果可满足，则获取模型中每个变量的具体赋值
            y_val = solver.getValue(y)
            z_val = solver.getValue(z)
            f_val = solver.getValue(target_func)

            # 转换为Python整数
            x_int = int(str(x_val))
            y_int = int(str(y_val))
            z_int = int(str(z_val))
            f_int = int(str(f_val))

            print(f"找到可行解: x={x_int}, y={y_int}, z={z_int}, f={f_int}") # 更新可行解

            if f_int < best_value:
                best_value = f_int
                best_solution = (x_int, y_int, z_int, f_int)
                print(f"当前最优解: f={best_value}")

            high = mid - 1  # 说明最优值可能更小，应在左半区间继续搜索
        else:
            # 不可行，尝试更大的目标值
            low = mid + 1 # 说明最优值可能更大，应在右半区间继续搜索

        # 恢复状态，移除临时约束
        solver.pop() # 撤销最近一次的push，进入下一次循环，添加更新上下界后的约束

    # 输出最终结果
    if best_solution:
        x, y, z, f = best_solution
        print("\n" + "=" * 50)
        print("最优解找到!")
        print(f"x = {x}, y = {y}, z = {z}")
        print(f"目标函数最小值: f = {f}")
        print(f"验证约束:")
        print(f"x + y + z = {x + y + z} < 15: {x + y + z < 15}")
        print(f"x + 3y + 2z = {x + 3 * y + 2 * z} > 10: {x + 3 * y + 2 * z > 10}")
        print(f"x + 2y = {x + 2 * y} ≤ 12: {x + 2 * y <= 12}")
        print(f"2x - z = {2 * x - z} ≥ 1: {2 * x - z >= 1}")
        print("=" * 50)
    else:
        print("未找到可行解!")

    return best_solution


# 运行求解
if __name__ == "__main__":
    start_time = time.time()
    solution = solve_integer_programming()
    end_time = time.time()
    print(f"总运行时间: {end_time - start_time:.2f}秒")