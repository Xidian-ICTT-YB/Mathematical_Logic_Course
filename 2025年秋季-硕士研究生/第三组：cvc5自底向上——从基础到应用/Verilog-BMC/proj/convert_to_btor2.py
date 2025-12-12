import os
import sys
import subprocess
from pathlib import Path

# Yosys处理流程配置
PASSES = [
    "hierarchy -check",
    "memory -nomap",  # 支持数组/Memory
    "flatten;",       # 扁平化电路
    "clk2fflogic;"    # 不进行时钟抽象
]

# Yosys命令模板
COMMANDS = [
    "read_verilog -nomem2reg -sv {FILES}",
    "prep -top {TARGET}",
    "{PASSES}",
    "setundef -undriven -anyseq",
    "write_btor {BTORFILE}"
]

def convert_verilog_to_btor2(input_file: Path, top_module: str, output_file: Path):
    """使用Yosys将Verilog文件转换为BTOR2文件"""
    # 格式化Yosys命令
    abs_input_file = str(input_file.absolute())
    command_str = "; ".join(COMMANDS)
    formatted_command = command_str.format(
        FILES=abs_input_file,
        TARGET=top_module,
        PASSES="; ".join(PASSES),
        BTORFILE=str(output_file.absolute())
    )
    
    full_yosys_command = f"yosys -p \"{formatted_command}\""
    
    print(f"--- 正在执行 Yosys 转换 ---")
    print(f"命令: {full_yosys_command}")
    
    # 执行转换命令
    try:
        result = subprocess.run(
            full_yosys_command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        
        if result.stderr:
            print("Yosys 警告信息:\n", result.stderr)
            
        print(f"--- 转换完成，BTOR2文件生成: {output_file} ---")

    except subprocess.CalledProcessError as e:
        print("\n--- Yosys 执行失败 ---", file=sys.stderr)
        print("错误信息:", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("\n--- 错误 ---", file=sys.stderr)
        print("找不到 'yosys' 命令。请确保Yosys已安装并在PATH中。", file=sys.stderr)
        sys.exit(1)