#!/usr/bin/env python3
"""
可视化工具模块

提供各种可视化功能：
- 数独网格显示
- N 皇后棋盘显示
- 图着色可视化
- 性能对比图表

西安电子科技大学 数学逻辑课程
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


def print_sudoku(grid, title="数独"):
    """
    打印数独网格（文本形式）

    参数：
        grid: 9x9 的二维列表
        title: 标题
    """
    print(f"\n{'='*37}")
    print(f"  {title}")
    print(f"{'='*37}\n")

    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("  " + "-" * 33)

        row_str = "  "
        for j in range(9):
            if j % 3 == 0 and j != 0:
                row_str += "| "

            cell = grid[i][j]
            if cell == 0:
                row_str += "· "
            else:
                row_str += str(cell) + " "

        print(row_str)
    print()


def plot_sudoku(grid, filename=None, title="Sudoku"):
    """
    绘制数独网格（图形形式）

    参数：
        grid: 9x9 的二维列表
        filename: 保存文件名（可选）
        title: 标题
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # 绘制网格线
    for i in range(10):
        linewidth = 3 if i % 3 == 0 else 0.5
        ax.plot([0, 9], [i, i], 'k-', linewidth=linewidth)
        ax.plot([i, i], [0, 9], 'k-', linewidth=linewidth)

    # 填充数字
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                ax.text(j + 0.5, 8.5 - i, str(grid[i][j]),
                       ha='center', va='center', fontsize=20)

    ax.set_xlim(0, 9)
    ax.set_ylim(0, 9)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=16, pad=20)

    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"已保存图片: {filename}")

    plt.show()


def print_chess(solution, n, title="N 皇后"):
    """
    打印 N 皇后棋盘（文本形式）

    参数：
        solution: 长度为 n 的列表，solution[i] 表示第 i 行皇后的列位置
        n: 棋盘大小
        title: 标题
    """
    print(f"\n{title} (N={n})")
    print("  " + "─" * (n * 2 + 1))

    for i in range(n):
        row = "  │"
        for j in range(n):
            if solution[i] == j:
                row += "♛ "
            else:
                row += "· "
        row += "│"
        print(row)

    print("  " + "─" * (n * 2 + 1))
    print()


def plot_queens(solution, n, filename=None, title="N-Queens"):
    """
    绘制 N 皇后棋盘（图形形式）

    参数：
        solution: 长度为 n 的列表
        n: 棋盘大小
        filename: 保存文件名（可选）
        title: 标题
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # 绘制棋盘
    for i in range(n):
        for j in range(n):
            color = 'lightgray' if (i + j) % 2 == 0 else 'white'
            rect = patches.Rectangle((j, n - 1 - i), 1, 1,
                                     linewidth=1, edgecolor='black',
                                     facecolor=color)
            ax.add_patch(rect)

            # 放置皇后
            if solution[i] == j:
                ax.text(j + 0.5, n - 0.5 - i, '♛',
                       ha='center', va='center', fontsize=40)

    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=16, pad=20)

    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"已保存图片: {filename}")

    plt.show()


def plot_graph_coloring(nodes, edges, coloring, filename=None, title="Graph Coloring"):
    """
    绘制图着色结果

    参数：
        nodes: 节点列表
        edges: 边列表（元组列表）
        coloring: 节点着色方案（字典：节点 -> 颜色）
        filename: 保存文件名（可选）
        title: 标题
    """
    import networkx as nx

    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    # 颜色映射
    color_map = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
    node_colors = [color_map[coloring[node] - 1] for node in nodes]

    # 绘制图
    fig, ax = plt.subplots(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)

    nx.draw(G, pos,
           node_color=node_colors,
           with_labels=True,
           node_size=800,
           font_size=12,
           font_weight='bold',
           edge_color='gray',
           linewidths=2,
           ax=ax)

    ax.set_title(title, fontsize=16, pad=20)

    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"已保存图片: {filename}")

    plt.show()


def plot_performance_comparison(labels, times, filename=None, title="Performance Comparison"):
    """
    绘制性能对比柱状图

    参数：
        labels: 标签列表
        times: 时间列表（秒）
        filename: 保存文件名（可选）
        title: 标题
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(labels))
    bars = ax.bar(x, times, color='steelblue', alpha=0.8)

    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.4f}s',
               ha='center', va='bottom', fontsize=10)

    ax.set_xlabel('测试案例', fontsize=12)
    ax.set_ylabel('求解时间（秒）', fontsize=12)
    ax.set_title(title, fontsize=14, pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"已保存图片: {filename}")

    plt.show()


def plot_sat_unsat_ratio(sat_count, unsat_count, filename=None, title="SAT vs UNSAT"):
    """
    绘制 SAT/UNSAT 比例饼图

    参数：
        sat_count: SAT 数量
        unsat_count: UNSAT 数量
        filename: 保存文件名（可选）
        title: 标题
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    sizes = [sat_count, unsat_count]
    labels = [f'SAT ({sat_count})', f'UNSAT ({unsat_count})']
    colors = ['lightgreen', 'lightcoral']
    explode = (0.1, 0)

    ax.pie(sizes, explode=explode, labels=labels, colors=colors,
          autopct='%1.1f%%', shadow=True, startangle=90)

    ax.set_title(title, fontsize=14, pad=20)

    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"已保存图片: {filename}")

    plt.show()


if __name__ == "__main__":
    # 测试代码
    print("可视化工具模块测试")
    print("=" * 60)

    # 测试数独打印
    sudoku_grid = [
        [5,3,0, 0,7,0, 0,0,0],
        [6,0,0, 1,9,5, 0,0,0],
        [0,9,8, 0,0,0, 0,6,0],
        [8,0,0, 0,6,0, 0,0,3],
        [4,0,0, 8,0,3, 0,0,1],
        [7,0,0, 0,2,0, 0,0,6],
        [0,6,0, 0,0,0, 2,8,0],
        [0,0,0, 4,1,9, 0,0,5],
        [0,0,0, 0,8,0, 0,7,9]
    ]

    print_sudoku(sudoku_grid, "数独示例")

    # 测试 N 皇后打印
    queens_solution = [0, 4, 7, 5, 2, 6, 1, 3]
    print_chess(queens_solution, 8, "8 皇后示例")

    print("所有测试完成！")
