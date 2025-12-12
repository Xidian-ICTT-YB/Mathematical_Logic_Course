import sys
from pathlib import Path
import convert_to_btor2
import parse_btor
import bmc
from testbench_loader import load_testbench
from property_parser import build_property_formula

def main():
    parser = argparse.ArgumentParser(description="Verilog边界模型检查工具")
    parser.add_argument("input_file", help="输入的Verilog (.v) 或 SystemVerilog (.sv) 文件")
    parser.add_argument("top_module", help="Verilog文件中的顶层模块名称")
    parser.add_argument("testbench_file", help="testbench文件")
    parser.add_argument("-k", "--k_max", type=int, default=20, help="BMC最大展开步数 (默认: 20)")
    
    args = parser.parse_args()
    
    # 处理输入输出路径
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"错误: 输入文件不存在 '{input_path}'", file=sys.stderr)
        sys.exit(1)

    testbench_file = Path(args.testbench_file)    
    if not testbench_file.exists():
        print(f"错误: 找不到 testbench 文件 '{testbench_file}'。")
        sys.exit(1)

    output_path = Path(input_path.with_suffix(".btor2"))
    
    # 步骤1: 转换Verilog到BTOR2
    if not output_path.exists():
        convert_to_btor2.convert_verilog_to_btor2(input_path, args.top_module, output_path)
    
    # 步骤2: 解析BTOR2文件
    print(f"--- 解析 BTOR2 文件: {output_path} ---")
    init, transitions, invariants, state_vars, input_vars, symbol_table = parse_btor.parse_btor2_manual(str(output_path))
    
    # 打印解析信息
    print("\n--- 解析结果摘要 ---")
    print(f"状态变量: {[s.symbol_name() for s in state_vars]}")
    print(f"输入变量: {[i.symbol_name() for i in input_vars]}")
    print(f"初始状态: {init.serialize()}")
    print(f"不变量: {invariants.serialize()}")
    print("转换关系:")
    for state_var, next_formula in transitions.items():
        print(f"  {state_var.symbol_name()} -> {next_formula.serialize()}")
    print("-----------------\n")
    
    # 从 testbench 文件加载属性
    prop_check, process_flow, clock_info = load_testbench(testbench_file)
    print(f"加载属性: {prop_check.var_name} {prop_check.op} {prop_check.value_str}")
    print(f"加载了 {len(process_flow)} 个 process 段。")
    if clock_info:
        print(f"加载了时钟: {clock_info}")
    else:
        print("未加载 [CLOCK] 定义，所有输入（包括clk）必须由 [PROCESS] 控制。")
    
    try:
        check_formula, fail_msg = build_property_formula(prop_check, symbol_table)
    except (KeyError, ValueError) as e:
        print(f"错误: 构建属性时失败: {e}")
        sys.exit(1)

    # 步骤3: 执行BMC检查
    bmc.run_bmc(init, transitions, invariants, symbol_table, state_vars, input_vars,
                check_formula, fail_msg, process_flow, clock_info, args.k_max)

if __name__ == "__main__":
    import argparse  # 在main中延迟导入，避免其他模块依赖
    main()