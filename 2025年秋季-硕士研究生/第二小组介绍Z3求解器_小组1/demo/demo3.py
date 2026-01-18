from z3 import *
def demo_optimization():
    print("\n--- Demo 3: 组合优化 (最大化利润) ---")

    a, b = Ints('a b')

    opt = Optimize()

    opt.add(a >= 0, b >= 0)
    opt.add(a + b <= 50)
    opt.add(2*a + 1*b <= 80)

    profit = opt.maximize(10*a + 9*b)
    
    if opt.check() == sat:
        opt.model()
        print(f"最佳方案: 产品A = {opt.model()[a]}, 产品B = {opt.model()[b]}")
        final_profit = 10 * opt.model()[a].as_long() + 9 * opt.model()[b].as_long()
        print(f"最大利润: {final_profit}")
    else:
        print("无解")

demo_optimization()