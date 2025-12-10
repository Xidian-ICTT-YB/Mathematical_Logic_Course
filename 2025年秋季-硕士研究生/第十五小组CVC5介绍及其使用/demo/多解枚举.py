# 地图着色枚举:4 个国家相邻，只有 3 种颜色 (1=红, 2=绿, 3=蓝)。求所有可能的着色方案。
import cvc5
from cvc5 import Kind
import time

solver = cvc5.Solver()
solver.setOption("produce-models", "true")
solver.setLogic("QF_LIA")

intSort = solver.getIntegerSort()

# 定义 4 个国家
countries = [solver.mkConst(intSort, f"Country_{i}") for i in range(4)]
# 假设拓扑结构: 0与1,2,3相连; 1与2相连 (简单结构)
adj_matrix = [(0, 1), (0, 2), (0, 3), (1, 2)]

# 颜色范围 1-3
for c in countries:
    solver.assertFormula(solver.mkTerm(Kind.GEQ, c, solver.mkInteger(1)))
    solver.assertFormula(solver.mkTerm(Kind.LEQ, c, solver.mkInteger(3)))

# 相邻不能同色
for i, j in adj_matrix:
    solver.assertFormula(solver.mkTerm(Kind.DISTINCT, countries[i], countries[j]))

solution_count = 0

print("开始枚举所有着色方案...")

while True:
    start_time = time.time()
    result = solver.checkSat()

    if not result.isSat():
        break  # 没有更多解了

    solution_count += 1

    # 提取当前解
    vals = []
    print(f"方案 #{solution_count}: ", end="")
    for i in range(4):
        val = solver.getValue(countries[i]).getIntegerValue()
        vals.append(val)
    print(vals)  # 打印颜色代码 [1, 2, 3, 2] 等

    # 构建 Blocking Clause: 禁止再次出现完全相同的颜色组合
    # NOT (c0==v0 AND c1==v1 AND c2==v2 AND c3==v3)
    # 等价于: (c0!=v0 OR c1!=v1 OR ...)

    distinct_terms = []
    for i in range(4):
        term = solver.mkTerm(Kind.DISTINCT, countries[i], solver.mkInteger(vals[i]))
        distinct_terms.append(term)

    blocking_clause = solver.mkTerm(Kind.OR, *distinct_terms)
    solver.assertFormula(blocking_clause)

print(f"搜索结束，共找到 {solution_count} 种方案。")