import sys
from pysmt.shortcuts import Solver, EqualsOrIff, Not, Symbol, get_type, BV
from pysmt.fnode import FNode

def print_counterexample(model, k, vars_at_step):
    """打印反例信息"""
    print("--- 反例信息 ---")
    for i in range(k + 1):
        print(f"  --- 步骤 {i} ---")
        for base_var, var_at_i in vars_at_step[i].items():
            value = model.get_value(var_at_i)
            print(f"    {base_var.symbol_name()}: {value}")
    print("-----------------")

def run_bmc(init_formula, transitions, invariant_formula, symbol_table,
        state_vars, input_vars,
        property_formula, fail_msg_template, process_flow, clock_info, k_max=20):
    """
    执行边界模型检查
    参数:
        - init_formula: 初始状态公式 (PySMT FNode)
        - transitions: 转换关系字典 {状态变量: 下一个状态公式}
        - invariant_formula: 系统不变量公式 (PySMT FNode)
        - symbol_table: 符号表 {变量名: PySMT 变量}
        - state_vars: 状态变量列表 (PySMT 变量)
        - input_vars: 输入变量列表 (PySMT 变量)
        - property_formula: 要检查的属性公式 (PySMT FNode)
        - fail_msg_template: 失败消息模板 (字符串)
        - process_flow: 流程段列表 
        - clock_info: 时钟信息
        - k_max: 最大展开步数 (整数)
    """
    all_vars = set(symbol_table.values())

    with Solver(name='cvc5', logic='QF_AUFBV') as solver:
        vars_at_step = {}
        print(f"--- 开始 BMC (K_max = {k_max}) ---")

        k = 0
        segment_index = 0
        k_in_segment = 0
        
        while k <= k_max:
            if segment_index >= len(process_flow):
                print(f"Process flow 结束于 k={k-1}。停止检查。")
                break
                
            current_segment_values, current_duration = process_flow[segment_index]
            print(f"正在检查步骤 K = {k} (段 {segment_index}, 段内步数 {k_in_segment})")

            # 1. 创建当前步骤的变量
            vars_at_step[k] = {}
            sub_map_k = {}
            for var in all_vars:
                var_at_k = Symbol(f"{var.symbol_name()}_{k}", var.symbol_type())
                vars_at_step[k][var] = var_at_k
                sub_map_k[var] = var_at_k

            # 2. 断言 初始状态 / 转换关系
            if k == 0:
                init_at_k0 = init_formula.substitute(sub_map_k)
                solver.add_assertion(init_at_k0)
            else:
                # 1. 这个 map (k-1) 是正确的: {base_var: var_at_{k-1}}
                sub_map_k_minus_1 = vars_at_step[k-1] 
                
                for state_var, next_formula in transitions.items():
                    # 2. 这是当前步骤的状态 (例如, state_6_k)
                    next_var_at_k = vars_at_step[k][state_var]
                    
                    # 3. 这是次态逻辑 (D-input)
                    #    它 *必须* 只使用来自 k-1 的值进行评估
                    formula_at_k_minus_1 = next_formula.substitute(sub_map_k_minus_1)

                    # 4. 断言正确的顺序逻辑:
                    #    state_k == D(state_{k-1}, input_{k-1})
                    solver.add_assertion(EqualsOrIff(next_var_at_k, formula_at_k_minus_1))


            # 3. 断言 不变量 (例如 'out' 的定义)
            if not invariant_formula.is_true():
                inv_at_k = invariant_formula.substitute(sub_map_k)
                solver.add_assertion(inv_at_k)

            # 4. (关键) 断言激励 (Stimulus)
            for clock_name, period in clock_info.items():
                try:
                    # 计算时钟值: (k // period) % 2
                    # 示例 (period=1): k=0 -> 0; k=1 -> 1; k=2 -> 0; ...
                    # 示例 (period=2): k=0,1 -> 0; k=2,3 -> 1; ...
                    current_clk_val = (k // period) % 2
                    
                    base_var = symbol_table[clock_name]
                    var_at_k = vars_at_step[k][base_var]
                    val_bv = BV(current_clk_val, base_var.symbol_type().width)
                    
                    solver.add_assertion(EqualsOrIff(var_at_k, val_bv))
                except KeyError:
                    print(f"警告: [CLOCK] 中的时钟 '{clock_name}' 在模型中未找到。")
            
            # 4.B 断言 [PROCESS] 行为
            for var_name, str_val in current_segment_values.items():
                
                if var_name in clock_info:
                    # 如果这个变量由 [CLOCK] 块控制, [PROCESS] 块不能覆盖它
                    continue 
                
                try:
                    base_var = symbol_table[var_name]
                    var_at_k = vars_at_step[k][base_var]
                    val_bv = BV(int(str_val), base_var.symbol_type().width)
                    solver.add_assertion(EqualsOrIff(var_at_k, val_bv))
                except KeyError:
                    print(f"警告: Process 中的变量 '{var_name}' 在模型中未找到。")
                except ValueError:
                    print(f"警告: Process 中的值 '{str_val}' 不是有效整数。")

            # 5. 检查 [PROPERTY]
            check_formula_at_k = property_formula.substitute(sub_map_k)
            
            solver.push()
            solver.add_assertion(check_formula_at_k)
            
            if solver.solve():
                print(f"\n!!! {fail_msg_template.format(k=k)} !!!\n")
                model = solver.get_model()
                print_counterexample(model, k, vars_at_step)
                solver.pop()
                return # 找到一个反例，停止

            solver.pop()

            # 6. 推进时间
            k += 1
            k_in_segment += 1
            if k_in_segment >= current_duration:
                segment_index += 1
                k_in_segment = 0
        
        print("---------------------------------")
        print(f"属性在 {k_max} 个步骤内未被触发 (PASSED)")