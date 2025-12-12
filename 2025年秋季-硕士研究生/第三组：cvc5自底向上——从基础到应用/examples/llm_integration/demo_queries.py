#!/usr/bin/env python3
"""
演示查询集合
用于测试和展示
"""

# 简单整数约束问题
SIMPLE_QUERIES = [
    "找三个正整数,它们的和是15,第一个数是偶数",
    "找两个数,差是5,积是24",
    "x 和 y 都是正整数,x+2y=10,求所有可能的解",
]

# 方程求解
EQUATION_QUERIES = [
    "解方程 x^2 - 5*x + 6 = 0",
    "解方程组: x + y = 10, x - y = 2",
    "2*x + 3*y = 12, x 和 y 都是正整数",
]

# 逻辑推理问题
LOGIC_QUERIES = [
    "有三个人A、B、C,A比B年龄大,C比A小,B是25岁,问C可能多少岁",
    "有5个人,分别叫甲乙丙丁戊,身高都不同。甲比乙高,丙比丁矮,戊最高。求一种可能的身高排序",
    "4个人参加比赛,张三不是第一,李四比王五名次高,赵六是第三,求可能的排名",
]

# 组合优化
OPTIMIZATION_QUERIES = [
    "3个物品,重量分别是2kg、3kg、4kg,价值分别是10元、15元、20元,背包容量5kg,怎么装价值最大",
    "买苹果和橙子,苹果3元/个,橙子5元/个,总共花50元,至少买3个苹果,最多能买多少个橙子",
]

# 数学问题
MATH_QUERIES = [
    "找一个两位数,个位数字是十位数字的2倍,这个数能被3整除",
    "一个三位数,百位数字比十位大2,十位比个位大1,三个数字之和是15",
]


def run_demos(solver_func, category: str = "all"):
    """
    运行演示

    Args:
        solver_func: 求解函数
        category: 类别 (all/simple/equation/logic/optimization/math)
    """
    queries_map = {
        'simple': SIMPLE_QUERIES,
        'equation': EQUATION_QUERIES,
        'logic': LOGIC_QUERIES,
        'optimization': OPTIMIZATION_QUERIES,
        'math': MATH_QUERIES,
    }

    if category == 'all':
        queries = SIMPLE_QUERIES + EQUATION_QUERIES + LOGIC_QUERIES
    else:
        queries = queries_map.get(category, SIMPLE_QUERIES)

    print(f"\n{'='*60}")
    print(f"演示: {category.upper()} 类问题")
    print(f"{'='*60}\n")

    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] {query}")
        try:
            solver_func(query, verbose=False)
        except Exception as e:
            print(f"错误: {e}")

        if i < len(queries):
            input("\n按回车继续...")


if __name__ == "__main__":
    print("这是演示查询文件,不能直接运行")
    print("请使用: python nl2smt_solver.py")
    print("\n可用的演示查询:")

    print("\n【简单整数约束】")
    for q in SIMPLE_QUERIES:
        print(f"  - {q}")

    print("\n【方程求解】")
    for q in EQUATION_QUERIES:
        print(f"  - {q}")

    print("\n【逻辑推理】")
    for q in LOGIC_QUERIES:
        print(f"  - {q}")

    print("\n【组合优化】")
    for q in OPTIMIZATION_QUERIES:
        print(f"  - {q}")

    print("\n【数学问题】")
    for q in MATH_QUERIES:
        print(f"  - {q}")
