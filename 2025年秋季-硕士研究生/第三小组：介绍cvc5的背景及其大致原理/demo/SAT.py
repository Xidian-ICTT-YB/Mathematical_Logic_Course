import cvc5
from cvc5 import Kind
import time


def solve_new_sat_problem():
    # 初始化求解器
    tm = cvc5.TermManager()
    solver = cvc5.Solver(tm)
    solver.setOption("produce-models", "true")
    solver.setOption("produce-unsat-cores", "true")
    solver.setLogic("ALL")

    # 定义辅助函数，简化代码，符合阅读习惯
    def OR(*args):
        return tm.mkTerm(Kind.OR, *args)

    def NOT(x):
        return tm.mkTerm(Kind.NOT, x)

    # 定义布尔类型
    boolSort = tm.getBooleanSort()

    # 创建布尔变量 p, q, r, s, t, u，作为逻辑命题的基本原子
    p = tm.mkConst(boolSort, "p")
    q = tm.mkConst(boolSort, "q")
    r = tm.mkConst(boolSort, "r")
    s = tm.mkConst(boolSort, "s")
    t = tm.mkConst(boolSort, "t")
    u = tm.mkConst(boolSort, "u")



    # 构建子句
    # 1. (p ∨ ¬q ∨ r)
    clause1 = OR(p, NOT(q), r) #添加8个约束
    solver.assertFormula(clause1)

    # 2. (¬p ∨ q ∨ ¬s)
    clause2 = OR(NOT(p), q, NOT(s))
    solver.assertFormula(clause2)

    # 3. (r ∨ s ∨ ¬t)
    clause3 = OR(r, s, NOT(t))
    solver.assertFormula(clause3)

    # 4. (¬r ∨ t ∨ u)
    clause4 = OR(NOT(r), t, u)
    solver.assertFormula(clause4)

    # 5. (p ∨ ¬s ∨ ¬u)
    clause5 = OR(p, NOT(s), NOT(u))
    solver.assertFormula(clause5)

    # 6. (¬p ∨ q ∨ ¬t)
    clause6 = OR(NOT(p), q, NOT(t))
    solver.assertFormula(clause6)

    # 7. (q ∨ r ∨ s ∨ ¬u)
    clause7 = OR(q, r, s, NOT(u))
    solver.assertFormula(clause7)

    # 8. (¬q ∨ ¬r ∨ t ∨ u)
    clause8 = OR(NOT(q), NOT(r), t, u)
    solver.assertFormula(clause8)

    # 记录开始时间
    start_time = time.time()

    # 求解
    result = solver.checkSat()

    # 记录结束时间
    end_time = time.time()
    elapsed_time = end_time - start_time

    # 输出结果
    print("结果:", result)

    if result.isSat():
        p_val = solver.getValue(p).getBooleanValue() # 通过.getBooleanValue() 将其转换为Python的布尔值 True 或 False
        q_val = solver.getValue(q).getBooleanValue()
        r_val = solver.getValue(r).getBooleanValue()
        s_val = solver.getValue(s).getBooleanValue()
        t_val = solver.getValue(t).getBooleanValue()
        u_val = solver.getValue(u).getBooleanValue()

        print("满足解:")
        print("p =", p_val)
        print("q =", q_val)
        print("r =", r_val)
        print("s =", s_val)
        print("t =", t_val)
        print("u =", u_val)

        # 验证解的正确性
        print("\n验证解的正确性:")
        clauses = [
            (p_val or not q_val or r_val),  # 子句1: (p ∨ ¬q ∨ r)
            (not p_val or q_val or not s_val),  # 子句2: (¬p ∨ q ∨ ¬s)
            (r_val or s_val or not t_val),  # 子句3: (r ∨ s ∨ ¬t)
            (not r_val or t_val or u_val),  # 子句4: (¬r ∨ t ∨ u)
            (p_val or not s_val or not u_val),  # 子句5: (p ∨ ¬s ∨ ¬u)
            (not p_val or q_val or not t_val),  # 子句6: (¬p ∨ q ∨ ¬t)
            (q_val or r_val or s_val or not u_val),  # 子句7: (q ∨ r ∨ s ∨ ¬u)
            (not q_val or not r_val or t_val or u_val)  # 子句8: (¬q ∨ ¬r ∨ t ∨ u)
        ]

        all_satisfied = True
        for i, clause in enumerate(clauses, 1): # 输出各个子句是否为真
            satisfied = bool(clause)
            print(f"子句{i}: {satisfied}")
            if not satisfied: # 一假全假
                all_satisfied = False

        if all_satisfied:
            print("所有子句均满足 ✓")
        else:
            print("存在不满足的子句 ✗")

    else:
        print("公式不可满足。")
        unsatCore = solver.getUnsatCore()
        print("不可满足核心大小:", len(unsatCore))
        print("不可满足核心:", unsatCore)

    print(f"运行时间: {elapsed_time:.6f} 秒")
    return result


# 运行求解
if __name__ == "__main__":
    solve_new_sat_problem()