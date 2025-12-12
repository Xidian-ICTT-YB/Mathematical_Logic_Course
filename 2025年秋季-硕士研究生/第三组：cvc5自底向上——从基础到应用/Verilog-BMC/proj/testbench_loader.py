#!/usr/bin/env python3

import sys
import re
from collections import namedtuple

# 使用一个简单的数据结构来存储解析后的属性
PropertyCheck = namedtuple("PropertyCheck", ["var_name", "op", "value_str"])

def load_testbench(filepath):
    """
    解析自定义的 .txt testbench 文件。 
    
    返回:
    - property_to_check: 一个 PropertyCheck 对象
    - process_flow: 一个代表激励流程的列表
    - clock_info: 一个字典, 例如 {'clk': 1}
    """
    
    property_to_check = None
    process_flow = []
    clock_info = {}
    
    mode = None
    current_assignments = {}
    sticky_assignments = {}
    
    try:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith(';'): # 允许注释
                    continue

                # --- 模式切换 ---
                if line == "[PROPERTY]":
                    mode = "PROPERTY"
                    continue
                elif line == "[PROCESS]":
                    mode = "PROCESS"
                    continue
                elif line == "[CLOCK]":
                    mode = "CLOCK"
                    continue
                
                # --- 模式解析 ---
                if mode == "PROPERTY":
                    match = re.match(r"^\s*(\w+)\s*([=<>!]+)\s*(\S+)\s*$", line)
                    if match:
                        var, op, val = match.groups()
                        property_to_check = PropertyCheck(var, op, val)
                    else:
                        raise ValueError(f"第 {line_num} 行属性格式无效: {line}")
                    mode = None 

                elif mode == "CLOCK": 
                    try:
                        var, val = line.split('=', 1)
                        var = var.strip()
                        period_steps = int(val.strip())
                        if period_steps <= 0:
                            raise ValueError("时钟周期必须大于 0")
                        clock_info[var] = period_steps
                    except (ValueError, TypeError):
                         raise ValueError(f"第 {line_num} 行 [CLOCK] 格式无效: {line}")

                elif mode == "PROCESS":
                    if line.startswith("#"):
                        try:
                            duration = int(line[1:])
                        except ValueError:
                            raise ValueError(f"第 {line_num} 行'#'指令无效: {line}")
                        
                        segment_values = sticky_assignments.copy()
                        segment_values.update(current_assignments)
                        process_flow.append( (segment_values, duration) )
                        
                        sticky_assignments.update(current_assignments)
                        current_assignments = {}
                    
                    elif '=' in line:
                        try:
                            var, val = line.split('=', 1)
                            current_assignments[var.strip()] = val.strip()
                        except ValueError:
                             raise ValueError(f"第 {line_num} 行赋值格式无效: {line}")

        # 循环结束后，处理最后一个 [PROCESS] 段
        if mode == "PROCESS" or current_assignments or not process_flow:
             segment_values = sticky_assignments.copy()
             segment_values.update(current_assignments)
             process_flow.append( (segment_values, float('inf')) )
            
        if not property_to_check:
            raise ValueError("未在文件中找到 [PROPERTY] 部分。")
        if not process_flow:
            raise ValueError("未在文件中找到 [PROCESS] 部分。")
            
        return property_to_check, process_flow, clock_info

    except FileNotFoundError:
        print(f"错误: 找不到 Testbench 文件 '{filepath}'")
        sys.exit(1)
    except ValueError as e:
        print(f"错误: 解析 Testbench 文件时出错: {e}")
        sys.exit(1)