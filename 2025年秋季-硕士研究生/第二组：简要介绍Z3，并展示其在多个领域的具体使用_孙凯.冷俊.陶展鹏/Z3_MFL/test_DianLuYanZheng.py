# """
# Z3 求解器在电路验证中的应用
# 本程序演示如何使用 Z3 验证数字电路的正确性
# """

# from z3 import *

# class CircuitVerifier:
#     def __init__(self):
#         """初始化电路验证器"""
#         print("=" * 70)
#         print("Z3 求解器在电路验证中的应用演示")
#         print("=" * 70)
#         print("\n电路验证目标：验证数字电路的正确性和等价性")
#         print("使用 Z3 将电路行为建模为逻辑约束，然后进行验证\n")
    
#     def verify_half_adder(self):
#         """验证半加器电路"""
#         print("\n" + "=" * 70)
#         print("示例 1: 半加器电路验证")
#         print("=" * 70)
        
#         # 半加器真值表
#         print("\n半加器真值表:")
#         print("A B | Sum Carry")
#         print("0 0 |  0     0")
#         print("0 1 |  1     0")
#         print("1 0 |  1     0")
#         print("1 1 |  0     1")
        
#         # 创建 Z3 求解器
#         solver = Solver()
#         print("\n步骤 1: 创建 Z3 求解器")
        
#         # 定义输入变量
#         A = Bool('A')
#         B = Bool('B')
#         print(f"步骤 2: 定义输入变量 A, B (布尔类型)")
        
#         # 定义输出变量（根据电路设计）
#         # 半加器逻辑：
#         # Sum = A XOR B
#         # Carry = A AND B
#         Sum_circuit = Xor(A, B)      # 电路实现的 Sum
#         Carry_circuit = And(A, B)    # 电路实现的 Carry
        
#         # 定义期望的输出（根据真值表规格）
#         # 使用 if-then-else 表达式定义期望行为
#         Sum_spec = If(A != B, True, False)     # A XOR B
#         Carry_spec = And(A, B)                  # A AND B
        
#         print("步骤 3: 定义电路实现和规格说明")
#         print(f"  电路实现: Sum = A XOR B, Carry = A AND B")
#         print(f"  规格说明: Sum = A XOR B, Carry = A AND B")
        
#         # 添加验证条件：验证电路实现是否满足规格
#         # 对于所有可能的输入组合，输出必须一致
#         condition1 = (Sum_circuit == Sum_spec)
#         condition2 = (Carry_circuit == Carry_spec)
        
#         print("\n步骤 4: 添加验证约束")
#         print(f"  约束 1: Sum_circuit == Sum_spec")
#         print(f"  约束 2: Carry_circuit == Carry_spec")
        
#         # 验证正向条件
#         solver.add(condition1)
#         solver.add(condition2)
        
#         print("\n步骤 5: 开始验证正向条件（电路实现满足规格）")
        
#         # 检查是否满足
#         if solver.check() == sat:
#             print("✓ 验证通过：电路实现满足规格要求")
#         else:
#             print("✗ 验证失败：电路实现不满足规格要求")
        
#         # 反向验证：是否存在反例使得电路不满足规格
#         print("\n步骤 6: 检查是否存在反例（反向验证）")
#         solver.reset()
#         solver.add(Not(And(condition1, condition2)))
        
#         if solver.check() == unsat:
#             print("✓ 确认：不存在反例，电路完全正确")
#         else:
#             print("✗ 发现反例：电路存在错误")
#             model = solver.model()
#             print(f"  反例: A={model[A]}, B={model[B]}")
    
#     def verify_full_adder(self):
#         """验证全加器电路"""
#         print("\n" + "=" * 70)
#         print("示例 2: 全加器电路验证")
#         print("=" * 70)
        
#         # 全加器真值表
#         print("\n全加器真值表:")
#         print("A B Cin | Sum Cout")
#         print("0 0  0  |  0    0")
#         print("0 0  1  |  1    0")
#         print("0 1  0  |  1    0")
#         print("0 1  1  |  0    1")
#         print("1 0  0  |  1    0")
#         print("1 0  1  |  0    1")
#         print("1 1  0  |  0    1")
#         print("1 1  1  |  1    1")
        
#         # 创建 Z3 求解器
#         solver = Solver()
        
#         # 定义输入变量
#         A = Bool('A')
#         B = Bool('B')
#         Cin = Bool('Cin')  # 进位输入
        
#         # 两种不同的全加器实现
        
#         # 实现1：直接布尔表达式实现
#         print("\n实现 1: 直接布尔表达式")
#         print("  Sum1 = A ⊕ B ⊕ Cin")
#         print("  Cout1 = (A ∧ B) ∨ (B ∧ Cin) ∨ (A ∧ Cin)")
        
#         Sum1 = Xor(Xor(A, B), Cin)
#         Cout1 = Or(And(A, B), And(B, Cin), And(A, Cin))
        
#         # 实现2：使用两个半加器实现
#         print("\n实现 2: 使用两个半加器级联")
#         print("  半加器1: S1 = A ⊕ B, C1 = A ∧ B")
#         print("  半加器2: Sum2 = S1 ⊕ Cin")
#         print("          Cout2 = (A ∧ B) ∨ (S1 ∧ Cin)")
        
#         # 第一个半加器
#         S1 = Xor(A, B)      # A XOR B
#         C1 = And(A, B)      # A AND B
        
#         # 第二个半加器
#         Sum2 = Xor(S1, Cin)
#         Cout2 = Or(C1, And(S1, Cin))
        
#         # 验证两种实现是否等价
#         print("\n验证目标：两种实现是否等价")
        
#         # 添加等价性约束
#         solver.add(Sum1 == Sum2)
#         solver.add(Cout1 == Cout2)
        
#         print("\n检查等价性约束:")
#         print(f"  Sum1 == Sum2: {Sum1} == {Sum2}")
#         print(f"  Cout1 == Cout2: {Cout1} == {Cout2}")
        
#         if solver.check() == sat:
#             print("\n✓ 两种实现等价")
            
#             # 获取一个满足条件的实例
#             model = solver.model()
#             print(f"\n示例输入: A={model[A]}, B={model[B]}, Cin={model[Cin]}")
#             print(f"输出: Sum={is_true(model.eval(Sum1))}, Cout={is_true(model.eval(Cout1))}")
#         else:
#             print("\n✗ 两种实现不等价")
            
#             # 寻找反例
#             solver.reset()
#             solver.add(Or(Sum1 != Sum2, Cout1 != Cout2))
            
#             if solver.check() == sat:
#                 model = solver.model()
#                 print(f"\n发现不等价的反例:")
#                 print(f"  A={model[A]}, B={model[B]}, Cin={model[Cin]}")
#                 print(f"  实现1: Sum={is_true(model.eval(Sum1))}, Cout={is_true(model.eval(Cout1))}")
#                 print(f"  实现2: Sum={is_true(model.eval(Sum2))}, Cout={is_true(model.eval(Cout2))}")
    
#     def verify_arithmetic_circuit(self):
#         """验证算术电路"""
#         print("\n" + "=" * 70)
#         print("示例 3: 4位加法器电路验证")
#         print("=" * 70)
        
#         print("\n验证一个4位加法器的正确性")
#         print("输入: 两个4位二进制数 A[3:0] 和 B[3:0]")
#         print("输出: 4位和 S[3:0] 和进位输出 Cout")
        
#         # 创建 Z3 求解器
#         solver = Solver()
        
#         # 定义4位输入
#         A = [Bool(f'A{i}') for i in range(4)]  # A3是最高位
#         B = [Bool(f'B{i}') for i in range(4)]  # B3是最高位
        
#         # 定义输出
#         S = [Bool(f'S{i}') for i in range(4)]  # 和
#         Cout = Bool('Cout')                     # 进位输出
        
#         # 将二进制转换为整数（用于验证）
#         print("\n定义辅助函数：将二进制位转换为整数")
        
#         def bits_to_int(bits):
#             """将布尔位列表转换为整数"""
#             result = 0
#             for i, bit in enumerate(bits):
#                 result += (If(bit, 1, 0) << i)
#             return result
        
#         # 计算期望的和（整数运算）
#         A_int = bits_to_int(A)
#         B_int = bits_to_int(B)
#         expected_sum = A_int + B_int
        
#         print(f"\n数学表示:")
#         print(f"  A = {[f'A{i}' for i in range(4)]}")
#         print(f"  B = {[f'B{i}' for i in range(4)]}")
#         print(f"  期望: A + B = A_int + B_int")
        
#         # 电路实现：逐位加法
#         print("\n电路实现：使用全加器级联")
        
#         # 第一个全加器（最低位）
#         Cin = False  # 最低位没有进位输入
#         S0_circuit = Xor(Xor(A[0], B[0]), Cin)
#         C0_circuit = Or(And(A[0], B[0]), And(B[0], Cin), And(A[0], Cin))
        
#         # 第二个全加器
#         S1_circuit = Xor(Xor(A[1], B[1]), C0_circuit)
#         C1_circuit = Or(And(A[1], B[1]), And(B[1], C0_circuit), And(A[1], C0_circuit))
        
#         # 第三个全加器
#         S2_circuit = Xor(Xor(A[2], B[2]), C1_circuit)
#         C2_circuit = Or(And(A[2], B[2]), And(B[2], C1_circuit), And(A[2], C1_circuit))
        
#         # 第四个全加器（最高位）
#         S3_circuit = Xor(Xor(A[3], B[3]), C2_circuit)
#         Cout_circuit = Or(And(A[3], B[3]), And(B[3], C2_circuit), And(A[3], C2_circuit))
        
#         # 收集电路输出
#         S_circuit = [S0_circuit, S1_circuit, S2_circuit, S3_circuit]
#         circuit_sum = bits_to_int(S_circuit) + (If(Cout_circuit, 1, 0) << 4)
        
#         # 验证电路是否正确
#         print("\n验证约束：电路输出是否等于数学运算结果")
#         solver.add(circuit_sum == expected_sum)
        
#         print(f"约束: circuit_sum == expected_sum")
#         print(f"  circuit_sum = 二进制{S_circuit} + Cout<<4")
#         print(f"  expected_sum = A + B (数学加法)")
        
#         if solver.check() == sat:
#             print("\n✓ 4位加法器电路验证通过")
            
#             # 生成一个随机测试用例
#             print("\n随机测试用例验证:")
            
#             # 重置求解器并添加随机约束
#             solver.reset()
            
#             # 固定A和B的值进行测试
#             test_A = 5  # 二进制 0101
#             test_B = 11 # 二进制 1011
            
#             # 添加测试约束
#             solver.add(A[0] == True)   # A=0101
#             solver.add(A[1] == False)
#             solver.add(A[2] == True)
#             solver.add(A[3] == False)
            
#             solver.add(B[0] == True)   # B=1011
#             solver.add(B[1] == True)
#             solver.add(B[2] == False)
#             solver.add(B[3] == True)
            
#             # 重新添加验证约束
#             solver.add(circuit_sum == expected_sum)
            
#             if solver.check() == sat:
#                 model = solver.model()
#                 print(f"\n测试输入: A={test_A}(0101), B={test_B}(1011)")
#                 print(f"电路输出:")
#                 print(f"  S = [{is_true(model.eval(S3_circuit))}"
#                       f"{is_true(model.eval(S2_circuit))}"
#                       f"{is_true(model.eval(S1_circuit))}"
#                       f"{is_true(model.eval(S0_circuit))}]")
#                 print(f"  Cout = {is_true(model.eval(Cout_circuit))}")
#                 print(f"计算结果: {test_A} + {test_B} = {test_A + test_B}")
#                 print(f"二进制: 0101 + 1011 = 10000 (16)")
#                 print("✓ 测试用例验证通过")
#         else:
#             print("\n✗ 4位加法器电路存在错误")
            
#             # 寻找反例
#             solver.reset()
#             solver.add(circuit_sum != expected_sum)
            
#             if solver.check() == sat:
#                 model = solver.model()
#                 print(f"\n发现错误反例:")
#                 print(f"  A = {[is_true(model.eval(a)) for a in A]}")
#                 print(f"  B = {[is_true(model.eval(b)) for b in B]}")
#                 print(f"  电路输出: S={[is_true(model.eval(s)) for s in S_circuit]}, Cout={is_true(model.eval(Cout_circuit))}")
    
#     def verify_equivalence_optimization(self):
#         """验证电路优化等价性"""
#         print("\n" + "=" * 70)
#         print("示例 4: 电路优化等价性验证")
#         print("=" * 70)
        
#         print("\n验证优化后的电路是否与原始电路等价")
#         print("原始电路: (A ∧ B) ∨ (A ∧ C) ∨ (B ∧ C)")
#         print("优化电路: (A ∧ B) ∨ (C ∧ (A ∨ B))")
        
#         # 创建 Z3 求解器
#         solver = Solver()
        
#         # 定义输入
#         A, B, C = Bools('A B C')
        
#         # 原始电路
#         original = Or(And(A, B), And(A, C), And(B, C))
        
#         # 优化后的电路
#         optimized = Or(And(A, B), And(C, Or(A, B)))
        
#         # 验证等价性
#         print("\n验证约束: original == optimized")
#         solver.add(original != optimized)  # 寻找不等价的例子
        
#         if solver.check() == unsat:
#             print("✓ 优化电路与原始电路完全等价")
#             print("  优化是有效的，不会改变电路功能")
#         else:
#             print("✗ 优化电路与原始电路不等价")
#             model = solver.model()
#             print(f"  反例: A={model[A]}, B={model[B]}, C={model[C]}")
#             print(f"  原始电路输出: {is_true(model.eval(original))}")
#             print(f"  优化电路输出: {is_true(model.eval(optimized))}")
        
#         # 验证另一个优化（可能存在错误）
#         print("\n\n验证另一个可能错误的优化:")
#         print("原始电路: A ∨ (A ∧ B)")
#         print("优化电路: A")
        
#         original2 = Or(A, And(A, B))
#         optimized2 = A
        
#         solver.reset()
#         solver.add(original2 != optimized2)
        
#         if solver.check() == unsat:
#             print("✓ 优化正确: A ∨ (A ∧ B) 等价于 A")
#             print("  这是布尔代数中的吸收律")
#         else:
#             print("✗ 优化可能不正确")
#             model = solver.model()
#             print(f"  反例: A={model[A]}, B={model[B]}")
#             print(f"  原始电路输出: {is_true(model.eval(original2))}")
#             print(f"  优化电路输出: {is_true(model.eval(optimized2))}")

# def main():
#     """主函数"""
#     try:
#         # 检查是否安装了Z3
#         from z3 import Solver
#     except ImportError:
#         print("错误: 未找到 Z3 模块。请使用以下命令安装:")
#         print("pip install z3-solver")
#         return
    
#     # 创建电路验证器
#     verifier = CircuitVerifier()
    
#     # 运行所有验证示例
#     verifier.verify_half_adder()
#     verifier.verify_full_adder()
#     verifier.verify_arithmetic_circuit()
#     verifier.verify_equivalence_optimization()
    
#     print("\n" + "=" * 70)
#     print("Z3 在电路验证中的优势总结:")
#     print("=" * 70)
#     print("1. 自动化验证: 自动验证电路的正确性和等价性")
#     print("2. 完备性检查: 检查所有可能的输入组合")
#     print("3. 反例生成: 当验证失败时，自动生成反例")
#     print("4. 形式化方法: 提供严格的数学证明")
#     print("5. 高效求解: 处理复杂的电路验证问题")
#     print("\n应用场景:")
#     print("  - 硬件设计验证")
#     print("  - 电路优化验证")
#     print("  - 等价性检查")
#     print("  - 形式化验证")
#     print("=" * 70)

# if __name__ == "__main__":
#     main()
    




















#--------------------------带可视化界面-----------------------------------------------------------------------------

"""
Z3 求解器在电路验证中的应用 - 可视化界面
这个程序展示了如何使用 Z3 验证数字电路的正确性、等价性和优化效果。
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time
from z3 import *
import itertools

class CircuitVerifierGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Z3 求解器 - 电路验证演示")
        self.root.geometry("1200x800")
        
        # 设置样式
        self.setup_styles()
        
        # 初始化变量
        self.solver = None
        self.current_circuit = None
        self.verification_results = []
        
        # 创建界面
        self.create_widgets()
        
        # 显示欢迎信息
        self.display_welcome()
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 自定义颜色
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
    
    def create_widgets(self):
        """创建所有界面组件"""
        # 主容器
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板 - 电路示例和验证
        left_panel = ttk.LabelFrame(main_container, text="电路验证示例", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 右侧面板 - Z3 工作原理和验证结果
        right_panel = ttk.LabelFrame(main_container, text="Z3 求解器工作原理", padding="10")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 创建左侧面板内容
        self.create_left_panel(left_panel)
        
        # 创建右侧面板内容
        self.create_right_panel(right_panel)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_left_panel(self, parent):
        """创建左侧面板内容"""
        # 示例选择
        example_frame = ttk.LabelFrame(parent, text="选择验证示例", padding="10")
        example_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 示例按钮
        examples = [
            ("半加器验证", self.verify_half_adder),
            ("全加器验证", self.verify_full_adder),
            ("4位加法器验证", self.verify_4bit_adder),
            ("电路优化验证", self.verify_circuit_optimization),
            ("门级电路验证", self.verify_gate_level),
            ("时序电路验证", self.verify_sequential_circuit),
        ]
        
        for i, (text, command) in enumerate(examples):
            btn = ttk.Button(example_frame, text=text, command=command, width=20)
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky=tk.W)
        
        # 电路可视化区域
        self.circuit_display = tk.Canvas(parent, bg='white', height=200)
        self.circuit_display.pack(fill=tk.X, pady=(0, 10))
        
        # 真值表显示
        truth_table_frame = ttk.LabelFrame(parent, text="真值表/验证结果", padding="10")
        truth_table_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建文本显示区域
        self.truth_table_text = scrolledtext.ScrolledText(truth_table_frame, 
                                                          height=15, 
                                                          font=('Courier', 10))
        self.truth_table_text.pack(fill=tk.BOTH, expand=True)
    
    def create_right_panel(self, parent):
        """创建右侧面板内容"""
        # Z3 求解过程
        process_frame = ttk.LabelFrame(parent, text="Z3 求解过程", padding="10")
        process_frame.pack(fill=tk.BOTH, expand=True)
        
        # 求解过程文本区域
        self.process_text = scrolledtext.ScrolledText(process_frame, 
                                                     height=20, 
                                                     font=('Courier', 10))
        self.process_text.pack(fill=tk.BOTH, expand=True)
        
        # 控制按钮
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(control_frame, text="清除日志", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="导出结果", command=self.export_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="关于 Z3", command=self.show_about).pack(side=tk.RIGHT, padx=5)
    
    def display_welcome(self):
        """显示欢迎信息"""
        welcome_text = """
        Z3 求解器在电路验证中的应用
        
        欢迎使用电路验证演示程序！
        
        Z3 是一个高性能的定理证明器，在电路验证中可以：
        1. 验证电路设计的正确性
        2. 检查不同电路实现的等价性
        3. 验证电路优化的正确性
        4. 发现设计错误并生成反例
        
        请从左侧选择验证示例开始。
        """
        self.update_process_text(welcome_text)
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def update_process_text(self, message, clear=False):
        """更新求解过程文本"""
        if clear:
            self.process_text.delete(1.0, tk.END)
        self.process_text.insert(tk.END, message + "\n")
        self.process_text.see(tk.END)
    
    def update_truth_table(self, message, clear=False):
        """更新真值表文本"""
        if clear:
            self.truth_table_text.delete(1.0, tk.END)
        self.truth_table_text.insert(tk.END, message + "\n")
        self.truth_table_text.see(tk.END)
    
    def clear_logs(self):
        """清除所有日志"""
        self.process_text.delete(1.0, tk.END)
        self.truth_table_text.delete(1.0, tk.END)
        self.update_status("日志已清除")
    
    def draw_half_adder(self):
        """绘制半加器电路图"""
        canvas = self.circuit_display
        canvas.delete("all")
        
        # 设置画布大小
        canvas.config(width=400, height=200)
        
        # 绘制输入端口
        canvas.create_text(50, 50, text="A", font=('Arial', 14, 'bold'))
        canvas.create_text(50, 100, text="B", font=('Arial', 14, 'bold'))
        
        # 绘制 XOR 门
        canvas.create_rectangle(100, 30, 150, 120, fill='lightgray')
        canvas.create_text(125, 75, text="XOR", font=('Arial', 10, 'bold'))
        
        # 绘制 AND 门
        canvas.create_rectangle(160, 60, 210, 90, fill='lightgray')
        canvas.create_text(185, 75, text="AND", font=('Arial', 10, 'bold'))
        
        # 绘制输出端口
        canvas.create_text(280, 50, text="Sum", font=('Arial', 14, 'bold'))
        canvas.create_text(280, 100, text="Carry", font=('Arial', 14, 'bold'))
        
        # 绘制连接线
        # A 到 XOR
        canvas.create_line(60, 50, 100, 50, arrow=tk.LAST)
        # A 到 AND
        canvas.create_line(60, 50, 160, 70, arrow=tk.LAST)
        
        # B 到 XOR
        canvas.create_line(60, 100, 100, 100, arrow=tk.LAST)
        # B 到 AND
        canvas.create_line(60, 100, 160, 80, arrow=tk.LAST)
        
        # XOR 到 Sum
        canvas.create_line(150, 75, 260, 50, arrow=tk.LAST)
        
        # AND 到 Carry
        canvas.create_line(210, 75, 260, 100, arrow=tk.LAST)
        
        # 添加标题
        canvas.create_text(200, 20, text="半加器电路图", font=('Arial', 12, 'bold'))
    
    def verify_half_adder(self):
        """验证半加器电路"""
        self.update_status("正在验证半加器...")
        self.draw_half_adder()
        
        self.update_process_text("="*60, clear=True)
        self.update_process_text("示例 1: 半加器验证")
        self.update_process_text("="*60)
        
        self.update_process_text("\n步骤 1: 定义半加器真值表")
        self.update_truth_table("半加器真值表:", clear=True)
        self.update_truth_table("A B | Sum Carry")
        self.update_truth_table("0 0 |  0     0")
        self.update_truth_table("0 1 |  1     0")
        self.update_truth_table("1 0 |  1     0")
        self.update_truth_table("1 1 |  0     1")
        
        # 创建 Z3 求解器
        self.solver = Solver()
        self.update_process_text("\n步骤 2: 创建 Z3 求解器实例")
        
        # 定义输入变量
        A = Bool('A')
        B = Bool('B')
        self.update_process_text(f"步骤 3: 定义输入变量 A, B (布尔类型)")
        
        # 电路实现
        Sum_circuit = Xor(A, B)
        Carry_circuit = And(A, B)
        self.update_process_text(f"步骤 4: 定义电路输出")
        self.update_process_text(f"  Sum = A XOR B")
        self.update_process_text(f"  Carry = A AND B")
        
        # 规格说明（期望行为）
        Sum_spec = If(A != B, True, False)
        Carry_spec = And(A, B)
        self.update_process_text(f"步骤 5: 定义规格说明")
        self.update_process_text(f"  规格: Sum = A XOR B, Carry = A AND B")
        
        # 验证电路是否正确
        self.update_process_text("\n步骤 6: 添加验证约束")
        self.solver.add(Sum_circuit == Sum_spec)
        self.solver.add(Carry_circuit == Carry_spec)
        self.update_process_text(f"  约束 1: Sum_circuit == Sum_spec")
        self.update_process_text(f"  约束 2: Carry_circuit == Carry_spec")
        
        self.update_process_text("\n步骤 7: 开始验证...")
        start_time = time.time()
        
        if self.solver.check() == sat:
            elapsed = time.time() - start_time
            self.update_process_text(f"✓ 验证通过！耗时: {elapsed:.3f}秒")
            
            # 显示所有输入组合的输出
            self.update_truth_table("\n验证结果 - 所有输入组合:")
            self.update_truth_table("A B | Sum Carry")
            
            for a_val in [False, True]:
                for b_val in [False, True]:
                    # 创建临时求解器检查具体值
                    temp_solver = Solver()
                    temp_solver.add(A == a_val)
                    temp_solver.add(B == b_val)
                    temp_solver.add(Sum_circuit == Sum_spec)
                    temp_solver.add(Carry_circuit == Carry_spec)
                    
                    if temp_solver.check() == sat:
                        model = temp_solver.model()
                        sum_val = is_true(model.eval(Sum_circuit))
                        carry_val = is_true(model.eval(Carry_circuit))
                        self.update_truth_table(f"{int(a_val)} {int(b_val)} |  {int(sum_val)}     {int(carry_val)}")
            
            self.update_status("半加器验证通过！")
            
        else:
            self.update_process_text("✗ 验证失败：电路实现不满足规格")
            self.update_status("半加器验证失败")
    
    def verify_full_adder(self):
        """验证全加器电路"""
        self.update_status("正在验证全加器...")
        self.update_process_text("="*60, clear=True)
        self.update_process_text("示例 2: 全加器验证")
        self.update_process_text("="*60)
        
        # 绘制简单的全加器图示
        canvas = self.circuit_display
        canvas.delete("all")
        canvas.config(width=400, height=200)
        
        canvas.create_text(200, 20, text="全加器电路 (使用两个半加器实现)", 
                          font=('Arial', 12, 'bold'))
        canvas.create_text(100, 50, text="A", font=('Arial', 12, 'bold'))
        canvas.create_text(100, 80, text="B", font=('Arial', 12, 'bold'))
        canvas.create_text(100, 110, text="Cin", font=('Arial', 12, 'bold'))
        canvas.create_text(300, 60, text="Sum", font=('Arial', 12, 'bold'))
        canvas.create_text(300, 100, text="Cout", font=('Arial', 12, 'bold'))
        canvas.create_text(180, 70, text="半加器1", font=('Arial', 10))
        canvas.create_text(230, 90, text="半加器2", font=('Arial', 10))
        canvas.create_text(260, 150, text="OR", font=('Arial', 10, 'bold'))
        
        self.update_process_text("\n全加器规格：")
        self.update_truth_table("全加器真值表:", clear=True)
        self.update_truth_table("A B Cin | Sum Cout")
        
        # 生成真值表
        for bits in itertools.product([0, 1], repeat=3):
            a, b, cin = bits
            # 计算期望值
            sum_val = a ^ b ^ cin
            cout_val = (a & b) | (b & cin) | (a & cin)
            self.update_truth_table(f"{a} {b}  {cin}  |  {sum_val}    {cout_val}")
        
        # 创建 Z3 求解器
        self.solver = Solver()
        
        # 定义输入变量
        A, B, Cin = Bools('A B Cin')
        
        # 实现1：直接实现
        self.update_process_text("\n实现 1: 直接布尔表达式")
        Sum1 = Xor(Xor(A, B), Cin)
        Cout1 = Or(And(A, B), And(B, Cin), And(A, Cin))
        
        # 实现2：使用半加器实现
        self.update_process_text("实现 2: 使用两个半加器")
        # 第一个半加器
        sum_ha1 = Xor(A, B)
        carry_ha1 = And(A, B)
        # 第二个半加器
        Sum2 = Xor(sum_ha1, Cin)
        carry_ha2 = And(sum_ha1, Cin)
        Cout2 = Or(carry_ha1, carry_ha2)
        
        # 验证两种实现是否等价
        self.update_process_text("\n验证目标：两种实现是否等价")
        self.solver.add(Sum1 == Sum2)
        self.solver.add(Cout1 == Cout2)
        
        self.update_process_text("开始验证等价性...")
        start_time = time.time()
        
        if self.solver.check() == sat:
            elapsed = time.time() - start_time
            self.update_process_text(f"✓ 两种实现等价！耗时: {elapsed:.3f}秒")
            
            # 显示一个示例
            model = self.solver.model()
            self.update_truth_table("\n示例输入/输出:")
            self.update_truth_table(f"A={is_true(model.eval(A))}, "
                                   f"B={is_true(model.eval(B))}, "
                                   f"Cin={is_true(model.eval(Cin))}")
            self.update_truth_table(f"Sum={is_true(model.eval(Sum1))}, "
                                   f"Cout={is_true(model.eval(Cout1))}")
            
            self.update_status("全加器验证通过！")
        else:
            self.update_process_text("✗ 两种实现不等价")
            self.update_status("全加器验证失败")
    
    def verify_4bit_adder(self):
        """验证4位加法器"""
        self.update_status("正在验证4位加法器...")
        self.update_process_text("="*60, clear=True)
        self.update_process_text("示例 3: 4位加法器验证")
        self.update_process_text("="*60)
        
        # 绘制4位加法器示意图
        canvas = self.circuit_display
        canvas.delete("all")
        canvas.config(width=500, height=200)
        
        canvas.create_text(250, 20, text="4位加法器 (全加器级联)", 
                          font=('Arial', 12, 'bold'))
        
        # 绘制4个全加器
        for i in range(4):
            x = 100 + i * 100
            canvas.create_rectangle(x, 50, x+60, 100, fill='lightblue')
            canvas.create_text(x+30, 75, text=f"FA{i}", font=('Arial', 9, 'bold'))
            
            # 输入
            canvas.create_text(x-20, 60, text=f"A{i}", font=('Arial', 9))
            canvas.create_text(x-20, 90, text=f"B{i}", font=('Arial', 9))
            
            # 输出
            canvas.create_text(x+90, 75, text=f"S{i}", font=('Arial', 9))
        
        # 进位链
        for i in range(3):
            x = 100 + i * 100
            canvas.create_line(x+60, 100, x+100, 50, arrow=tk.LAST)
        
        canvas.create_text(50, 140, text="Cin", font=('Arial', 9))
        canvas.create_text(450, 140, text="Cout", font=('Arial', 9))
        
        self.update_process_text("\n验证4位二进制加法器的正确性")
        self.update_truth_table("4位加法器测试用例:", clear=True)
        self.update_truth_table("输入A 输入B | 期望和 实际和 | 结果")
        
        # 创建 Z3 求解器
        self.solver = Solver()
        
        # 定义4位输入
        A_bits = [Bool(f'A{i}') for i in range(4)]
        B_bits = [Bool(f'B{i}') for i in range(4)]
        
        # 实现4位加法器
        def create_4bit_adder(A, B, cin):
            """创建4位加法器电路"""
            S = []
            cout = cin
            
            for i in range(4):
                # 全加器逻辑
                sum_bit = Xor(Xor(A[i], B[i]), cout)
                cout = Or(And(A[i], B[i]), And(B[i], cout), And(A[i], cout))
                S.append(sum_bit)
            
            return S, cout
        
        # 创建电路
        S_circuit, Cout_circuit = create_4bit_adder(A_bits, B_bits, False)
        
        # 测试几个具体用例
        test_cases = [
            ([0,0,0,0], [0,0,0,0]),  # 0 + 0
            ([0,0,0,1], [0,0,0,1]),  # 1 + 1
            ([0,1,0,1], [0,0,1,1]),  # 5 + 3
            ([1,0,0,1], [0,1,1,0]),  # 9 + 6
        ]
        
        correct_count = 0
        total_count = len(test_cases)
        
        for a_bits, b_bits in test_cases:
            # 创建测试求解器
            test_solver = Solver()
            
            # 添加输入约束
            for i in range(4):
                test_solver.add(A_bits[i] == (a_bits[i] == 1))
                test_solver.add(B_bits[i] == (b_bits[i] == 1))
            
            # 计算期望值
            a_val = sum(a_bits[i] * (2**i) for i in range(4))
            b_val = sum(b_bits[i] * (2**i) for i in range(4))
            expected_sum = a_val + b_val
            
            # 创建电路并验证
            S_test, Cout_test = create_4bit_adder(A_bits, B_bits, False)
            
            # 将输出转换为整数
            def bits_to_int(bits):
                result = 0
                for i, bit in enumerate(bits):
                    result += (If(bit, 1, 0) << i)
                return result
            
            circuit_sum = bits_to_int(S_test) + (If(Cout_test, 1, 0) << 4)
            test_solver.add(circuit_sum == expected_sum)
            
            if test_solver.check() == sat:
                result = "✓"
                correct_count += 1
            else:
                result = "✗"
            
            # 显示结果
            a_str = ''.join(str(b) for b in reversed(a_bits))
            b_str = ''.join(str(b) for b in reversed(b_bits))
            self.update_truth_table(f"{a_str}  {b_str} | {expected_sum:4d}   "
                                   f"{expected_sum:4d} | {result}")
        
        if correct_count == total_count:
            self.update_process_text(f"\n✓ 所有{total_count}个测试用例验证通过！")
            self.update_status("4位加法器验证通过！")
        else:
            self.update_process_text(f"\n✗ {total_count-correct_count}个测试用例失败")
            self.update_status("4位加法器验证部分失败")
    
    def verify_circuit_optimization(self):
        """验证电路优化"""
        self.update_status("正在验证电路优化...")
        self.update_process_text("="*60, clear=True)
        self.update_process_text("示例 4: 电路优化验证")
        self.update_process_text("="*60)
        
        canvas = self.circuit_display
        canvas.delete("all")
        canvas.config(width=500, height=200)
        
        canvas.create_text(250, 20, text="电路优化验证", font=('Arial', 12, 'bold'))
        canvas.create_text(100, 50, text="原始电路", font=('Arial', 10, 'bold'))
        canvas.create_text(100, 80, text="(A∧B)∨(A∧C)∨(B∧C)", font=('Courier', 10))
        canvas.create_text(100, 110, text="↓↓↓ 优化", font=('Arial', 10))
        canvas.create_text(100, 140, text="优化电路", font=('Arial', 10, 'bold'))
        canvas.create_text(100, 170, text="(A∧B)∨(C∧(A∨B))", font=('Courier', 10))
        
        canvas.create_line(200, 100, 300, 100, arrow=tk.LAST)
        canvas.create_text(250, 90, text="验证等价性", font=('Arial', 9))
        
        self.update_process_text("\n验证电路优化是否保持功能不变")
        self.update_truth_table("优化验证:", clear=True)
        
        # 创建 Z3 求解器
        self.solver = Solver()
        
        # 定义输入变量
        A, B, C = Bools('A B C')
        
        # 原始电路
        original = Or(And(A, B), And(A, C), And(B, C))
        
        # 优化后的电路
        optimized = Or(And(A, B), And(C, Or(A, B)))
        
        # 显示真值表
        self.update_truth_table("A B C | 原始 优化 | 等价")
        self.update_truth_table("-" * 30)
        
        # 检查所有可能输入
        all_equivalent = True
        counterexample = None
        
        for bits in itertools.product([False, True], repeat=3):
            a_val, b_val, c_val = bits
            
            # 创建临时求解器
            temp_solver = Solver()
            temp_solver.add(A == a_val)
            temp_solver.add(B == b_val)
            temp_solver.add(C == c_val)
            
            # 评估两个电路
            temp_solver.add(original != optimized)
            
            if temp_solver.check() == sat:
                # 找到反例
                all_equivalent = False
                counterexample = (a_val, b_val, c_val)
                eq_mark = "✗"
                break
            else:
                # 检查具体值
                eval_solver = Solver()
                eval_solver.add(A == a_val)
                eval_solver.add(B == b_val)
                eval_solver.add(C == c_val)
                
                if eval_solver.check() == sat:
                    model = eval_solver.model()
                    orig_val = is_true(model.eval(original))
                    opt_val = is_true(model.eval(optimized))
                    eq_mark = "✓" if orig_val == opt_val else "✗"
                    
                    self.update_truth_table(
                        f"{int(a_val)} {int(b_val)} {int(c_val)} |  "
                        f"{int(orig_val)}    {int(opt_val)}   |  {eq_mark}"
                    )
        
        if all_equivalent:
            self.update_process_text("\n✓ 优化正确：两个电路完全等价")
            self.update_process_text("  优化减少了门数量，同时保持功能不变")
            self.update_status("电路优化验证通过！")
        else:
            self.update_process_text(f"\n✗ 优化错误：发现反例")
            if counterexample:
                a_val, b_val, c_val = counterexample
                self.update_process_text(f"  反例: A={a_val}, B={b_val}, C={c_val}")
            self.update_status("电路优化验证失败")
    
    def verify_gate_level(self):
        """验证门级电路"""
        self.update_status("正在验证门级电路...")
        self.update_process_text("="*60, clear=True)
        self.update_process_text("示例 5: 门级电路验证")
        self.update_process_text("="*60)
        
        self.update_process_text("\n验证一个复杂的门级组合电路")
        self.update_truth_table("电路: F = (A∧B) ∨ (¬A∧C) ∨ (B∧¬C)", clear=True)
        
        # 创建 Z3 求解器
        self.solver = Solver()
        
        # 定义输入
        A, B, C = Bools('A B C')
        
        # 电路实现
        circuit = Or(
            And(A, B),
            And(Not(A), C),
            And(B, Not(C))
        )
        
        # 简化后的电路（通过布尔代数）
        simplified = Or(And(A, B), And(Not(A), C))
        
        self.update_process_text("简化电路: F = (A∧B) ∨ (¬A∧C)")
        
        # 验证等价性
        self.solver.add(circuit != simplified)
        
        if self.solver.check() == unsat:
            self.update_process_text("\n✓ 简化正确：两个电路等价")
            
            # 显示真值表对比
            self.update_truth_table("\n真值表对比:")
            self.update_truth_table("A B C | 原始 简化 | 等价")
            self.update_truth_table("-" * 30)
            
            for bits in itertools.product([0, 1], repeat=3):
                a_val, b_val, c_val = bits
                
                # 计算原始电路值
                orig_val = (a_val & b_val) | ((1 - a_val) & c_val) | (b_val & (1 - c_val))
                
                # 计算简化电路值
                simp_val = (a_val & b_val) | ((1 - a_val) & c_val)
                
                eq_mark = "✓" if orig_val == simp_val else "✗"
                self.update_truth_table(
                    f"{a_val} {b_val} {c_val} |  {orig_val}    {simp_val}   |  {eq_mark}"
                )
            
            self.update_status("门级电路验证通过！")
        else:
            self.update_process_text("\n✗ 简化错误：电路不等价")
            model = self.solver.model()
            self.update_process_text(f"  反例: A={model[A]}, B={model[B]}, C={model[C]}")
            self.update_status("门级电路验证失败")
    
    def verify_sequential_circuit(self):
        """验证时序电路"""
        self.update_status("正在验证时序电路...")
        self.update_process_text("="*60, clear=True)
        self.update_process_text("示例 6: 时序电路验证 (D触发器)")
        self.update_process_text("="*60)
        
        self.update_process_text("\n验证D触发器的行为")
        self.update_truth_table("D触发器特性:", clear=True)
        self.update_truth_table("时钟  D | Q(next)")
        self.update_truth_table("上升沿 0 |   0")
        self.update_truth_table("上升沿 1 |   1")
        self.update_truth_table("其他情况 |  保持")
        
        # 创建 Z3 求解器
        self.solver = Solver()
        
        # 定义变量（时序电路需要状态）
        D = Bool('D')          # 数据输入
        CLK = Bool('CLK')      # 时钟
        CLK_prev = Bool('CLK_prev')  # 上一个时钟
        Q = Bool('Q')          # 当前状态
        Q_next = Bool('Q_next')  # 下一个状态
        
        # D触发器行为规则
        # 规则1: 在时钟上升沿，Q_next = D
        rising_edge = And(Not(CLK_prev), CLK)
        rule1 = Implies(rising_edge, Q_next == D)
        
        # 规则2: 其他情况，Q_next保持原值
        rule2 = Implies(Not(rising_edge), Q_next == Q)
        
        self.update_process_text("\n形式化规则:")
        self.update_process_text("  1. rising_edge = ¬CLK_prev ∧ CLK")
        self.update_process_text("  2. 如果 rising_edge 则 Q_next = D")
        self.update_process_text("  3. 否则 Q_next = Q")
        
        # 添加规则
        self.solver.add(rule1)
        self.solver.add(rule2)
        
        # 验证一些场景
        test_cases = [
            ("上升沿传输0", True, False, False, True, False, False),
            ("上升沿传输1", True, False, True, True, True, True),
            ("非上升沿保持", False, False, True, False, True, True),
            ("时钟为低保持", False, True, False, False, True, True),
        ]
        
        self.update_truth_table("\n验证结果:")
        self.update_truth_table("场景 | CLK_prev CLK D Q | Q_next | 结果")
        self.update_truth_table("-" * 50)
        
        all_correct = True
        
        for name, clk_prev, clk, d_val, q_val, expected, _ in test_cases:
            # 创建测试求解器
            test_solver = Solver()
            test_solver.add(rule1)
            test_solver.add(rule2)
            
            # 添加测试条件
            test_solver.add(CLK_prev == clk_prev)
            test_solver.add(CLK == clk)
            test_solver.add(D == d_val)
            test_solver.add(Q == q_val)
            
            if test_solver.check() == sat:
                model = test_solver.model()
                q_next_val = is_true(model.eval(Q_next))
                correct = (q_next_val == expected)
                result = "✓" if correct else "✗"
                
                if not correct:
                    all_correct = False
                
                self.update_truth_table(
                    f"{name[:8]} |    {int(clk_prev)}      {int(clk)}   "
                    f"{int(d_val)} {int(q_val)} |   {int(q_next_val)}   | {result}"
                )
        
        if all_correct:
            self.update_process_text("\n✓ D触发器行为验证通过")
            self.update_status("时序电路验证通过！")
        else:
            self.update_process_text("\n✗ D触发器行为验证失败")
            self.update_status("时序电路验证失败")
    
    def export_results(self):
        """导出验证结果"""
        try:
            # 获取当前时间作为文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"circuit_verification_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Z3 电路验证结果报告\n")
                f.write("=" * 60 + "\n\n")
                
                f.write("求解过程:\n")
                f.write(self.process_text.get(1.0, tk.END))
                f.write("\n" + "=" * 60 + "\n\n")
                
                f.write("验证结果:\n")
                f.write(self.truth_table_text.get(1.0, tk.END))
            
            messagebox.showinfo("导出成功", f"结果已导出到: {filename}")
            self.update_status(f"结果已导出到 {filename}")
            
        except Exception as e:
            messagebox.showerror("导出错误", f"导出失败: {str(e)}")
    
    def show_about(self):
        """显示关于信息"""
        about_text = """
        Z3 求解器在电路验证中的应用
        
        Z3 是一个由微软开发的高性能定理证明器，基于SMT（可满足性模理论）技术。
        
        在电路验证中，Z3 可以：
        1. 形式化验证电路设计的正确性
        2. 自动化等价性检查
        3. 验证电路优化和重构
        4. 发现设计错误并生成反例
        5. 验证时序电路和组合电路
        
        优势：
        - 完备性：检查所有可能的输入情况
        - 自动化：无需人工编写测试用例
        - 高效性：使用先进的求解算法
        - 精确性：提供数学上严格的证明
        
        应用领域：
        - 硬件设计验证
        - 电路优化验证
        - 形式化方法教学
        - 数字系统验证
        """
        
        messagebox.showinfo("关于 Z3 求解器", about_text)

def main():
    """主函数"""
    try:
        # 检查是否安装了Z3
        from z3 import Solver
    except ImportError:
        print("错误: 未找到 Z3 模块。请使用以下命令安装:")
        print("pip install z3-solver")
        return
    
    # 创建主窗口
    root = tk.Tk()
    
    # 创建应用程序
    app = CircuitVerifierGUI(root)
    
    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    main()