#!/usr/bin/env python3
"""
通用辅助函数模块

提供各种辅助功能：
- 时间测量
- 模型解析
- 结果格式化
- 文件 I/O 辅助

西安电子科技大学 数学逻辑课程
"""

import time
from contextlib import contextmanager
from typing import Any, Dict, List


@contextmanager
def timer(name="操作"):
    """
    计时上下文管理器

    使用示例：
        with timer("求解"):
            result = solver.check()
    """
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"[{name}] 耗时: {elapsed:.6f} 秒")


def format_time(seconds: float) -> str:
    """
    格式化时间输出

    参数：
        seconds: 秒数

    返回：
        格式化的时间字符串
    """
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f} μs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.3f} s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.2f}s"


def parse_model(model, variables: List) -> Dict[str, Any]:
    """
    解析模型为字典

    参数：
        model: cvc5 模型
        variables: 变量列表

    返回：
        变量名到值的字典
    """
    result = {}
    for var in variables:
        var_name = str(var)
        try:
            val = model[var]
            # 尝试转换为 Python 原生类型
            if hasattr(val, 'as_long'):
                result[var_name] = val.as_long()
            elif hasattr(val, 'as_fraction'):
                result[var_name] = str(val)
            else:
                result[var_name] = str(val)
        except:
            result[var_name] = None
    return result


def print_model(model, variables: List, title="模型"):
    """
    格式化打印模型

    参数：
        model: cvc5 模型
        variables: 变量列表
        title: 标题
    """
    print(f"\n{title}:")
    parsed = parse_model(model, variables)
    for var_name, val in parsed.items():
        print(f"  {var_name} = {val}")
    print()


def print_separator(char="=", length=60, title=None):
    """
    打印分隔线

    参数：
        char: 分隔符字符
        length: 长度
        title: 标题（可选）
    """
    if title:
        print(f"\n{char * length}")
        print(f"{title:^{length}}")
        print(f"{char * length}\n")
    else:
        print(f"{char * length}")


def print_result(result, details=None):
    """
    格式化打印求解结果

    参数：
        result: 求解结果 (sat/unsat/unknown)
        details: 额外详情（可选）
    """
    result_map = {
        'sat': '✓ 可满足 (SAT)',
        'unsat': '✗ 不可满足 (UNSAT)',
        'unknown': '? 未知 (UNKNOWN)'
    }

    result_str = str(result)
    display = result_map.get(result_str, result_str)

    print(f"求解结果: {display}")

    if details:
        print(f"详情: {details}")


def compare_solvers(solvers_dict: Dict[str, float]):
    """
    对比多个求解器的性能

    参数：
        solvers_dict: 求解器名称到时间的字典

    示例：
        compare_solvers({
            "策略 A": 0.123,
            "策略 B": 0.089,
            "策略 C": 0.156
        })
    """
    print("\n性能对比:")
    print(f"{'策略':<20} {'时间':<15} {'相对速度':<10}")
    print("-" * 50)

    # 找出最快的
    fastest_time = min(solvers_dict.values())

    for name, elapsed in sorted(solvers_dict.items(), key=lambda x: x[1]):
        relative = elapsed / fastest_time
        time_str = format_time(elapsed)
        print(f"{name:<20} {time_str:<15} {relative:.2f}x")

    print()


def verify_solution(solver, model, constraints: List, variables: List) -> bool:
    """
    验证解是否满足所有约束

    参数：
        solver: 求解器
        model: 模型
        constraints: 约束列表
        variables: 变量列表

    返回：
        True 如果所有约束都满足
    """
    print("验证解的正确性...")

    all_satisfied = True
    for i, constraint in enumerate(constraints, 1):
        try:
            val = model.eval(constraint)
            is_true = str(val) == "True"

            if is_true:
                print(f"  约束 {i}: ✓ 满足")
            else:
                print(f"  约束 {i}: ✗ 不满足")
                all_satisfied = False
        except Exception as e:
            print(f"  约束 {i}: ? 无法验证 ({e})")
            all_satisfied = False

    return all_satisfied


def count_solutions(solver, variables: List, max_count=100) -> int:
    """
    枚举并计数所有解（最多 max_count 个）

    参数：
        solver: 求解器
        variables: 变量列表
        max_count: 最多枚举的解数

    返回：
        找到的解的数量
    """
    from cvc5.pythonic import Or

    count = 0
    print(f"枚举解（最多 {max_count} 个）...")

    while solver.check() == 'sat' and count < max_count:
        model = solver.model()
        count += 1

        # 打印这个解
        parsed = parse_model(model, variables)
        print(f"  解 {count}: {parsed}")

        # 排除这个解
        exclusion = []
        for var in variables:
            val = model[var]
            exclusion.append(var != val)

        solver.add(Or(*exclusion))

    if count >= max_count:
        print(f"已达到最大枚举数 {max_count}，可能还有更多解")

    return count


def save_results(filename: str, data: Dict):
    """
    保存结果到 JSON 文件

    参数：
        filename: 文件名
        data: 数据字典
    """
    import json

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"结果已保存到: {filename}")


def load_results(filename: str) -> Dict:
    """
    从 JSON 文件加载结果

    参数：
        filename: 文件名

    返回：
        数据字典
    """
    import json

    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


def benchmark(func, *args, runs=10, **kwargs):
    """
    对函数进行基准测试

    参数：
        func: 要测试的函数
        args: 位置参数
        runs: 运行次数
        kwargs: 关键字参数

    返回：
        (平均时间, 标准差)
    """
    import statistics

    times = []
    print(f"基准测试 {func.__name__}（{runs} 次运行）...")

    for i in range(runs):
        start = time.time()
        func(*args, **kwargs)
        elapsed = time.time() - start
        times.append(elapsed)

    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if runs > 1 else 0

    print(f"  平均时间: {format_time(avg_time)}")
    print(f"  标准差: {format_time(std_dev)}")

    return avg_time, std_dev


if __name__ == "__main__":
    # 测试代码
    print("通用辅助函数模块测试")
    print("=" * 60)

    # 测试时间格式化
    print("\n时间格式化测试:")
    print(f"  0.0000005 秒 = {format_time(0.0000005)}")
    print(f"  0.0005 秒 = {format_time(0.0005)}")
    print(f"  0.5 秒 = {format_time(0.5)}")
    print(f"  65.5 秒 = {format_time(65.5)}")

    # 测试分隔符
    print_separator(title="测试标题")

    # 测试计时器
    print("\n计时器测试:")
    with timer("睡眠 0.1 秒"):
        time.sleep(0.1)

    # 测试性能对比
    compare_solvers({
        "策略 A": 0.123,
        "策略 B": 0.089,
        "策略 C": 0.156
    })

    print("\n所有测试完成！")
