"""
实际应用示例1: 数独求解器
使用 cvc5 求解数独问题
"""

from cvc5 import Solver, Kind

class SudokuSolver:
    """使用 cvc5 的数独求解器"""
    
    def __init__(self):
        self.solver = Solver()
        self.solver.setOption("produce-models", "true")
        self.int_sort = self.solver.getIntegerSort()
        
        # 创建 9x9 的变量网格
        self.grid = [[self.solver.mkConst(self.int_sort, f"cell_{i}_{j}") 
                      for j in range(9)] for i in range(9)]
        
        # 添加基本约束
        self._add_basic_constraints()
    
    def _add_basic_constraints(self):
        """添加数独的基本约束"""
        # 1. 每个单元格的值在 1-9 之间
        for i in range(9):
            for j in range(9):
                cell = self.grid[i][j]
                # cell >= 1 AND cell <= 9
                self.solver.assertFormula(
                    self.solver.mkTerm(Kind.GEQ, cell, self.solver.mkInteger(1))
                )
                self.solver.assertFormula(
                    self.solver.mkTerm(Kind.LEQ, cell, self.solver.mkInteger(9))
                )
        
        # 2. 每行的数字不重复
        for i in range(9):
            self.solver.assertFormula(
                self.solver.mkTerm(Kind.DISTINCT, *self.grid[i])
            )
        
        # 3. 每列的数字不重复
        for j in range(9):
            column = [self.grid[i][j] for i in range(9)]
            self.solver.assertFormula(
                self.solver.mkTerm(Kind.DISTINCT, *column)
            )
        
        # 4. 每个 3x3 宫格内的数字不重复
        for box_row in range(3):
            for box_col in range(3):
                box_cells = []
                for i in range(3):
                    for j in range(3):
                        row = box_row * 3 + i
                        col = box_col * 3 + j
                        box_cells.append(self.grid[row][col])
                self.solver.assertFormula(
                    self.solver.mkTerm(Kind.DISTINCT, *box_cells)
                )
    
    def set_clues(self, clues):
        """
        设置初始线索
        clues: 9x9 的数组，0 表示空格，1-9 表示已知数字
        """
        for i in range(9):
            for j in range(9):
                if clues[i][j] != 0:
                    constraint = self.solver.mkTerm(
                        Kind.EQUAL, 
                        self.grid[i][j], 
                        self.solver.mkInteger(clues[i][j])
                    )
                    self.solver.assertFormula(constraint)
    
    def solve(self):
        """求解数独"""
        result = self.solver.checkSat()
        
        if result.isSat():
            # 提取解
            solution = []
            for i in range(9):
                row = []
                for j in range(9):
                    value = self.solver.getValue(self.grid[i][j])
                    row.append(value.toPythonObj())
                solution.append(row)
            return solution
        else:
            return None
    
    @staticmethod
    def print_sudoku(grid):
        """打印数独网格"""
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("-" * 21)
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    print("|", end=" ")
                print(grid[i][j] if grid[i][j] != 0 else ".", end=" ")
            print()


def example_easy_sudoku():
    """示例1: 简单数独"""
    print("=" * 60)
    print("示例1: 简单数独")
    print("=" * 60)
    
    # 初始线索
    clues = [
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
    
    print("\n初始数独:")
    SudokuSolver.print_sudoku(clues)
    
    print("\n正在求解...")
    solver = SudokuSolver()
    solver.set_clues(clues)
    solution = solver.solve()
    
    if solution:
        print("\n找到解:")
        SudokuSolver.print_sudoku(solution)
    else:
        print("\n无解!")
    print()


def example_hard_sudoku():
    """示例2: 困难数独"""
    print("=" * 60)
    print("示例2: 困难数独")
    print("=" * 60)
    
    # 更少的初始线索
    clues = [
        [0, 0, 0, 0, 0, 0, 6, 8, 0],
        [0, 0, 0, 0, 7, 3, 0, 0, 9],
        [3, 0, 9, 0, 0, 0, 0, 4, 5],
        [4, 9, 0, 0, 0, 0, 0, 0, 0],
        [8, 0, 3, 0, 5, 0, 9, 0, 2],
        [0, 0, 0, 0, 0, 0, 0, 3, 6],
        [9, 6, 0, 0, 0, 0, 3, 0, 8],
        [7, 0, 0, 6, 8, 0, 0, 0, 0],
        [0, 2, 8, 0, 0, 0, 0, 0, 0]
    ]
    
    print("\n初始数独:")
    SudokuSolver.print_sudoku(clues)
    
    print("\n正在求解...")
    solver = SudokuSolver()
    solver.set_clues(clues)
    solution = solver.solve()
    
    if solution:
        print("\n找到解:")
        SudokuSolver.print_sudoku(solution)
    else:
        print("\n无解!")
    print()


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("数独求解器 - 使用 CVC5")
    print("=" * 60 + "\n")
    
    example_easy_sudoku()
    example_hard_sudoku()
    
    print("=" * 60)
    print("求解完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
