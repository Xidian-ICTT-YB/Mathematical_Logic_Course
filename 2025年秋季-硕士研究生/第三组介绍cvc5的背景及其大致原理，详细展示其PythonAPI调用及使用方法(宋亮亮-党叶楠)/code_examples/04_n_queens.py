"""
实际应用示例2: N皇后问题求解器
使用 cvc5 求解 N 皇后问题
"""

from cvc5 import Solver, Kind

class NQueensSolver:
    """使用 cvc5 的 N 皇后求解器"""
    
    def __init__(self, n):
        self.n = n
        self.solver = Solver()
        self.solver.setOption("produce-models", "true")
        self.int_sort = self.solver.getIntegerSort()
        
        # 为每一行创建一个变量，表示该行皇后所在的列
        self.queens = [self.solver.mkConst(self.int_sort, f"queen_{i}") 
                       for i in range(n)]
        
        self._add_constraints()
    
    def _add_constraints(self):
        """添加 N 皇后问题的约束"""
        # 1. 每个皇后必须在 0 到 n-1 列之间
        for i in range(self.n):
            self.solver.assertFormula(
                self.solver.mkTerm(Kind.GEQ, self.queens[i], self.solver.mkInteger(0))
            )
            self.solver.assertFormula(
                self.solver.mkTerm(Kind.LT, self.queens[i], self.solver.mkInteger(self.n))
            )
        
        # 2. 不同的皇后在不同的列（所有列不同）
        self.solver.assertFormula(
            self.solver.mkTerm(Kind.DISTINCT, *self.queens)
        )
        
        # 3. 不在同一对角线上
        for i in range(self.n):
            for j in range(i + 1, self.n):
                # 左上到右下对角线: queen[i] - i != queen[j] - j
                # 即: queen[i] - queen[j] != i - j
                diff_cols = self.solver.mkTerm(Kind.SUB, self.queens[i], self.queens[j])
                diff_rows = self.solver.mkInteger(i - j)
                constraint1 = self.solver.mkTerm(Kind.DISTINCT, diff_cols, diff_rows)
                
                # 右上到左下对角线: queen[i] + i != queen[j] + j
                # 即: queen[i] - queen[j] != j - i
                diff_rows2 = self.solver.mkInteger(j - i)
                constraint2 = self.solver.mkTerm(Kind.DISTINCT, diff_cols, diff_rows2)
                
                self.solver.assertFormula(constraint1)
                self.solver.assertFormula(constraint2)
    
    def solve(self):
        """求解 N 皇后问题"""
        result = self.solver.checkSat()
        
        if result.isSat():
            solution = []
            for i in range(self.n):
                col = self.solver.getValue(self.queens[i]).toPythonObj()
                solution.append(col)
            return solution
        else:
            return None
    
    @staticmethod
    def print_board(solution):
        """打印棋盘"""
        n = len(solution)
        for i in range(n):
            row = ""
            for j in range(n):
                if solution[i] == j:
                    row += "Q "
                else:
                    row += ". "
            print(row)


def example_8_queens():
    """示例1: 8皇后问题"""
    print("=" * 60)
    print("示例1: 8皇后问题")
    print("=" * 60)
    
    n = 8
    print(f"\n正在求解 {n} 皇后问题...")
    
    solver = NQueensSolver(n)
    solution = solver.solve()
    
    if solution:
        print(f"\n找到解:")
        print(f"皇后位置 (行, 列): {[(i, solution[i]) for i in range(n)]}")
        print(f"\n棋盘:")
        NQueensSolver.print_board(solution)
    else:
        print("\n无解!")
    print()


def example_4_queens():
    """示例2: 4皇后问题"""
    print("=" * 60)
    print("示例2: 4皇后问题")
    print("=" * 60)
    
    n = 4
    print(f"\n正在求解 {n} 皇后问题...")
    
    solver = NQueensSolver(n)
    solution = solver.solve()
    
    if solution:
        print(f"\n找到解:")
        print(f"皇后位置 (行, 列): {[(i, solution[i]) for i in range(n)]}")
        print(f"\n棋盘:")
        NQueensSolver.print_board(solution)
    else:
        print("\n无解!")
    print()


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("N皇后问题求解器 - 使用 CVC5")
    print("=" * 60 + "\n")
    
    example_4_queens()
    example_8_queens()
    
    print("=" * 60)
    print("求解完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
