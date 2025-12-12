#!/usr/bin/env python3
"""
11. 图着色问题 - 组合优化经典问题

演示内容：
1. 图着色基础概念
2. 3-着色问题求解
4. 寻找最小着色数（色数）


"""

from cvc5.pythonic import *
import time


def print_graph(edges, num_nodes):
    """打印图的邻接信息"""
    print("图结构（边列表）：")
    for i, j in edges:
        print(f"  {i} -- {j}")
    print()


def example_simple_3_coloring():
    """简单的 3-着色问题"""
    print("=" * 60)
    print("示例 1：简单图的 3-着色")
    print("=" * 60)
    print()

    # 图：三角形 + 一个额外顶点
    #    0
    #   / \
    #  1---2
    #   \ /
    #    3

    edges = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]
    num_nodes = 4

    print_graph(edges, num_nodes)

    # 创建变量：每个节点的颜色 (1, 2, 3)
    colors = [Int(f'c{i}') for i in range(num_nodes)]

    solver = Solver()

    # 约束 1：每个节点颜色在 1-3 之间
    for i in range(num_nodes):
        solver.add(colors[i] >= 1, colors[i] <= 3)

    # 约束 2：相邻节点颜色不同
    for i, j in edges:
        solver.add(colors[i] != colors[j])

    print("约束：")
    print("  - 每个节点颜色 ∈ {1, 2, 3}")
    print("  - 相邻节点颜色不同")
    print()

    result = solver.check()
    print(f"结果: {result}")
    print()

    if result == sat:
        model = solver.model()
        coloring = [model[colors[i]].as_long() for i in range(num_nodes)]

        print("找到 3-着色方案：")
        for i in range(num_nodes):
            print(f"  节点 {i}: 颜色 {coloring[i]}")
        print()

        # 验证
        print("验证边的约束：")
        valid = True
        for i, j in edges:
            if coloring[i] == coloring[j]:
                print(f"  节点 {i} 和 {j}: 颜色冲突！")
                valid = False
            else:
                print(f"  节点 {i} (颜色 {coloring[i]}) -- 节点 {j} (颜色 {coloring[j]}) ✓")

        if valid:
            print()
            print("✓ 着色方案有效")
    print()


def example_chromatic_number():
    """寻找色数（最小着色数）"""
    print("=" * 60)
    print("示例 2：寻找色数")
    print("=" * 60)
    print()

    # 完全图 K4（4 个节点两两相连）
    # 色数应该是 4
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    num_nodes = 4

    print("图：完全图 K4（4 个节点两两相连）")
    print_graph(edges, num_nodes)

    # 尝试用 k 种颜色着色
    for k in range(1, num_nodes + 1):
        print(f"尝试用 {k} 种颜色着色...")

        colors = [Int(f'c{i}') for i in range(num_nodes)]
        solver = Solver()

        # 域约束
        for i in range(num_nodes):
            solver.add(colors[i] >= 1, colors[i] <= k)

        # 边约束
        for i, j in edges:
            solver.add(colors[i] != colors[j])

        result = solver.check()

        if result == sat:
            print(f"  结果: SAT - 可以用 {k} 种颜色")

            model = solver.model()
            coloring = [model[colors[i]].as_long() for i in range(num_nodes)]

            print(f"  方案: ", end="")
            for i in range(num_nodes):
                print(f"节点{i}=颜色{coloring[i]}", end=" ")
            print()
            print()

            print(f"结论：色数 χ(G) = {k}")
            break
        else:
            print(f"  结果: UNSAT - {k} 种颜色不够")
    print()


def example_course_scheduling():
    """实际应用：课程排课"""
    print("=" * 60)
    print("示例 3：课程排课问题")
    print("=" * 60)
    print()

    # 6 门课程
    courses = ["数学", "物理", "化学", "英语", "体育", "历史"]
    num_courses = len(courses)

    # 冲突关系（有共同学生的课程不能同时上）
    conflicts = [
        (0, 1),  # 数学 vs 物理
        (0, 2),  # 数学 vs 化学
        (1, 2),  # 物理 vs 化学
        (3, 4),  # 英语 vs 体育
        (0, 3),  # 数学 vs 英语
        (1, 4),  # 物理 vs 体育
    ]

    print("课程列表：")
    for i, course in enumerate(courses):
        print(f"  {i}: {course}")
    print()

    print("冲突关系（有共同学生）：")
    for i, j in conflicts:
        print(f"  {courses[i]} vs {courses[j]}")
    print()

    # 尝试用最少的时间槽
    for num_slots in range(1, num_courses + 1):
        print(f"尝试分配到 {num_slots} 个时间槽...")

        slots = [Int(f'slot{i}') for i in range(num_courses)]
        solver = Solver()

        # 域约束：每门课分配到 1 到 num_slots 的时间槽
        for i in range(num_courses):
            solver.add(slots[i] >= 1, slots[i] <= num_slots)

        # 冲突约束：有冲突的课程不能在同一时间槽
        for i, j in conflicts:
            solver.add(slots[i] != slots[j])

        result = solver.check()

        if result == sat:
            model = solver.model()
            schedule = [model[slots[i]].as_long() for i in range(num_courses)]

            print(f"  结果: SAT - 可以用 {num_slots} 个时间槽")
            print()
            print("  排课方案：")

            # 按时间槽分组
            for slot in range(1, num_slots + 1):
                courses_in_slot = [courses[i] for i in range(num_courses) if schedule[i] == slot]
                if courses_in_slot:
                    print(f"    时间槽 {slot}: {', '.join(courses_in_slot)}")

            print()
            print(f"  最少需要 {num_slots} 个时间槽")
            break
        else:
            print(f"  结果: UNSAT - {num_slots} 个时间槽不够")

    print()


def example_map_coloring():
    """地图着色问题"""
    print("=" * 60)
    print("示例 4：地图着色（四色定理）")
    print("=" * 60)
    print()

    # 简化的中国部分省份地图（相邻关系）
    provinces = ["陕西", "甘肃", "四川", "重庆", "湖北", "河南"]
    num_provinces = len(provinces)

    # 相邻关系
    borders = [
        (0, 1),  # 陕西-甘肃
        (0, 2),  # 陕西-四川
        (0, 3),  # 陕西-重庆
        (0, 4),  # 陕西-湖北
        (0, 5),  # 陕西-河南
        (1, 2),  # 甘肃-四川
        (2, 3),  # 四川-重庆
        (3, 4),  # 重庆-湖北
        (4, 5),  # 湖北-河南
    ]

    print("省份列表：")
    for i, province in enumerate(provinces):
        print(f"  {i}: {province}")
    print()

    print("相邻关系：")
    for i, j in borders:
        print(f"  {provinces[i]} -- {provinces[j]}")
    print()

    # 尝试 4-着色
    k = 4
    print(f"尝试用 {k} 种颜色给地图着色...")
    print()

    colors = [Int(f'c{i}') for i in range(num_provinces)]
    solver = Solver()

    # 域约束
    for i in range(num_provinces):
        solver.add(colors[i] >= 1, colors[i] <= k)

    # 边界约束
    for i, j in borders:
        solver.add(colors[i] != colors[j])

    start = time.time()
    result = solver.check()
    elapsed = time.time() - start

    print(f"结果: {result}")
    print(f"耗时: {elapsed:.6f} 秒")
    print()

    if result == sat:
        model = solver.model()
        coloring = [model[colors[i]].as_long() for i in range(num_provinces)]

        print("着色方案：")
        color_names = ["", "红色", "蓝色", "绿色", "黄色"]
        for i in range(num_provinces):
            print(f"  {provinces[i]}: {color_names[coloring[i]]}")

        print()
        print("验证：相邻省份颜色不同 ✓")
    print()


def main():
    """主函数"""
    print()
    print("=" * 60)
    print("图着色问题：组合优化经典案例")
    print("=" * 60)
    print()

    start_time = time.time()

    example_simple_3_coloring()
    example_chromatic_number()
    example_course_scheduling()
    example_map_coloring()

    elapsed = time.time() - start_time

    print(f"总耗时: {elapsed:.3f} 秒")
    print()


if __name__ == "__main__":
    main()
