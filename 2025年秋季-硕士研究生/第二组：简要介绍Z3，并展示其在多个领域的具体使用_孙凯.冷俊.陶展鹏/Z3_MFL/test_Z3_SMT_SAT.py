"""
一个代码展示SAT、SMT、Z3的区别
同一个问题，用三种方式解决，对比难度和表达能力
"""
from z3 import *
import itertools

def print_section(title):
    """打印分隔部分"""
    print("\n" + "="*70)
    print(f"🔍 {title}")
    print("="*70)

def problem_description():
    """问题描述"""
    print_section("问题：逻辑电路分析")
    print("有一个逻辑电路，规则如下：")
    print("1. 如果开关A和B都打开，则灯亮")
    print("2. 如果开关B和C都打开，则灯灭")
    print("3. 开关只能是开(1)或关(0)")
    print("4. 灯只能是亮(1)或灭(0)")
    print("\n问：是否存在开关设置，使得所有规则都满足？")

# ==================== 1. SAT求解器方式 ====================
def sat_solver_approach():
    """纯SAT求解器方式"""
    print_section("方法1：SAT求解器（纯布尔逻辑）")
    
    print("SAT只能处理布尔变量，所以需要：")
    print("1. 每个开关用布尔变量表示")
    print("2. 灯用布尔变量表示")
    print("3. 所有规则转换为CNF格式")
    
    # SAT输入需要CNF格式，这里我们模拟手动转换过程
    print("\n📝 手动转换为CNF（合取范式）：")
    
    # 变量：A, B, C, L
    # 规则1: (A ∧ B) → L 等价于 ¬(A ∧ B) ∨ L 等价于 ¬A ∨ ¬B ∨ L
    print("规则1: (A ∧ B) → L")
    print("      转换为: ¬A ∨ ¬B ∨ L")
    
    # 规则2: (B ∧ C) → ¬L 等价于 ¬(B ∧ C) ∨ ¬L 等价于 ¬B ∨ ¬C ∨ ¬L
    print("规则2: (B ∧ C) → ¬L")
    print("      转换为: ¬B ∨ ¬C ∨ ¬L")
    
    # 模拟SAT求解过程：暴力枚举所有可能性
    print("\n🔎 SAT暴力枚举（2⁴ = 16种可能）：")
    
    # 所有可能的真值赋值
    variables = ['A', 'B', 'C', 'L']
    solutions = []
    
    for bits in itertools.product([0, 1], repeat=4):
        A, B, C, L = bits
        
        # 检查是否满足所有CNF子句
        # 子句1: ¬A ∨ ¬B ∨ L
        clause1 = (not A) or (not B) or L
        
        # 子句2: ¬B ∨ ¬C ∨ ¬L  
        clause2 = (not B) or (not C) or (not L)
        
        if clause1 and clause2:
            solutions.append((A, B, C, L))
    
    print(f"找到 {len(solutions)} 个解：")
    for i, sol in enumerate(solutions[:5]):  # 只显示前5个
        A, B, C, L = sol
        print(f"  解{i+1}: A={A}, B={B}, C={C}, 灯={'亮' if L==1 else '灭'}")
    
    if len(solutions) > 5:
        print(f"  ... 还有 {len(solutions)-5} 个解")
    
    print("\n⚠️ SAT的限制：")
    print("  1. 只能处理布尔值")
    print("  2. 需要手动转换为CNF")
    print("  3. 无法处理算术运算")
    print("  4. 表达式复杂难懂")
    
    return solutions

# ==================== 2. SMT求解器方式 ====================
def smt_solver_approach():
    """SMT求解器方式"""
    print_section("方法2：SMT求解器（支持整数理论）")
    
    print("SMT可以处理整数，所以：")
    print("1. 开关用整数变量，值域{0,1}")
    print("2. 灯用整数变量，值域{0,1}")
    print("3. 规则用一阶逻辑表达")
    
    print("\n📝 用SMT-LIB格式表达问题：")
    smt_lib_code = """
(set-logic QF_LIA)  ; 量化自由的线性整数算术
(declare-const A Int)
(declare-const B Int)
(declare-const C Int)
(declare-const L Int)  ; 灯：1=亮, 0=灭

; 开关只能是0或1
(assert (or (= A 0) (= A 1)))
(assert (or (= B 0) (= B 1)))
(assert (or (= C 0) (= C 1)))

; 灯只能是0或1
(assert (or (= L 0) (= L 1)))

; 规则1: 如果A和B都开，则灯亮
(assert (=> (and (= A 1) (= B 1)) (= L 1)))

; 规则2: 如果B和C都开，则灯灭
(assert (=> (and (= B 1) (= C 1)) (= L 0)))

(check-sat)
(get-model)
"""
    print(smt_lib_code)
    
    print("\n✅ SMT的优势：")
    print("  1. 可以直接用整数")
    print("  2. 可以用算术运算")
    print("  3. 表达式更接近自然描述")
    print("  4. 不需要手动转换为CNF")
    
    # 用Z3模拟SMT求解（Z3是SMT求解器）
    print("\n🔎 用Z3求解（作为SMT求解器）：")
    
    # 创建求解器
    s = Solver()
    
    # 定义变量为整数
    A = Int('A')
    B = Int('B')
    C = Int('C')
    L = Int('L')
    
    # 添加约束
    s.add(Or(A == 0, A == 1))
    s.add(Or(B == 0, B == 1))
    s.add(Or(C == 0, C == 1))
    s.add(Or(L == 0, L == 1))
    
    # 规则1: 如果A和B都开，则灯亮
    s.add(Implies(And(A == 1, B == 1), L == 1))
    
    # 规则2: 如果B和C都开，则灯灭
    s.add(Implies(And(B == 1, C == 1), L == 0))
    
    # 找所有解
    solutions = []
    temp_solver = Solver()
    for c in s.assertions():
        temp_solver.add(c)
    
    while temp_solver.check() == sat:
        m = temp_solver.model()
        sol = (m[A].as_long(), m[B].as_long(), m[C].as_long(), m[L].as_long())
        solutions.append(sol)
        
        # 排除这个解
        temp_solver.add(Or(A != m[A], B != m[B], C != m[C], L != m[L]))
    
    print(f"找到 {len(solutions)} 个解（与SAT结果相同）")
    
    return solutions

# ==================== 3. Z3高级功能展示 ====================
def z3_advanced_features():
    """Z3高级功能展示"""
    print_section("方法3：Z3的高级功能（超越普通SMT）")
    
    print("Z3不仅是SMT求解器，还有额外功能：")
    
    # 1. 优化功能
    print("\n🌟 功能1：优化求解（不只是找解，要找最优解）")
    
    # 假设每个开关有耗电量：A=3W, B=2W, C=1W
    # 问题：在满足规则的前提下，最小化总耗电量
    
    print("\n扩展问题：每个开关耗电不同")
    print("  A开关: 3W, B开关: 2W, C开关: 1W")
    print("  目标：在满足规则的前提下，最小化总耗电")
    
    # 使用Optimize而不是Solver
    opt = Optimize()
    
    A = Int('A')
    B = Int('B')
    C = Int('C')
    L = Int('L')
    
    # 基本约束
    opt.add(Or(A == 0, A == 1))
    opt.add(Or(B == 0, B == 1))
    opt.add(Or(C == 0, C == 1))
    opt.add(Or(L == 0, L == 1))
    
    # 规则约束
    opt.add(Implies(And(A == 1, B == 1), L == 1))
    opt.add(Implies(And(B == 1, C == 1), L == 0))
    
    # 目标函数：最小化总耗电
    power = 3*A + 2*B + 1*C
    opt.minimize(power)
    
    if opt.check() == sat:
        m = opt.model()
        total_power = 3*m[A].as_long() + 2*m[B].as_long() + 1*m[C].as_long()
        print(f"\n✅ 最优解：")
        print(f"  A={m[A]}, B={m[B]}, C={m[C]}, 灯={'亮' if m[L].as_long()==1 else '灭'}")
        print(f"  总耗电：{total_power}W（最小可能）")
    
    # 2. 找所有解的高级方式
    print("\n🌟 功能2：找特定类型的解")
    print("问题：找到所有让灯亮的解")
    
    s2 = Solver()
    s2.add(Or(A == 0, A == 1))
    s2.add(Or(B == 0, B == 1))
    s2.add(Or(C == 0, C == 1))
    s2.add(Or(L == 0, L == 1))
    s2.add(Implies(And(A == 1, B == 1), L == 1))
    s2.add(Implies(And(B == 1, C == 1), L == 0))
    s2.add(L == 1)  # 只找灯亮的解
    
    light_on_solutions = []
    while s2.check() == sat:
        m = s2.model()
        sol = (m[A].as_long(), m[B].as_long(), m[C].as_long(), m[L].as_long())
        light_on_solutions.append(sol)
        s2.add(Or(A != m[A], B != m[B], C != m[C], L != m[L]))
    
    print(f"  让灯亮的解有 {len(light_on_solutions)} 个：")
    for sol in light_on_solutions:
        print(f"    A={sol[0]}, B={sol[1]}, C={sol[2]}")
    
    # 3. 混合不同类型
    print("\n🌟 功能3：混合不同类型")
    print("扩展：开关有状态（0/1）和颜色（红/绿/蓝）")
    
    # 定义枚举类型
    Color = Datatype('Color')
    Color.declare('red')
    Color.declare('green')
    Color.declare('blue')
    Color = Color.create()
    
    # 创建变量
    A_state, B_state, C_state = Ints('A_state B_state C_state')
    A_color, B_color, C_color = Consts('A_color B_color C_color', Color)
    L = Int('L')
    
    s3 = Solver()
    
    # 状态约束
    s3.add(Or(A_state == 0, A_state == 1))
    s3.add(Or(B_state == 0, B_state == 1))
    s3.add(Or(C_state == 0, C_state == 1))
    s3.add(Or(L == 0, L == 1))
    
    # 规则约束
    s3.add(Implies(And(A_state == 1, B_state == 1), L == 1))
    s3.add(Implies(And(B_state == 1, C_state == 1), L == 0))
    
    # 颜色约束：A必须是红色
    s3.add(A_color == Color.red)
    
    if s3.check() == sat:
        m = s3.model()
        print(f"\n✅ 混合类型解：")
        print(f"  A: 状态={m[A_state]}, 颜色={m[A_color]}")
        print(f"  B: 状态={m[B_state]}, 颜色={m[B_color]}")
        print(f"  C: 状态={m[C_state]}, 颜色={m[C_color]}")
        print(f"  灯: {'亮' if m[L].as_long()==1 else '灭'}")
    
    print("\n🎯 Z3的独特优势：")
    print("  1. 优化功能：minimize()/maximize()")
    print("  2. 丰富的API：Python/C++/Java等")
    print("  3. 混合理论：布尔+整数+自定义类型")
    print("  4. 策略控制：可以调整求解策略")
    print("  5. 易用性：像写Python一样简单")

# ==================== 4. 三者的对比总结 ====================
def comparison_summary():
    """对比总结"""
    print_section("三种方法对比总结")
    
    print("🧩 表达能力对比：")
    print("  SAT:     只能处理 布尔逻辑")
    print("  SMT:     能处理 布尔逻辑 + 数学理论（整数、实数等）")
    print("  Z3:      能处理 布尔逻辑 + 数学理论 + 优化 + 自定义类型 + ...")
    
    print("\n💻 使用难度对比：")
    print("  SAT:     🔴🔴🔴🔴🔴 非常困难")
    print("            需要手动转换为CNF格式")
    print("            只能通过文件输入")
    print("            输出难以解析")
    
    print("\n  SMT:     🟡🟡🟡⚪⚪ 中等难度")  
    print("            需要学习SMT-LIB语法")
    print("            表达式更自然")
    print("            支持算术运算")
    
    print("\n  Z3:      🟢🟢🟢🟢🟢 非常简单")
    print("            Python API，直观易用")
    print("            几乎直接翻译问题描述")
    print("            丰富的文档和示例")
    
    print("\n🚀 性能对比：")
    print("  SAT:     极快，针对布尔逻辑优化")
    print("  SMT:     快，但比SAT慢（需要理论推理）")
    print("  Z3:      快，有各种优化策略")
    
    print("\n🎯 应用场景：")
    print("  SAT:     硬件验证、电路设计、纯逻辑问题")
    print("  SMT:     软件验证、程序分析、带算术的问题")
    print("  Z3:      研究、教育、CTF、测试生成、优化问题")
    
    print("\n🔗 关系总结：")
    print("  Z3 ⊃ SMT求解器 ⊃ SAT求解器")
    print("  Z3内部包含SAT引擎，但功能远超SAT")

# ==================== 5. 实际演示算术问题 ====================
def arithmetic_problem_demo():
    """演示SAT无法处理，但SMT/Z3可以处理的问题"""
    print_section("算术问题演示：SAT的局限性")
    
    print("问题：找两个正整数x,y，满足：")
    print("  1. x + y = 10")
    print("  2. 2x + 3y = 26")
    print("  3. x, y > 0")
    
    # 尝试用SAT思路（会非常复杂）
    print("\n🔴 SAT方式（理论上可行，实际上极其复杂）：")
    print("  需要把整数编码为二进制")
    print("  需要实现二进制加法器逻辑")
    print("  需要实现二进制乘法器逻辑")
    print("  表达式极其庞大复杂")
    print("  几乎没有人会这么做！")
    
    # SMT方式
    print("\n🟡 SMT方式（SMT-LIB格式）：")
    print("""
(set-logic QF_LIA)
(declare-const x Int)
(declare-const y Int)
(assert (= (+ x y) 10))
(assert (= (+ (* 2 x) (* 3 y)) 26))
(assert (> x 0))
(assert (> y 0))
(check-sat)
(get-model)
""")
    
    # Z3方式
    print("\n🟢 Z3方式（Python，最简单）：")
    x, y = Ints('x y')
    s = Solver()
    s.add(x + y == 10)
    s.add(2*x + 3*y == 26)
    s.add(x > 0, y > 0)
    
    if s.check() == sat:
        m = s.model()
        print(f"  解：x = {m[x]}, y = {m[y]}")
        print(f"  验证：{m[x]} + {m[y]} = {m[x].as_long() + m[y].as_long()}")
        print(f"        2×{m[x]} + 3×{m[y]} = {2*m[x].as_long() + 3*m[y].as_long()}")
    
    print("\n💡 关键洞察：")
    print("  SAT只能处理离散的布尔值")
    print("  SMT可以处理连续的数学域")
    print("  Z3让这一切变得简单易用")

# ==================== 主函数 ====================
def main():
    """主函数"""
    print("🚀 SAT、SMT、Z3求解器对比演示")
    print("="*70)
    print("同一个问题，三种解法，展示从难到易的演变")
    
    # 问题描述
    problem_description()
    
    # 1. SAT方式
    sat_solutions = sat_solver_approach()
    
    # 2. SMT方式
    smt_solutions = smt_solver_approach()
    
    # 验证两种方式结果一致
    if set(sat_solutions) == set(smt_solutions):
        print("\n✅ SAT和SMT找到的解完全相同")
    else:
        print("\n❌ SAT和SMT结果不同（这不应该发生）")
    
    # 3. Z3高级功能
    z3_advanced_features()
    
    # 4. 算术问题演示
    arithmetic_problem_demo()
    
    # 5. 总结对比
    comparison_summary()
    
    # 最终建议
    print_section("给初学者的建议")
    print("🎓 学习路径：")
    print("  1. 直接从Z3开始学习（最友好）")
    print("  2. 理解SMT的基本概念（理论背景）")
    print("  3. 了解SAT的原理（深入底层）")
    print("  4. 实际用Z3解决问题（实践）")
    
    print("\n💪 开始使用Z3：")
    print("  安装：pip install z3-solver")
    print("  第一行代码：from z3 import *")
    print("  第一个问题：x = Int('x'); solve(x > 0, x < 10)")
    
    print("\n" + "="*70)
    print("🌟 总结：从SAT到Z3，是表达能力↑、易用性↑、功能↑的进化")
    print("="*70)

# 运行主函数
if __name__ == "__main__":
    main()