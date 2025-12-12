#!/usr/bin/env python3

from pysmt.shortcuts import Symbol, BV, EqualsOrIff, Not, BVULT, BVULE, BVUGT, BVUGE
from pysmt.fnode import FNode

def build_property_formula(prop_check, symbol_table):
    """
    将 PropertyCheck 对象转换为可执行的 PySMT 公式。
    
    返回: (check_formula, fail_msg_template)
    """
    
    # 1. 从符号表中获取 PySMT 变量
    try:
        var_symbol = symbol_table[prop_check.var_name]
    except KeyError:
        raise KeyError(f"属性 '{prop_check.var_name}' 在模型中未找到。")

    # 2. 获取变量的位宽
    width = var_symbol.symbol_type().width

    # 3. 将字符串值转换为 PySMT 的 BV (比特向量)
    try:
        val_int = int(prop_check.value_str)
        val_bv = BV(val_int, width)
    except ValueError:
        raise ValueError(f"属性值 '{prop_check.value_str}' 必须是一个整数。")

    # 4. 根据操作符构建 PySMT 公式
    op = prop_check.op
    formula = None
    
    if op == "==":
        formula = EqualsOrIff(var_symbol, val_bv)
    elif op == "!=":
        formula = Not(EqualsOrIff(var_symbol, val_bv))
    elif op == "<":
        formula = BVULT(var_symbol, val_bv)
    elif op == "<=":
        formula = BVULE(var_symbol, val_bv)
    elif op == ">":
        formula = BVUGT(var_symbol, val_bv)
    elif op == ">=":
        formula = BVUGE(var_symbol, val_bv)
    else:
        raise ValueError(f"不支持的属性操作符: '{op}'")

    fail_msg = f"属性 '{prop_check.var_name} {op} {val_int}' 在步骤 {{k}} 变为 TRUE"
    
    return formula, fail_msg