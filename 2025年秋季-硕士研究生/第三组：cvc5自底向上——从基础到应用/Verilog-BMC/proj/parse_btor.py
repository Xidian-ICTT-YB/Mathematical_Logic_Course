from pysmt.fnode import FNode
from pysmt.shortcuts import (
    Symbol, Not, And, Or, Xor, BVAdd, BVSub, BVMul, BVAnd, BVOr, BVXor,
    BVNot, BVNeg, BVConcat, BVExtract, BVZExt, BVSExt, BVComp, EqualsOrIff,
    BVUGT, BVUGE, BVULT, BVULE, BVSGT, BVSGE, BVSLT, BVSLE,
    BVLShl, BVLShr, BVAShr, Ite, Array, Select, Store, TRUE, BV, get_type
)
from pysmt.typing import BOOL, BVType, ArrayType

def B2BV(formula: FNode) -> FNode:
    """将布尔公式转换为1位比特向量"""
    if get_type(formula) == BOOL:
        return Ite(formula, BV(1, 1), BV(0, 1))
    return formula

def BV2B(formula: FNode) -> FNode:
    """将1位比特向量转换为布尔公式"""
    ty = get_type(formula)
    if ty.is_bv_type() and ty.width == 1:
        return EqualsOrIff(formula, BV(1, 1))
    return formula

def parse_btor2_manual(btor2_filepath: str):
    """
    解析BTOR2文件为PySMT可处理的结构
    """
    node_map = {}
    init_formulas = []
    invariant_formulas = []
    transitions = {}  # {状态变量: 下一状态公式}
    # properties = []   # [(属性名, 待检查公式)]
    state_vars = set()
    input_vars = set()
    output_vars = set()
    symbol_table = {}

    def get_node(nid_str: str) -> FNode:
        """获取节点对应的公式（处理负节点的取反）"""
        nid = int(nid_str)
        if nid < 0:
            positive_nid_str = str(-nid)
            node = node_map[positive_nid_str]
            if get_type(node) == BOOL:
                return Not(node)
            else:
                return BVNot(node)
        else:
            return node_map[nid_str]

    with open(btor2_filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            
            tokens = line.split()
            nid, ntype, *args = tokens
            
            if ntype == "sort":
                if args[0] == "bitvec":
                    node_map[nid] = BVType(int(args[1]))
                elif args[0] == "array":
                    node_map[nid] = ArrayType(get_node(args[1]), get_node(args[2]))
            
            elif ntype == "constd":
                node_map[nid] = BV(int(args[1]), get_node(args[0]).width)
            elif ntype == "zero":
                node_map[nid] = BV(0, get_node(args[0]).width)
            
            elif ntype == "state":
                var_type = get_node(args[0])
                var_name = args[1] if len(args) > 1 else f"state_{nid}"
                var_symbol = Symbol(var_name, var_type)
                node_map[nid] = var_symbol
                state_vars.add(var_symbol)
                symbol_table[var_name] = var_symbol

            elif ntype == "input":
                var_type = get_node(args[0])
                var_name = args[1] if len(args) > 1 else f"input_{nid}"
                var_symbol = Symbol(var_name, var_type)
                node_map[nid] = var_symbol
                input_vars.add(var_symbol)
                symbol_table[var_name] = var_symbol
            
            elif ntype == "output":
                internal_signal = B2BV(get_node(args[0]))
                output_symbol = Symbol(args[1], internal_signal.get_type())
                constraint = EqualsOrIff(output_symbol, internal_signal)
                invariant_formulas.append(constraint)
                output_vars.add(output_symbol)
                node_map[nid] = constraint
                symbol_table[args[1]] = output_symbol

            elif ntype == "init":
                state_var_node = get_node(args[1])
                init_val_node = get_node(args[2])

                if (get_type(state_var_node) == BOOL) or (get_type(init_val_node) == BOOL):
                    formula = EqualsOrIff(BV2B(state_var_node), BV2B(init_val_node))
                elif get_type(state_var_node).is_array_type():
                    array_type = get_type(state_var_node)
                    formula = EqualsOrIff(state_var_node, Array(array_type.index_type, default=init_val_node))
                else:
                    formula = EqualsOrIff(state_var_node, init_val_node)
                
                init_formulas.append(formula)
                node_map[nid] = formula
                
            elif ntype == "next":
                state_var = get_node(args[1])
                next_val_formula = get_node(args[2])
                if (get_type(state_var) == BOOL) or (get_type(next_val_formula) == BOOL):
                    rval = B2BV(next_val_formula)
                else:
                    rval = next_val_formula
                transitions[state_var] = rval
                
            # elif ntype == "bad":
            #     bad_signal = get_node(args[0])
            #     property_formula = Not(BV2B(bad_signal))
            #     prop_name = args[1] if len(args) > 1 else f"embedded_assertion_{len(properties)}"
            #     properties.append((prop_name, "invariant", property_formula))

            # 算术和逻辑操作
            elif ntype == "add":
                node_map[nid] = BVAdd(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "sub":
                node_map[nid] = BVSub(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "mul":
                node_map[nid] = BVMul(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "neg":
                node_map[nid] = BVNeg(B2BV(get_node(args[1])))
            elif ntype == "and":
                node_map[nid] = BVAnd(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "or":
                node_map[nid] = BVOr(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "xor":
                node_map[nid] = BVXor(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "not":
                node_map[nid] = BVNot(B2BV(get_node(args[1])))
            elif ntype == "eq":
                node_map[nid] = BVComp(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "neq":
                node_map[nid] = Not(BVComp(B2BV(get_node(args[1])), B2BV(get_node(args[2]))))
            elif ntype == "slice":
                node_map[nid] = BVExtract(B2BV(get_node(args[1])), int(args[3]), int(args[2]))
            elif ntype == "uext":
                node_map[nid] = BVZExt(B2BV(get_node(args[1])), int(args[2]))
            elif ntype == "sext":
                node_map[nid] = BVSExt(B2BV(get_node(args[1])), int(args[2]))
            elif ntype == "concat":
                node_map[nid] = BVConcat(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "sll":
                node_map[nid] = BVLShl(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "srl":
                node_map[nid] = BVLShr(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "sra":
                node_map[nid] = BVAShr(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "ugt":
                node_map[nid] = BVUGT(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "ugte":
                node_map[nid] = BVUGE(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "ult":
                node_map[nid] = BVULT(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "ulte":
                node_map[nid] = BVULE(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "sgt":
                node_map[nid] = BVSGT(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "sgte":
                node_map[nid] = BVSGE(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "slt":
                node_map[nid] = BVSLT(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "slte":
                node_map[nid] = BVSLE(B2BV(get_node(args[1])), B2BV(get_node(args[2])))
            elif ntype == "ite":
                node_map[nid] = Ite(BV2B(get_node(args[1])), get_node(args[2]), get_node(args[3]))
            elif ntype == "read":
                node_map[nid] = Select(get_node(args[1]), get_node(args[2]))
            elif ntype == "write":
                node_map[nid] = Store(get_node(args[1]), get_node(args[2]), get_node(args[3]))
            elif ntype == "const":
                node_map[nid] = BV(int(args[1], 2), get_node(args[0]).width)
            else:
                if nid not in node_map:
                    print(f"Warning: 未知操作: '{ntype}'")

    return (
        And(init_formulas),
        transitions,
        # properties,
        And(invariant_formulas),
        state_vars,
        input_vars,
        symbol_table
    )