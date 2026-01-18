# """
# 使用 Z3 求解器解决数独问题
# Z3 是一个高性能的定理证明器，可以处理各种约束满足问题
# """

# from z3 import Solver, Int, Distinct, And, sat

# def solve_sudoku_z3(puzzle):
#     """
#     使用 Z3 求解器解决数独问题
    
#     参数:
#     puzzle: 9x9 的数独矩阵，0 表示空白格
    
#     返回:
#     如果找到解，返回解矩阵；否则返回 None
#     """
#     # 创建 Z3 求解器实例
#     solver = Solver()
    
#     # 创建 9x9 的整数变量矩阵，每个变量表示数独中的一个格子
#     # 每个变量的取值范围是 1 到 9
#     cells = [[Int(f'cell_{i}_{j}') for j in range(9)] for i in range(9)]
    
#     print("步骤 1: 创建变量和基本约束")
#     print(f"创建了 {9*9} 个整数变量，每个变量代表数独中的一个格子")
#     print("-" * 50)
    
#     # 添加基本约束：每个格子的值必须在 1 到 9 之间
#     for i in range(9):
#         for j in range(9):
#             solver.add(cells[i][j] >= 1)
#             solver.add(cells[i][j] <= 9)
    
#     print("步骤 2: 添加数独规则约束")
#     print("规则 1: 每行中的数字 1-9 各出现一次")
    
#     # 约束 1: 每行中的数字 1-9 各出现一次
#     for i in range(9):
#         solver.add(Distinct(cells[i]))
    
#     print("规则 2: 每列中的数字 1-9 各出现一次")
    
#     # 约束 2: 每列中的数字 1-9 各出现一次
#     for j in range(9):
#         # 提取第 j 列的所有单元格
#         column = [cells[i][j] for i in range(9)]
#         solver.add(Distinct(column))
    
#     print("规则 3: 每个 3x3 宫中的数字 1-9 各出现一次")
    
#     # 约束 3: 每个 3x3 宫中的数字 1-9 各出现一次
#     for block_i in range(3):
#         for block_j in range(3):
#             # 提取 3x3 宫的所有单元格
#             block_cells = []
#             for i in range(3):
#                 for j in range(3):
#                     block_cells.append(cells[block_i*3 + i][block_j*3 + j])
#             solver.add(Distinct(block_cells))
    
#     print("步骤 3: 添加已知数字的约束")
    
#     # 添加已知数字的约束
#     known_count = 0
#     for i in range(9):
#         for j in range(9):
#             if puzzle[i][j] != 0:
#                 solver.add(cells[i][j] == puzzle[i][j])
#                 known_count += 1
    
#     print(f"添加了 {known_count} 个已知数字作为约束")
#     print("-" * 50)
    
#     print("步骤 4: 开始求解")
#     print("Z3 求解器正在处理约束条件...")
    
#     # 检查是否存在解
#     if solver.check() == sat:
#         print("✓ 找到解！")
#         print("-" * 50)
        
#         # 获取解模型
#         model = solver.model()
        
#         # 从模型中提取解
#         solution = [[0 for _ in range(9)] for _ in range(9)]
#         for i in range(9):
#             for j in range(9):
#                 solution[i][j] = model[cells[i][j]].as_long()
        
#         return solution
#     else:
#         print("✗ 无解")
#         return None

# def print_sudoku(grid, title="数独"):
#     """
#     打印数独网格
    
#     参数:
#     grid: 9x9 的数独矩阵
#     title: 打印的标题
#     """
#     print(f"\n{title}:")
#     print("+" + "---" * 9 + "+")
    
#     for i in range(9):
#         if i % 3 == 0 and i != 0:
#             print("+" + "---" * 9 + "+")
        
#         row_str = "|"
#         for j in range(9):
#             if j % 3 == 0 and j != 0:
#                 row_str += "|"
#             row_str += f" {grid[i][j] if grid[i][j] != 0 else '.'} "
#         row_str += "|"
#         print(row_str)
    
#     print("+" + "---" * 9 + "+")

# def main():
#     """主函数：演示 Z3 求解器解决数独问题"""
#     print("=" * 60)
#     print("Z3 求解器在数独求解中的应用演示")
#     print("=" * 60)
    
#     # 定义一个中等难度的数独问题
#     # 0 表示空白格
#     puzzle = [
#         [5, 3, 0, 0, 7, 0, 0, 0, 0],
#         [6, 0, 0, 1, 9, 5, 0, 0, 0],
#         [0, 9, 8, 0, 0, 0, 0, 6, 0],
#         [8, 0, 0, 0, 6, 0, 0, 0, 3],
#         [4, 0, 0, 8, 0, 3, 0, 0, 1],
#         [7, 0, 0, 0, 2, 0, 0, 0, 6],
#         [0, 6, 0, 0, 0, 0, 2, 8, 0],
#         [0, 0, 0, 4, 1, 9, 0, 0, 5],
#         [0, 0, 0, 0, 8, 0, 0, 7, 9]
#     ]
    
#     # 打印原始数独问题
#     print_sudoku(puzzle, "原始数独问题")
    
#     print("\n" + "=" * 60)
#     print("开始使用 Z3 求解器求解...")
#     print("=" * 60)
    
#     # 使用 Z3 求解器求解数独
#     solution = solve_sudoku_z3(puzzle)
    
#     if solution:
#         # 打印求解结果
#         print_sudoku(solution, "Z3 求解器找到的解")
        
#         # 验证解的正确性
#         print("\n验证解的正确性:")
#         print("1. 每行是否包含 1-9 所有数字？", all(set(row) == set(range(1, 10)) for row in solution))
        
#         # 验证每列
#         cols_valid = True
#         for j in range(9):
#             col = [solution[i][j] for i in range(9)]
#             if set(col) != set(range(1, 10)):
#                 cols_valid = False
#                 break
#         print("2. 每列是否包含 1-9 所有数字？", cols_valid)
        
#         # 验证每个 3x3 宫
#         blocks_valid = True
#         for block_i in range(3):
#             for block_j in range(3):
#                 block = []
#                 for i in range(3):
#                     for j in range(3):
#                         block.append(solution[block_i*3 + i][block_j*3 + j])
#                 if set(block) != set(range(1, 10)):
#                     blocks_valid = False
#                     break
#         print("3. 每个 3x3 宫是否包含 1-9 所有数字？", blocks_valid)
        
#         print("\n" + "=" * 60)
#         print("总结: Z3 求解器通过以下步骤解决数独问题:")
#         print("1. 将数独问题转化为逻辑变量和约束")
#         print("2. 添加数独规则约束（行、列、宫的唯一性）")
#         print("3. 添加已知数字作为额外约束")
#         print("4. 使用定理证明技术寻找满足所有约束的解")
#         print("=" * 60)
#     else:
#         print("未找到解")

# if __name__ == "__main__":
#     # 安装提示
#     try:
#         from z3 import Solver
#     except ImportError:
#         print("错误: 未找到 Z3 模块。请使用以下命令安装:")
#         print("pip install z3-solver")
#         exit(1)
    
#     main()






















#  --------------------------------------------------有可视化界面------------------------------------------------------------------------------------
"""
Z3 求解器在数独求解中的应用 - 可视化界面
这个程序展示了如何将约束满足问题转化为 Z3 可求解的形式，
并通过可视化界面展示求解过程和结果。
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
from z3 import Solver, Int, Distinct, And, sat, unsat, unknown
import threading

class SudokuSolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Z3 求解器 - 数独求解演示")
        self.root.geometry("1000x700")
        
        # 初始化变量
        self.puzzle = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = None
        self.solving = False
        
        # 创建界面
        self.create_widgets()
        
        # 设置默认数独（中等难度）
        self.set_default_puzzle()
        
        # 更新显示
        self.update_display()
    
    def create_widgets(self):
        """创建所有界面组件"""
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="Z3 求解器在数独求解中的应用演示",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Z3 求解器介绍
        intro_text = """
        Z3 是一个由微软开发的高性能定理证明器，可以处理各种约束满足问题。
        在数独求解中，Z3 将数独规则转化为逻辑约束，然后自动找到满足所有约束的解。
        """
        intro_label = ttk.Label(main_frame, text=intro_text, wraplength=800, justify="center")
        intro_label.grid(row=1, column=0, columnspan=3, pady=10)
        
        # 数独网格框架
        self.grid_frame = ttk.Frame(main_frame, relief="solid", padding=5)
        self.grid_frame.grid(row=2, column=0, padx=10, pady=10, sticky=tk.N)
        
        # 创建数独网格
        self.cells = []
        for i in range(9):
            row_cells = []
            for j in range(9):
                # 确定边框样式
                border_width = 3 if i % 3 == 0 else 1
                border_width2 = 3 if j % 3 == 0 else 1
                
                # 创建单元格
                cell = tk.Entry(
                    self.grid_frame,
                    width=3,
                    font=("Arial", 20, "bold"),
                    justify="center",
                    validate="key",
                    validatecommand=(self.grid_frame.register(self.validate_input), "%P")
                )
                cell.grid(row=i, column=j, padx=(0, 1), pady=(0, 1))
                cell.bind("<FocusOut>", lambda e, row=i, col=j: self.cell_changed(row, col))
                row_cells.append(cell)
            self.cells.append(row_cells)
        
        # 控制面板框架
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding=10)
        control_frame.grid(row=2, column=1, padx=10, pady=10, sticky=tk.N)
        
        # 按钮
        ttk.Button(control_frame, text="清除所有", command=self.clear_all).grid(row=0, column=0, pady=5, sticky=tk.W+tk.E)
        ttk.Button(control_frame, text="设置默认题目", command=self.set_default_puzzle).grid(row=1, column=0, pady=5, sticky=tk.W+tk.E)
        ttk.Button(control_frame, text="随机题目", command=self.random_puzzle).grid(row=2, column=0, pady=5, sticky=tk.W+tk.E)
        ttk.Button(control_frame, text="求解", command=self.solve_puzzle).grid(row=3, column=0, pady=10, sticky=tk.W+tk.E)
        ttk.Button(control_frame, text="逐步求解", command=self.step_by_step_solve).grid(row=4, column=0, pady=5, sticky=tk.W+tk.E)
        ttk.Button(control_frame, text="验证当前", command=self.verify_solution).grid(row=5, column=0, pady=5, sticky=tk.W+tk.E)
        
        # 文件操作按钮
        ttk.Button(control_frame, text="保存题目", command=self.save_puzzle).grid(row=6, column=0, pady=10, sticky=tk.W+tk.E)
        ttk.Button(control_frame, text="加载题目", command=self.load_puzzle).grid(row=7, column=0, pady=5, sticky=tk.W+tk.E)
        
        # 求解过程显示框架
        process_frame = ttk.LabelFrame(main_frame, text="Z3 求解过程", padding=10)
        process_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # 求解过程文本框
        self.process_text = tk.Text(process_frame, height=10, width=80, font=("Courier", 10))
        self.process_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(process_frame, orient="vertical", command=self.process_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.process_text.configure(yscrollcommand=scrollbar.set)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief="sunken")
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Z3 工作原理说明
        explanation_frame = ttk.LabelFrame(main_frame, text="Z3 求解器工作原理", padding=10)
        explanation_frame.grid(row=2, column=2, rowspan=2, padx=10, pady=10, sticky=tk.N)
        
        explanation_text = """
        Z3 求解数独的步骤：
        
        1. 变量定义：
           - 创建 81 个整数变量 x[i][j]
           - 每个变量表示格子(i,j)的值
        
        2. 约束条件：
           - 范围约束：1 ≤ x[i][j] ≤ 9
           - 行约束：Distinct(x[i][0], ..., x[i][8])
           - 列约束：Distinct(x[0][j], ..., x[8][j])
           - 宫约束：Distinct(3x3块内的9个变量)
           - 已知值：x[i][j] = 已知值
        
        3. 求解：
           - 将约束转化为SMT公式
           - 使用SAT/SMT求解技术
           - 寻找满足所有约束的解
        
        4. 输出：
           - 提取模型中的变量值
           - 验证解的正确性
        """
        explanation_label = ttk.Label(explanation_frame, text=explanation_text, wraplength=300, justify="left")
        explanation_label.grid(row=0, column=0, sticky=tk.W)
    
    def validate_input(self, value):
        """验证输入是否有效（1-9或空）"""
        if value == "" or (len(value) == 1 and value.isdigit() and 1 <= int(value) <= 9):
            return True
        return False
    
    def cell_changed(self, row, col):
        """单元格内容改变时的处理"""
        value = self.cells[row][col].get()
        if value == "":
            self.puzzle[row][col] = 0
        else:
            self.puzzle[row][col] = int(value)
    
    def clear_all(self):
        """清除所有单元格"""
        for i in range(9):
            for j in range(9):
                self.cells[i][j].delete(0, tk.END)
                self.puzzle[i][j] = 0
        self.solution = None
        self.update_status("已清除所有单元格")
    
    def set_default_puzzle(self):
        """设置默认数独题目"""
        default_puzzle = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ]
        
        self.load_puzzle_from_data(default_puzzle)
        self.update_status("已加载默认数独题目")
    
    def random_puzzle(self):
        """生成随机数独题目（这里使用一个预设的简单题目）"""
        random_puzzle = [
            [0, 0, 0, 2, 6, 0, 7, 0, 1],
            [6, 8, 0, 0, 7, 0, 0, 9, 0],
            [1, 9, 0, 0, 0, 4, 5, 0, 0],
            [8, 2, 0, 1, 0, 0, 0, 4, 0],
            [0, 0, 4, 6, 0, 2, 9, 0, 0],
            [0, 5, 0, 0, 0, 3, 0, 2, 8],
            [0, 0, 9, 3, 0, 0, 0, 7, 4],
            [0, 4, 0, 0, 5, 0, 0, 3, 6],
            [7, 0, 3, 0, 1, 8, 0, 0, 0]
        ]
        
        self.load_puzzle_from_data(random_puzzle)
        self.update_status("已生成随机数独题目")
    
    def load_puzzle_from_data(self, puzzle_data):
        """从数据加载数独"""
        for i in range(9):
            for j in range(9):
                self.puzzle[i][j] = puzzle_data[i][j]
                self.cells[i][j].delete(0, tk.END)
                if puzzle_data[i][j] != 0:
                    self.cells[i][j].insert(0, str(puzzle_data[i][j]))
        
        self.solution = None
        self.update_display()
    
    def solve_puzzle(self):
        """使用 Z3 求解数独"""
        if self.solving:
            return
        
        self.solving = True
        self.update_status("开始求解...")
        
        # 在新线程中求解，避免界面卡顿
        thread = threading.Thread(target=self._solve_in_thread)
        thread.daemon = True
        thread.start()
    
    def _solve_in_thread(self):
        """在线程中执行求解"""
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 清空过程显示
            self.process_text.delete(1.0, tk.END)
            self.log_process("=" * 60)
            self.log_process("开始 Z3 求解过程")
            self.log_process("=" * 60)
            
            # 创建 Z3 求解器
            solver = Solver()
            self.log_process("1. 创建 Z3 求解器实例")
            
            # 创建变量
            cells = [[Int(f'x_{i}_{j}') for j in range(9)] for i in range(9)]
            self.log_process(f"2. 创建 {9*9} 个整数变量: x_0_0 到 x_8_8")
            
            # 添加约束1：每个变量的值在1-9之间
            self.log_process("3. 添加约束：每个格子的值必须在 1-9 之间")
            for i in range(9):
                for j in range(9):
                    solver.add(cells[i][j] >= 1, cells[i][j] <= 9)
            
            # 添加约束2：每行数字互不相同
            self.log_process("4. 添加约束：每行的数字必须互不相同")
            for i in range(9):
                solver.add(Distinct(cells[i]))
            
            # 添加约束3：每列数字互不相同
            self.log_process("5. 添加约束：每列的数字必须互不相同")
            for j in range(9):
                column = [cells[i][j] for i in range(9)]
                solver.add(Distinct(column))
            
            # 添加约束4：每个3x3宫数字互不相同
            self.log_process("6. 添加约束：每个3x3宫的数字必须互不相同")
            for block_i in range(3):
                for block_j in range(3):
                    block_cells = []
                    for i in range(3):
                        for j in range(3):
                            block_cells.append(cells[block_i*3 + i][block_j*3 + j])
                    solver.add(Distinct(block_cells))
            
            # 添加已知数字约束
            self.log_process("7. 添加已知数字约束")
            known_count = 0
            for i in range(9):
                for j in range(9):
                    if self.puzzle[i][j] != 0:
                        solver.add(cells[i][j] == self.puzzle[i][j])
                        known_count += 1
            
            self.log_process(f"   添加了 {known_count} 个已知数字作为约束")
            
            # 检查约束数量
            self.log_process(f"8. 总共添加了 {len(solver.assertions())} 条约束")
            
            # 开始求解
            self.log_process("9. 开始求解...")
            self.log_process("   Z3 正在将约束转化为SMT公式...")
            
            result = solver.check()
            solve_time = time.time() - start_time
            
            if result == sat:
                self.log_process(f"10. 找到解！求解时间: {solve_time:.3f} 秒")
                
                # 获取解
                model = solver.model()
                self.solution = [[0 for _ in range(9)] for _ in range(9)]
                
                for i in range(9):
                    for j in range(9):
                        self.solution[i][j] = model[cells[i][j]].as_long()
                
                # 在主线程中更新显示
                self.root.after(0, self._update_solution_display)
                
                self.log_process("11. 解已找到并显示在界面上")
                self.update_status(f"求解完成！耗时: {solve_time:.3f} 秒")
                
            elif result == unsat:
                self.log_process("10. 无解：约束矛盾，数独无解")
                self.root.after(0, lambda: messagebox.showwarning("无解", "该数独无解！"))
                self.update_status("数独无解")
            else:
                self.log_process("10. 求解未知：Z3无法确定是否有解")
                self.root.after(0, lambda: messagebox.showwarning("求解失败", "Z3无法求解此数独"))
                self.update_status("求解失败")
            
            self.log_process("=" * 60)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"求解过程中出错: {str(e)}"))
            self.update_status(f"错误: {str(e)}")
        finally:
            self.solving = False
    
    def _update_solution_display(self):
        """更新解决方案显示"""
        if self.solution:
            for i in range(9):
                for j in range(9):
                    if self.puzzle[i][j] == 0:  # 只更新空白的单元格
                        self.cells[i][j].delete(0, tk.END)
                        self.cells[i][j].insert(0, str(self.solution[i][j]))
                        self.cells[i][j].config(fg="blue")  # 用蓝色显示求解出的数字
    
    def step_by_step_solve(self):
        """逐步求解（演示模式）"""
        # 这里简化实现，实际实现需要更复杂的步骤展示
        self.process_text.delete(1.0, tk.END)
        self.log_process("逐步求解模式演示：")
        self.log_process("1. 首先，Z3 会创建所有变量")
        self.log_process("2. 然后，添加基本约束：每个变量在1-9之间")
        self.log_process("3. 接着，添加行、列、宫的互异性约束")
        self.log_process("4. 最后，添加已知数字约束并求解")
        self.log_process("...")
        self.log_process("（这是一个简化演示，实际Z3内部步骤更复杂）")
        
        # 然后进行正常求解
        self.solve_puzzle()
    
    def verify_solution(self):
        """验证当前数独是否正确"""
        # 收集当前网格的值
        current = [[0 for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                value = self.cells[i][j].get()
                current[i][j] = int(value) if value.isdigit() else 0
        
        # 检查是否所有单元格都已填写
        empty_cells = sum(1 for row in current for cell in row if cell == 0)
        if empty_cells > 0:
            messagebox.showinfo("验证", f"还有 {empty_cells} 个空白单元格")
            return
        
        # 验证数独规则
        errors = []
        
        # 验证每行
        for i in range(9):
            row = current[i]
            if len(set(row)) != 9 or sum(row) != 45:
                errors.append(f"第 {i+1} 行错误")
        
        # 验证每列
        for j in range(9):
            col = [current[i][j] for i in range(9)]
            if len(set(col)) != 9 or sum(col) != 45:
                errors.append(f"第 {j+1} 列错误")
        
        # 验证每个宫
        for block_i in range(3):
            for block_j in range(3):
                block = []
                for i in range(3):
                    for j in range(3):
                        block.append(current[block_i*3 + i][block_j*3 + j])
                if len(set(block)) != 9 or sum(block) != 45:
                    errors.append(f"宫 ({block_i+1}, {block_j+1}) 错误")
        
        if errors:
            error_msg = "发现以下错误：\n" + "\n".join(errors)
            messagebox.showerror("验证失败", error_msg)
            self.update_status("验证失败")
        else:
            messagebox.showinfo("验证成功", "恭喜！数独解答正确！")
            self.update_status("验证成功")
    
    def save_puzzle(self):
        """保存当前数独题目到文件"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w') as f:
                    for i in range(9):
                        row = ' '.join(str(self.puzzle[i][j]) for j in range(9))
                        f.write(row + '\n')
                self.update_status(f"已保存到 {filename}")
        except Exception as e:
            messagebox.showerror("保存错误", f"保存文件时出错: {str(e)}")
    
    def load_puzzle(self):
        """从文件加载数独题目"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'r') as f:
                    lines = f.readlines()
                    puzzle_data = []
                    for line in lines[:9]:  # 只读取前9行
                        row = [int(x) for x in line.strip().split()]
                        if len(row) == 9:
                            puzzle_data.append(row)
                    
                    if len(puzzle_data) == 9:
                        self.load_puzzle_from_data(puzzle_data)
                        self.update_status(f"已加载 {filename}")
                    else:
                        messagebox.showerror("加载错误", "文件格式不正确")
        except Exception as e:
            messagebox.showerror("加载错误", f"加载文件时出错: {str(e)}")
    
    def log_process(self, message):
        """记录求解过程到文本框"""
        self.root.after(0, lambda: self.process_text.insert(tk.END, message + "\n"))
        self.root.after(0, lambda: self.process_text.see(tk.END))
    
    def update_status(self, message):
        """更新状态栏"""
        self.root.after(0, lambda: self.status_var.set(message))
    
    def update_display(self):
        """更新数独网格显示"""
        for i in range(9):
            for j in range(9):
                self.cells[i][j].delete(0, tk.END)
                if self.puzzle[i][j] != 0:
                    self.cells[i][j].insert(0, str(self.puzzle[i][j]))
                    self.cells[i][j].config(fg="black")
                else:
                    self.cells[i][j].config(fg="black")

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
    app = SudokuSolverApp(root)
    
    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    main()