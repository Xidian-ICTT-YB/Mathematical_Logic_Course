

# """
# Z3 求解器在员工排班中的应用
# 本程序演示如何使用 Z3 解决复杂的员工排班问题
# 包括硬约束（必须满足）和软约束（尽量满足）
# """

# from z3 import *
# import itertools
# from datetime import datetime, timedelta
# import pandas as pd

# class EmployeeSchedulingSystem:
#     def __init__(self):
#         """初始化排班系统"""
#         print("=" * 80)
#         print("Z3 求解器在员工排班中的应用演示")
#         print("=" * 80)
        
#         # 员工信息
#         self.employees = {
#             'E001': {'name': '张三', '职位': '店长', '经验': 5, '偏好': ['早班', '晚班']},
#             'E002': {'name': '李四', '职位': '收银员', '经验': 3, '偏好': ['早班']},
#             'E003': {'name': '王五', '职位': '收银员', '经验': 2, '偏好': ['中班', '晚班']},
#             'E004': {'name': '赵六', '职位': '理货员', '经验': 1, '偏好': ['早班', '中班']},
#             'E005': {'name': '钱七', '职位': '收银员', '经验': 4, '偏好': ['晚班']},
#             'E006': {'name': '孙八', '职位': '理货员', '经验': 2, '偏好': ['中班']},
#             'E007': {'name': '周九', '职位': '收银员', '经验': 1, '偏好': ['早班', '晚班']},
#         }
        
#         # 班次信息
#         self.shifts = {
#             '早班': {'id': 'S1', 'start': '08:00', 'end': '16:00', '人数': 2},
#             '中班': {'id': 'S2', 'start': '12:00', 'end': '20:00', '人数': 3},
#             '晚班': {'id': 'S3', 'start': '16:00', 'end': '24:00', '人数': 2}
#         }
        
#         # 日期范围（未来7天）
#         self.dates = self.generate_dates(7)
        
#         # 排班变量字典
#         self.schedule_vars = {}
        
#         # 约束计数器
#         self.constraint_count = 0
        
#     def generate_dates(self, days):
#         """生成日期列表"""
#         start_date = datetime.now().date()
#         return [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') 
#                 for i in range(days)]
    
#     def create_schedule_variables(self):
#         """创建排班变量"""
#         print("\n" + "=" * 80)
#         print("步骤 1: 创建排班变量")
#         print("=" * 80)
        
#         # 为每个员工、每个日期、每个班次创建一个布尔变量
#         # assigned[employee][date][shift] = True 表示该员工在该日期被分配该班次
#         print("创建布尔变量表示员工排班：")
#         print("格式: assigned[员工ID][日期][班次]")
        
#         for emp_id in self.employees.keys():
#             for date in self.dates:
#                 for shift_name in self.shifts.keys():
#                     var_name = f"assign_{emp_id}_{date}_{shift_name}"
#                     # 创建布尔变量
#                     self.schedule_vars[(emp_id, date, shift_name)] = Bool(var_name)
        
#         total_vars = len(self.schedule_vars)
#         print(f"\n共创建 {total_vars} 个排班变量")
#         print(f"员工数: {len(self.employees)} × 天数: {len(self.dates)} × 班次数: {len(self.shifts)} = {total_vars}")
#         return self.schedule_vars
    
#     def add_hard_constraints(self, solver):
#         """添加强制约束（硬约束）"""
#         print("\n" + "=" * 80)
#         print("步骤 2: 添加强制约束（硬约束）")
#         print("=" * 80)
        
#         # 约束1: 每个班次必须满足所需人数
#         print("\n约束 1: 每个班次必须满足所需人数")
#         for date in self.dates:
#             for shift_name, shift_info in self.shifts.items():
#                 required = shift_info['人数']
#                 # 统计该班次被分配的员工
#                 shift_assignments = []
#                 for emp_id in self.employees.keys():
#                     var = self.schedule_vars[(emp_id, date, shift_name)]
#                     shift_assignments.append(var)
                
#                 # 至少需要required名员工
#                 at_least_required = []
#                 for combo in itertools.combinations(shift_assignments, required):
#                     # 至少这个组合为真
#                     at_least_required.append(And(*combo))
                
#                 # 添加约束：至少有一个组合为真
#                 if at_least_required:
#                     solver.add(Or(*at_least_required))
#                     self.constraint_count += 1
#                 print(f"  日期 {date} {shift_name}: 需要 {required} 人")
        
#         # 约束2: 每个员工每天最多只能上一个班次
#         print("\n约束 2: 每个员工每天最多只能上一个班次")
#         for emp_id in self.employees.keys():
#             for date in self.dates:
#                 # 该员工在该日期所有可能的班次
#                 daily_shifts = [self.schedule_vars[(emp_id, date, s)] 
#                                for s in self.shifts.keys()]
#                 # 最多只能有一个为真（AtMost约束）
#                 solver.add(AtMost(*daily_shifts, 1))
#                 self.constraint_count += len(daily_shifts)
#             print(f"  员工 {self.employees[emp_id]['name']}: 每天最多一个班次")
        
#         # 约束3: 不能连续上晚班（劳动法要求）
#         print("\n约束 3: 不能连续上晚班")
#         for emp_id in self.employees.keys():
#             for i in range(len(self.dates) - 1):
#                 date1 = self.dates[i]
#                 date2 = self.dates[i + 1]
#                 # 如果今天上晚班，明天就不能上晚班
#                 var1 = self.schedule_vars[(emp_id, date1, '晚班')]
#                 var2 = self.schedule_vars[(emp_id, date2, '晚班')]
#                 solver.add(Implies(var1, Not(var2)))
#                 self.constraint_count += 1
#             print(f"  员工 {self.employees[emp_id]['name']}: 禁止连续晚班")
        
#         # 约束4: 每周最多工作5天（劳动法要求）
#         print("\n约束 4: 每周最多工作5天")
#         for emp_id in self.employees.keys():
#             weekly_work_days = []
#             for date in self.dates:
#                 # 如果该日期有任何班次，就算工作
#                 day_worked = Or([self.schedule_vars[(emp_id, date, s)] 
#                                 for s in self.shifts.keys()])
#                 weekly_work_days.append(day_worked)
#             # 最多工作5天
#             solver.add(AtMost(*weekly_work_days, 5))
#             self.constraint_count += len(weekly_work_days)
#             print(f"  员工 {self.employees[emp_id]['name']}: 每周最多5天")
        
#         # 约束5: 每个班次必须至少有一名经验丰富的员工（经验>=3）
#         print("\n约束 5: 关键班次需要经验丰富的员工")
#         experienced_employees = [emp_id for emp_id, info in self.employees.items() 
#                                 if info['经验'] >= 3]
        
#         for date in self.dates:
#             for shift_name in ['早班', '晚班']:  # 早班和晚班需要经验员工
#                 experienced_assignments = []
#                 for emp_id in experienced_employees:
#                     var = self.schedule_vars[(emp_id, date, shift_name)]
#                     experienced_assignments.append(var)
                
#                 # 至少需要一名经验丰富的员工
#                 if experienced_assignments:
#                     solver.add(Or(*experienced_assignments))
#                     self.constraint_count += 1
#                     print(f"  日期 {date} {shift_name}: 需要至少1名经验员工")
        
#         print(f"\n硬约束总数: {self.constraint_count}")
    
#     def add_soft_constraints(self, solver):
#         """添加优化约束（软约束）"""
#         print("\n" + "=" * 80)
#         print("步骤 3: 添加优化约束（软约束）")
#         print("=" * 80)
        
#         # 创建优化目标变量
#         optimization_vars = []
        
#         # 软约束1: 尽量满足员工偏好
#         print("\n软约束 1: 尽量满足员工班次偏好")
#         preference_satisfied = []
#         for emp_id, emp_info in self.employees.items():
#             preferred_shifts = emp_info['偏好']
#             for date in self.dates:
#                 for shift_name in self.shifts.keys():
#                     var = self.schedule_vars[(emp_id, date, shift_name)]
#                     if shift_name in preferred_shifts:
#                         # 分配偏好班次是好的
#                         preference_satisfied.append(var)
#                     else:
#                         # 分配非偏好班次是不好的（取反）
#                         preference_satisfied.append(Not(var))
        
#         # 创建偏好满足度变量
#         preference_score = Int('preference_score')
#         solver.add(preference_score == Sum([If(v, 1, 0) for v in preference_satisfied]))
#         optimization_vars.append(preference_score)
#         print(f"  创建偏好满足度评分，最大可能值: {len(preference_satisfied)}")
        
#         # 软约束2: 尽量均匀分配工作量
#         print("\n软约束 2: 尽量均匀分配班次数量")
#         # 计算每个员工的班次数量
#         employee_workloads = []
#         for emp_id in self.employees.keys():
#             emp_shifts = []
#             for date in self.dates:
#                 for shift_name in self.shifts.keys():
#                     emp_shifts.append(self.schedule_vars[(emp_id, date, shift_name)])
#             workload = Sum([If(v, 1, 0) for v in emp_shifts])
#             employee_workloads.append(workload)
        
#         # 计算工作量方差（作为均匀度的度量）
#         avg_workload = Sum(employee_workloads) / len(employee_workloads)
#         variance_terms = []
#         for w in employee_workloads:
#             variance_terms.append((w - avg_workload) * (w - avg_workload))
        
#         workload_variance = Int('workload_variance')
#         solver.add(workload_variance == Sum(variance_terms))
#         optimization_vars.append(workload_variance)
#         print(f"  创建工作量方差变量，越小表示分配越均匀")
        
#         # 软约束3: 尽量让员工每周有连续休息日
#         print("\n软约束 3: 尽量安排连续休息日")
#         consecutive_rest_score = []
#         for emp_id in self.employees.keys():
#             for i in range(len(self.dates) - 1):
#                 date1 = self.dates[i]
#                 date2 = self.dates[i + 1]
                
#                 # 这两天都没有班次就是连续休息
#                 day1_work = Or([self.schedule_vars[(emp_id, date1, s)] 
#                               for s in self.shifts.keys()])
#                 day2_work = Or([self.schedule_vars[(emp_id, date2, s)] 
#                               for s in self.shifts.keys()])
                
#                 consecutive_rest = And(Not(day1_work), Not(day2_work))
#                 consecutive_rest_score.append(If(consecutive_rest, 1, 0))
        
#         rest_score = Int('rest_score')
#         solver.add(rest_score == Sum(consecutive_rest_score))
#         optimization_vars.append(rest_score)
#         print(f"  创建连续休息评分，越高越好")
        
#         print(f"\n软约束优化变量: {len(optimization_vars)} 个")
#         return optimization_vars
    
#     def solve_and_optimize(self):
#         """求解并优化排班"""
#         print("\n" + "=" * 80)
#         print("步骤 4: 使用Z3求解和优化")
#         print("=" * 80)
        
#         # 创建求解器
#         solver = Solver()
#         print("创建 Z3 求解器实例")
        
#         # 创建排班变量
#         self.create_schedule_variables()
        
#         # 添加硬约束
#         self.add_hard_constraints(solver)
        
#         # 添加软约束（返回优化变量）
#         optimization_vars = self.add_soft_constraints(solver)
        
#         # 首先检查是否有可行解
#         print("\n" + "-" * 80)
#         print("检查可行性：是否存在满足所有硬约束的排班方案？")
#         print("Z3 正在搜索可行解...")
        
#         start_time = datetime.now()
#         feasibility = solver.check()
#         check_time = (datetime.now() - start_time).total_seconds()
        
#         if feasibility != sat:
#             print(f"\n✗ 无法找到可行解！求解时间: {check_time:.2f}秒")
#             print("可能的原因：约束过于严格或员工数量不足")
#             return None
        
#         print(f"\n✓ 找到可行解！检查时间: {check_time:.2f}秒")
#         print("现在进行优化，寻找最优解...")
        
#         # 创建优化器
#         print("\n创建 Z3 优化器进行多目标优化")
#         optimizer = Optimize()
        
#         # 添加所有约束
#         for constraint in solver.assertions():
#             optimizer.add(constraint)
        
#         # 设置优化目标
#         # 最大化：偏好满足度和连续休息
#         # 最小化：工作量方差
#         print("\n设置优化目标：")
#         print("  1. 最大化: 偏好满足度 (preference_score)")
#         print("  2. 最大化: 连续休息日 (rest_score)")
#         print("  3. 最小化: 工作量方差 (workload_variance)")
        
#         # 获取优化变量
#         preference_score = [v for v in optimization_vars if str(v) == 'preference_score'][0]
#         workload_variance = [v for v in optimization_vars if str(v) == 'workload_variance'][0]
#         rest_score = [v for v in optimization_vars if str(v) == 'rest_score'][0]
        
#         # 设置优先级：先最大化偏好，然后最小化方差，最后最大化休息
#         optimizer.maximize(preference_score)
#         optimizer.minimize(workload_variance)
#         optimizer.maximize(rest_score)
        
#         # 开始优化
#         print("\n开始优化求解...")
#         print("Z3 正在搜索最优排班方案...")
        
#         start_time = datetime.now()
#         optimization_result = optimizer.check()
#         optimize_time = (datetime.now() - start_time).total_seconds()
        
#         if optimization_result != sat:
#             print(f"\n✗ 优化失败！时间: {optimize_time:.2f}秒")
#             return None
        
#         print(f"\n✓ 找到最优解！优化时间: {optimize_time:.2f}秒")
        
#         # 获取模型
#         model = optimizer.model()
        
#         # 输出优化结果
#         print("\n" + "=" * 80)
#         print("优化结果统计")
#         print("=" * 80)
        
#         pref_val = model[preference_score]
#         var_val = model[workload_variance]
#         rest_val = model[rest_score]
        
#         print(f"偏好满足度: {pref_val} / {len(self.schedule_vars)}")
#         print(f"工作量方差: {var_val} (越小越均匀)")
#         print(f"连续休息日评分: {rest_val}")
        
#         total_vars = len(self.schedule_vars)
#         satisfied = sum(1 for var in self.schedule_vars.values() 
#                        if is_true(model[var]))
#         print(f"总排班安排数: {satisfied} / {total_vars}")
        
#         return model
    
#     def extract_schedule(self, model):
#         """从模型中提取排班表"""
#         print("\n" + "=" * 80)
#         print("步骤 5: 提取排班结果")
#         print("=" * 80)
        
#         schedule = {}
        
#         # 按日期组织排班
#         for date in self.dates:
#             schedule[date] = {}
#             for shift_name in self.shifts.keys():
#                 schedule[date][shift_name] = []
        
#         # 填充排班数据
#         for (emp_id, date, shift_name), var in self.schedule_vars.items():
#             if is_true(model[var]):
#                 schedule[date][shift_name].append({
#                     '员工ID': emp_id,
#                     '姓名': self.employees[emp_id]['name'],
#                     '职位': self.employees[emp_id]['职位'],
#                     '经验': self.employees[emp_id]['经验']
#                 })
        
#         return schedule
    
#     def print_schedule(self, schedule):
#         """打印排班表"""
#         print("\n" + "=" * 80)
#         print("最终排班表")
#         print("=" * 80)
        
#         # 按日期打印
#         for date in self.dates:
#             print(f"\n📅 日期: {date}")
#             print("-" * 60)
            
#             for shift_name, shift_info in self.shifts.items():
#                 assigned_employees = schedule[date][shift_name]
#                 if assigned_employees:
#                     print(f"\n  {shift_name} ({shift_info['start']}-{shift_info['end']}):")
#                     for emp in assigned_employees:
#                         pref_mark = "⭐" if shift_name in self.employees[emp['员工ID']]['偏好'] else "  "
#                         print(f"    {pref_mark} {emp['姓名']} ({emp['职位']}, 经验{emp['经验']}年)")
#                 else:
#                     print(f"\n  {shift_name}: (无人)")
        
#         # 统计信息
#         print("\n" + "=" * 80)
#         print("排班统计信息")
#         print("=" * 80)
        
#         # 员工工作量统计
#         print("\n员工工作量统计:")
#         print("-" * 40)
#         employee_work_counts = {}
        
#         for emp_id, emp_info in self.employees.items():
#             work_count = 0
#             for date in self.dates:
#                 for shift_name in self.shifts.keys():
#                     if any(emp['员工ID'] == emp_id for emp in schedule[date][shift_name]):
#                         work_count += 1
#             employee_work_counts[emp_id] = work_count
        
#         for emp_id, count in employee_work_counts.items():
#             emp_info = self.employees[emp_id]
#             print(f"  {emp_info['name']}: {count} 天")
        
#         # 班次覆盖统计
#         print("\n班次覆盖情况:")
#         print("-" * 40)
#         for date in self.dates:
#             for shift_name, shift_info in self.shifts.items():
#                 assigned = len(schedule[date][shift_name])
#                 required = shift_info['人数']
#                 status = "✓" if assigned >= required else f"✗ (缺{required-assigned}人)"
#                 print(f"  {date} {shift_name}: {assigned}/{required} 人 {status}")
    
#     def analyze_preference_satisfaction(self, schedule):
#         """分析偏好满足情况"""
#         print("\n" + "=" * 80)
#         print("员工偏好满足分析")
#         print("=" * 80)
        
#         for emp_id, emp_info in self.employees.items():
#             preferred_shifts = emp_info['偏好']
#             total_assigned = 0
#             preferred_assigned = 0
            
#             for date in self.dates:
#                 for shift_name in self.shifts.keys():
#                     # 检查是否被分配了这个班次
#                     assigned = any(emp['员工ID'] == emp_id 
#                                   for emp in schedule[date][shift_name])
#                     if assigned:
#                         total_assigned += 1
#                         if shift_name in preferred_shifts:
#                             preferred_assigned += 1
            
#             if total_assigned > 0:
#                 satisfaction_rate = preferred_assigned / total_assigned * 100
#                 print(f"  {emp_info['name']}: {preferred_assigned}/{total_assigned} "
#                       f"({satisfaction_rate:.1f}%) 的班次符合偏好")
#             else:
#                 print(f"  {emp_info['name']}: 本周无排班")
    
#     def generate_z3_analysis_report(self, model):
#         """生成Z3求解器分析报告"""
#         print("\n" + "=" * 80)
#         print("Z3 求解器性能分析报告")
#         print("=" * 80)
        
#         print("\n问题规模分析:")
#         print("-" * 40)
#         print(f"变量数量: {len(self.schedule_vars)}")
#         print(f"硬约束数量: {self.constraint_count}")
#         print(f"员工数量: {len(self.employees)}")
#         print(f"排班天数: {len(self.dates)}")
#         print(f"班次类型: {len(self.shifts)}")
        
#         print("\n约束类型分析:")
#         print("-" * 40)
#         print("1. 人数约束: 确保每个班次有足够员工")
#         print("2. 唯一性约束: 员工每天最多一个班次")
#         print("3. 连续性约束: 禁止连续晚班")
#         print("4. 工作量约束: 每周最多工作5天")
#         print("5. 经验约束: 关键班次需要经验员工")
#         print("6. 偏好优化: 尽量满足员工偏好")
#         print("7. 均匀性优化: 工作量尽量均匀")
#         print("8. 休息优化: 尽量安排连续休息")
        
#         print("\nZ3求解优势:")
#         print("-" * 40)
#         print("✓ 处理复杂约束组合")
#         print("✓ 保证找到最优解（如果存在）")
#         print("✓ 自动处理矛盾约束")
#         print("✓ 支持多目标优化")
#         print("✓ 可扩展到大问题规模")

# def main():
#     """主函数"""
#     try:
#         # 检查是否安装了Z3
#         from z3 import Solver, Optimize
#     except ImportError:
#         print("错误: 未找到 Z3 模块。请使用以下命令安装:")
#         print("pip install z3-solver")
#         return
    
#     # 创建排班系统
#     scheduler = EmployeeSchedulingSystem()
    
#     # 解决排班问题
#     model = scheduler.solve_and_optimize()
    
#     if model:
#         # 提取排班表
#         schedule = scheduler.extract_schedule(model)
        
#         # 打印排班表
#         scheduler.print_schedule(schedule)
        
#         # 分析偏好满足
#         scheduler.analyze_preference_satisfaction(schedule)
        
#         # 生成Z3分析报告
#         scheduler.generate_z3_analysis_report(model)
        
#         print("\n" + "=" * 80)
#         print("排班完成！")
#         print("=" * 80)
#     else:
#         print("\n排班失败，请调整约束条件或增加员工数量")

# if __name__ == "__main__":
#     main()

















#  --------------------------------------------------有可视化界面------------------------------------------------------------------------------------



"""
Z3 求解器在员工排班中的应用 - 可视化界面
这个程序展示了如何使用 Z3 解决复杂的员工排班问题，并提供直观的可视化界面。
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter import font as tkfont
import time
from datetime import datetime, timedelta
from z3 import *
import pandas as pd
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class EmployeeSchedulingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Z3 求解器 - 员工排班系统")
        self.root.geometry("1400x900")
        
        # 设置图标
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # 初始化数据
        self.initialize_data()
        
        # 创建界面
        self.create_widgets()
        
        # 状态变量
        self.solver = None
        self.model = None
        self.schedule_vars = {}
        self.schedule_result = None
        self.is_solving = False
        
        # 显示初始信息
        self.display_welcome_message()
    
    def initialize_data(self):
        """初始化员工和班次数据"""
        # 员工数据
        self.employees = [
            {'id': 'E001', 'name': '张三', 'position': '店长', 'exp': 5, 
             'pref_shifts': ['早班', '晚班'], 'max_days': 6, 'salary': 8000},
            {'id': 'E002', 'name': '李四', 'position': '收银员', 'exp': 3, 
             'pref_shifts': ['早班', '中班'], 'max_days': 5, 'salary': 6000},
            {'id': 'E003', 'name': '王五', 'position': '收银员', 'exp': 2, 
             'pref_shifts': ['中班', '晚班'], 'max_days': 5, 'salary': 5500},
            {'id': 'E004', 'name': '赵六', 'position': '理货员', 'exp': 1, 
             'pref_shifts': ['早班'], 'max_days': 5, 'salary': 5000},
            {'id': 'E005', 'name': '钱七', 'position': '收银员', 'exp': 4, 
             'pref_shifts': ['晚班'], 'max_days': 5, 'salary': 6500},
            {'id': 'E006', 'name': '孙八', 'position': '理货员', 'exp': 2, 
             'pref_shifts': ['中班'], 'max_days': 5, 'salary': 5200},
            {'id': 'E007', 'name': '周九', 'position': '收银员', 'exp': 1, 
             'pref_shifts': ['早班', '晚班'], 'max_days': 5, 'salary': 5100},
            {'id': 'E008', 'name': '吴十', 'position': '理货员', 'exp': 3, 
             'pref_shifts': ['中班', '晚班'], 'max_days': 5, 'salary': 5800},
        ]
        
        # 班次数据
        self.shifts = {
            '早班': {'id': 'M', 'time': '08:00-16:00', 'min_staff': 2, 'max_staff': 3, 'color': '#FFD700'},
            '中班': {'id': 'A', 'time': '12:00-20:00', 'min_staff': 3, 'max_staff': 4, 'color': '#87CEEB'},
            '晚班': {'id': 'N', 'time': '16:00-24:00', 'min_staff': 2, 'max_staff': 3, 'color': '#4169E1'},
        }
        
        # 生成日期（未来14天）
        self.generate_dates(14)
    
    def generate_dates(self, days):
        """生成日期列表"""
        start_date = datetime.now().date()
        self.dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') 
                      for i in range(days)]
        self.dates_display = [(start_date + timedelta(days=i)).strftime('%m/%d') 
                              for i in range(days)]
    
    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题栏
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(title_frame, 
                               text="Z3 求解器 - 员工智能排班系统",
                               font=("微软雅黑", 18, "bold"),
                               fg="#2C3E50")
        title_label.pack(side=tk.LEFT)
        
        # 分隔线
        separator = ttk.Separator(main_container, orient='horizontal')
        separator.pack(fill=tk.X, pady=5)
        
        # 左侧控制面板
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        
        # 右侧显示面板
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 创建左侧面板内容
        self.create_left_panel(left_panel)
        
        # 创建右侧面板内容
        self.create_right_panel(right_panel)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, 
                               textvariable=self.status_var,
                               relief=tk.SUNKEN,
                               anchor=tk.W,
                               font=("微软雅黑", 9))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_left_panel(self, parent):
        """创建左侧控制面板"""
        # 系统信息
        info_frame = ttk.LabelFrame(parent, text="系统信息", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text = f"""
        员工总数: {len(self.employees)} 人
        排班天数: {len(self.dates)} 天
        班次类型: {len(self.shifts)} 种
        总决策变量: {len(self.employees) * len(self.dates) * len(self.shifts)}
        """
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack()
        
        # Z3求解器说明
        z3_frame = ttk.LabelFrame(parent, text="Z3求解器工作原理", padding="10")
        z3_frame.pack(fill=tk.X, pady=(0, 10))
        
        z3_text = """
        Z3将排班问题转化为约束满足问题：
        1. 创建布尔变量表示排班决策
        2. 添加硬约束（必须满足）
        3. 添加软约束（优化目标）
        4. 使用SAT/SMT技术求解
        5. 优化找到最佳排班方案
        """
        z3_label = ttk.Label(z3_frame, text=z3_text, justify=tk.LEFT, wraplength=300)
        z3_label.pack()
        
        # 约束设置
        constraint_frame = ttk.LabelFrame(parent, text="排班约束设置", padding="10")
        constraint_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 硬约束
        ttk.Label(constraint_frame, text="硬约束（必须满足）:", font=("微软雅黑", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.var_min_staff = tk.BooleanVar(value=True)
        ttk.Checkbutton(constraint_frame, text="满足最少人数要求", variable=self.var_min_staff).grid(row=1, column=0, sticky=tk.W)
        
        self.var_no_consecutive_night = tk.BooleanVar(value=True)
        ttk.Checkbutton(constraint_frame, text="禁止连续晚班", variable=self.var_no_consecutive_night).grid(row=2, column=0, sticky=tk.W)
        
        self.var_max_days = tk.BooleanVar(value=True)
        ttk.Checkbutton(constraint_frame, text="限制最大工作天数", variable=self.var_max_days).grid(row=3, column=0, sticky=tk.W)
        
        self.var_one_shift_per_day = tk.BooleanVar(value=True)
        ttk.Checkbutton(constraint_frame, text="每天最多一个班次", variable=self.var_one_shift_per_day).grid(row=4, column=0, sticky=tk.W)
        
        # 软约束（优化目标）
        ttk.Label(constraint_frame, text="软约束（优化目标）:", font=("微软雅黑", 10, "bold")).grid(row=5, column=0, sticky=tk.W, pady=(10,5))
        
        self.var_preference = tk.BooleanVar(value=True)
        ttk.Checkbutton(constraint_frame, text="满足员工偏好", variable=self.var_preference).grid(row=6, column=0, sticky=tk.W)
        
        self.var_fairness = tk.BooleanVar(value=True)
        ttk.Checkbutton(constraint_frame, text="公平分配工作量", variable=self.var_fairness).grid(row=7, column=0, sticky=tk.W)
        
        self.var_consecutive_rest = tk.BooleanVar(value=True)
        ttk.Checkbutton(constraint_frame, text="安排连续休息", variable=self.var_consecutive_rest).grid(row=8, column=0, sticky=tk.W)
        
        # 控制按钮
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="开始排班", command=self.start_scheduling, 
                  style='Accent.TButton').pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="逐步求解演示", command=self.step_by_step_demo).pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="导出排班表", command=self.export_schedule).pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="重置系统", command=self.reset_system).pack(fill=tk.X, pady=5)
        
        # 自定义样式
        style = ttk.Style()
        style.configure('Accent.TButton', font=('微软雅黑', 10, 'bold'))
    
    def create_right_panel(self, parent):
        """创建右侧显示面板"""
        # 创建笔记本（标签页）
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 标签页1：排班可视化
        schedule_frame = ttk.Frame(notebook)
        notebook.add(schedule_frame, text='排班表可视化')
        
        # 创建排班表格的Canvas和滚动条
        self.create_schedule_table(schedule_frame)
        
        # 标签页2：Z3求解过程
        process_frame = ttk.Frame(notebook)
        notebook.add(process_frame, text='Z3求解过程')
        
        # 求解过程文本区域
        self.process_text = scrolledtext.ScrolledText(process_frame, 
                                                     height=25,
                                                     font=("Consolas", 10),
                                                     wrap=tk.WORD)
        self.process_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 标签页3：统计图表
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text='统计分析')
        
        # 创建统计图表框架
        self.stats_canvas = tk.Canvas(stats_frame, bg='white')
        self.stats_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 标签页4：员工信息
        employee_frame = ttk.Frame(notebook)
        notebook.add(employee_frame, text='员工信息')
        
        # 创建员工信息表格
        self.create_employee_table(employee_frame)
        
        # 标签页5：约束分析
        constraint_frame = ttk.Frame(notebook)
        notebook.add(constraint_frame, text='约束分析')
        
        # 约束分析文本
        self.constraint_text = scrolledtext.ScrolledText(constraint_frame,
                                                        height=25,
                                                        font=("微软雅黑", 10),
                                                        wrap=tk.WORD)
        self.constraint_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_schedule_table(self, parent):
        """创建排班表格"""
        # 创建带滚动条的Canvas
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas用于绘制排班表
        self.schedule_canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
        
        # 滚动条
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.schedule_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.schedule_canvas.xview)
        
        self.schedule_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 布局
        self.schedule_canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # 内部框架用于放置排班内容
        self.table_frame = ttk.Frame(self.schedule_canvas)
        self.canvas_window = self.schedule_canvas.create_window((0, 0), window=self.table_frame, anchor="nw")
        
        # 绑定事件
        self.table_frame.bind("<Configure>", self.on_frame_configure)
        self.schedule_canvas.bind("<Configure>", self.on_canvas_configure)
    
    def create_employee_table(self, parent):
        """创建员工信息表格"""
        # 创建Treeview
        columns = ('id', 'name', 'position', 'exp', 'pref_shifts', 'max_days')
        self.employee_tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        # 设置列标题
        self.employee_tree.heading('id', text='工号')
        self.employee_tree.heading('name', text='姓名')
        self.employee_tree.heading('position', text='职位')
        self.employee_tree.heading('exp', text='经验(年)')
        self.employee_tree.heading('pref_shifts', text='偏好班次')
        self.employee_tree.heading('max_days', text='最大天数')
        
        # 设置列宽
        self.employee_tree.column('id', width=80)
        self.employee_tree.column('name', width=100)
        self.employee_tree.column('position', width=100)
        self.employee_tree.column('exp', width=100)
        self.employee_tree.column('pref_shifts', width=150)
        self.employee_tree.column('max_days', width=100)
        
        # 添加数据
        for emp in self.employees:
            self.employee_tree.insert('', 'end', values=(
                emp['id'],
                emp['name'],
                emp['position'],
                emp['exp'],
                ', '.join(emp['pref_shifts']),
                emp['max_days']
            ))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.employee_tree.yview)
        self.employee_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.employee_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def on_frame_configure(self, event):
        """更新Canvas的滚动区域"""
        self.schedule_canvas.configure(scrollregion=self.schedule_canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """调整Canvas内部窗口的大小"""
        self.schedule_canvas.itemconfig(self.canvas_window, width=event.width)
    
    def display_welcome_message(self):
        """显示欢迎信息"""
        welcome_text = """
        Z3 求解器在员工排班中的应用
        
        欢迎使用智能排班系统！
        
        系统功能：
        1. 自动化排班：基于Z3求解器自动生成最优排班
        2. 约束管理：支持多种硬约束和软约束
        3. 可视化展示：直观的排班表格和统计图表
        4. 优化分析：显示求解过程和约束满足情况
        
        使用步骤：
        1. 在左侧设置约束条件
        2. 点击"开始排班"进行求解
        3. 查看右侧的排班结果和统计信息
        
        Z3求解器会将排班问题转化为约束满足问题，
        并自动寻找满足所有约束的最优解。
        """
        self.process_text.insert(tk.END, welcome_text)
        self.process_text.see(tk.END)
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_var.set(f"{datetime.now().strftime('%H:%M:%S')} - {message}")
        self.root.update_idletasks()
    
    def log_process(self, message, level="INFO"):
        """记录求解过程"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "INFO":
            prefix = "ℹ"
        elif level == "SUCCESS":
            prefix = "✓"
        elif level == "ERROR":
            prefix = "✗"
        elif level == "WARNING":
            prefix = "⚠"
        else:
            prefix = "•"
        
        formatted_message = f"[{timestamp}] {prefix} {message}\n"
        self.process_text.insert(tk.END, formatted_message)
        self.process_text.see(tk.END)
    
    def start_scheduling(self):
        """开始排班求解"""
        if self.is_solving:
            messagebox.showwarning("警告", "正在求解中，请稍候...")
            return
        
        # 清空之前的显示
        self.clear_schedule_table()
        self.process_text.delete(1.0, tk.END)
        
        # 开始求解
        self.is_solving = True
        self.update_status("开始排班求解...")
        
        # 在新线程中运行求解
        import threading
        thread = threading.Thread(target=self.solve_scheduling)
        thread.daemon = True
        thread.start()
    
    def solve_scheduling(self):
        """执行排班求解"""
        try:
            self.log_process("="*60)
            self.log_process("开始排班求解")
            self.log_process("="*60)
            
            start_time = time.time()
            
            # 步骤1: 创建Z3求解器
            self.log_process("步骤1: 创建Z3求解器和优化器", "INFO")
            solver = Optimize()
            
            # 步骤2: 创建排班变量
            self.log_process("步骤2: 创建排班决策变量", "INFO")
            self.create_schedule_variables()
            
            # 步骤3: 添加约束
            self.log_process("步骤3: 添加约束条件", "INFO")
            self.add_constraints(solver)
            
            # 步骤4: 设置优化目标
            self.log_process("步骤4: 设置优化目标", "INFO")
            self.set_optimization_goals(solver)
            
            # 步骤5: 求解
            self.log_process("步骤5: 开始求解...", "INFO")
            self.log_process("Z3正在搜索可行解...", "INFO")
            
            check_time = time.time()
            result = solver.check()
            solve_time = time.time() - check_time
            
            if result == sat:
                self.log_process(f"✓ 找到可行解！求解时间: {solve_time:.2f}秒", "SUCCESS")
                
                # 获取模型
                self.model = solver.model()
                
                # 步骤6: 提取结果
                self.log_process("步骤6: 提取排班结果", "INFO")
                self.extract_schedule_result()
                
                # 步骤7: 显示结果
                self.log_process("步骤7: 生成排班表和统计", "INFO")
                self.display_schedule_result()
                
                total_time = time.time() - start_time
                self.log_process(f"✓ 排班完成！总耗时: {total_time:.2f}秒", "SUCCESS")
                self.update_status(f"排班完成！总耗时: {total_time:.2f}秒")
                
            elif result == unsat:
                self.log_process("✗ 无可行解：约束条件过于严格", "ERROR")
                self.log_process("建议：放松某些约束条件或增加员工数量", "WARNING")
                self.update_status("无可行解")
                
            else:
                self.log_process("✗ 求解未知：Z3无法确定是否有解", "ERROR")
                self.update_status("求解失败")
            
        except Exception as e:
            self.log_process(f"✗ 求解过程中出错: {str(e)}", "ERROR")
            self.update_status(f"错误: {str(e)}")
        finally:
            self.is_solving = False
    
    def create_schedule_variables(self):
        """创建排班变量"""
        self.schedule_vars = {}
        
        for emp in self.employees:
            for date in self.dates:
                for shift_name in self.shifts:
                    var_name = f"assign_{emp['id']}_{date}_{shift_name}"
                    self.schedule_vars[(emp['id'], date, shift_name)] = Bool(var_name)
        
        var_count = len(self.schedule_vars)
        self.log_process(f"创建了 {var_count} 个布尔变量", "INFO")
        self.log_process(f"员工数({len(self.employees)}) × 天数({len(self.dates)}) × 班次({len(self.shifts)}) = {var_count}", "INFO")
    
    def add_constraints(self, solver):
        """添加约束条件"""
        constraint_count = 0
        
        # 硬约束1: 每个班次必须满足最少人数要求
        if self.var_min_staff.get():
            self.log_process("添加硬约束: 班次最少人数要求", "INFO")
            for date in self.dates:
                for shift_name, shift_info in self.shifts.items():
                    min_staff = shift_info['min_staff']
                    # 统计该班次被分配的员工
                    assignments = []
                    for emp in self.employees:
                        var = self.schedule_vars[(emp['id'], date, shift_name)]
                        assignments.append(var)
                    
                    # 至少需要min_staff名员工
                    solver.add(Sum([If(v, 1, 0) for v in assignments]) >= min_staff)
                    constraint_count += 1
            
            self.log_process(f"  添加了 {len(self.dates) * len(self.shifts)} 个人数约束", "INFO")
        
        # 硬约束2: 员工每天最多只能上一个班次
        if self.var_one_shift_per_day.get():
            self.log_process("添加硬约束: 员工每天最多一个班次", "INFO")
            for emp in self.employees:
                for date in self.dates:
                    daily_shifts = []
                    for shift_name in self.shifts:
                        var = self.schedule_vars[(emp['id'], date, shift_name)]
                        daily_shifts.append(var)
                    
                    # 最多只能有一个为真
                    solver.add(Sum([If(v, 1, 0) for v in daily_shifts]) <= 1)
                    constraint_count += len(daily_shifts)
            
            self.log_process(f"  添加了 {len(self.employees) * len(self.dates)} 个唯一性约束", "INFO")
        
        # 硬约束3: 不能连续上晚班
        if self.var_no_consecutive_night.get():
            self.log_process("添加硬约束: 禁止连续晚班", "INFO")
            for emp in self.employees:
                for i in range(len(self.dates) - 1):
                    date1 = self.dates[i]
                    date2 = self.dates[i + 1]
                    
                    var1 = self.schedule_vars[(emp['id'], date1, '晚班')]
                    var2 = self.schedule_vars[(emp['id'], date2, '晚班')]
                    
                    solver.add(Implies(var1, Not(var2)))
                    constraint_count += 1
            
            self.log_process(f"  添加了 {len(self.employees) * (len(self.dates)-1)} 个连续性约束", "INFO")
        
        # 硬约束4: 限制最大工作天数
        if self.var_max_days.get():
            self.log_process("添加硬约束: 限制最大工作天数", "INFO")
            for emp in self.employees:
                max_days = emp['max_days']
                total_work_days = []
                
                for date in self.dates:
                    worked_today = []
                    for shift_name in self.shifts:
                        var = self.schedule_vars[(emp['id'], date, shift_name)]
                        worked_today.append(var)
                    
                    # 如果今天有任何班次，就算工作
                    total_work_days.append(Or(worked_today))
                
                # 转换为计数约束
                solver.add(Sum([If(v, 1, 0) for v in total_work_days]) <= max_days)
                constraint_count += 1
            
            self.log_process(f"  添加了 {len(self.employees)} 个工作量约束", "INFO")
        
        self.log_process(f"总共添加了 {constraint_count} 个硬约束", "SUCCESS")
    
    def set_optimization_goals(self, solver):
        """设置优化目标"""
        self.log_process("设置优化目标:", "INFO")
        
        # 优化目标1: 最大化偏好满足
        if self.var_preference.get():
            self.log_process("  优化目标1: 最大化员工偏好满足", "INFO")
            preference_score = []
            
            for emp in self.employees:
                preferred_shifts = emp['pref_shifts']
                for date in self.dates:
                    for shift_name in self.shifts:
                        var = self.schedule_vars[(emp['id'], date, shift_name)]
                        if shift_name in preferred_shifts:
                            preference_score.append(If(var, 1, 0))
                        else:
                            preference_score.append(If(var, 0, 1))
            
            solver.maximize(Sum(preference_score))
        
        # 优化目标2: 最小化工作量方差（公平性）
        if self.var_fairness.get():
            self.log_process("  优化目标2: 最小化工作量方差（公平性）", "INFO")
            
            # 计算每个员工的工作量
            workloads = []
            for emp in self.employees:
                emp_work = []
                for date in self.dates:
                    for shift_name in self.shifts:
                        var = self.schedule_vars[(emp['id'], date, shift_name)]
                        emp_work.append(If(var, 1, 0))
                
                workloads.append(Sum(emp_work))
            
            # 计算平均工作量
            avg_workload = Sum(workloads) / len(workloads)
            
            # 计算方差
            variance_terms = []
            for w in workloads:
                variance_terms.append((w - avg_workload) * (w - avg_workload))
            
            variance = Sum(variance_terms)
            solver.minimize(variance)
        
        # 优化目标3: 最大化连续休息日
        if self.var_consecutive_rest.get():
            self.log_process("  优化目标3: 最大化连续休息日", "INFO")
            
            consecutive_rest_score = []
            for emp in self.employees:
                for i in range(len(self.dates) - 1):
                    date1 = self.dates[i]
                    date2 = self.dates[i + 1]
                    
                    # 检查这两天是否都休息
                    worked_day1 = []
                    worked_day2 = []
                    
                    for shift_name in self.shifts:
                        worked_day1.append(self.schedule_vars[(emp['id'], date1, shift_name)])
                        worked_day2.append(self.schedule_vars[(emp['id'], date2, shift_name)])
                    
                    day1_rest = Not(Or(worked_day1))
                    day2_rest = Not(Or(worked_day2))
                    
                    consecutive_rest = And(day1_rest, day2_rest)
                    consecutive_rest_score.append(If(consecutive_rest, 1, 0))
            
            solver.maximize(Sum(consecutive_rest_score))
        
        self.log_process("优化目标设置完成", "SUCCESS")
    
    def extract_schedule_result(self):
        """从模型中提取排班结果"""
        self.schedule_result = {}
        
        # 初始化数据结构
        for date in self.dates:
            self.schedule_result[date] = {}
            for shift_name in self.shifts:
                self.schedule_result[date][shift_name] = []
        
        # 填充排班数据
        for (emp_id, date, shift_name), var in self.schedule_vars.items():
            if is_true(self.model[var]):
                # 查找员工信息
                emp_info = next((e for e in self.employees if e['id'] == emp_id), None)
                if emp_info:
                    self.schedule_result[date][shift_name].append(emp_info)
        
        self.log_process("排班结果提取完成", "SUCCESS")
    
    def display_schedule_result(self):
        """显示排班结果"""
        # 清空表格
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        # 创建表格标题
        headers = ['员工'] + self.dates_display
        for i, header in enumerate(headers):
            if i == 0:
                label = tk.Label(self.table_frame, text=header, bg='#2C3E50', fg='white',
                                font=('微软雅黑', 10, 'bold'), width=15, height=2,
                                relief='ridge', borderwidth=1)
            else:
                label = tk.Label(self.table_frame, text=header, bg='#34495E', fg='white',
                                font=('微软雅黑', 9, 'bold'), width=12, height=2,
                                relief='ridge', borderwidth=1)
            label.grid(row=0, column=i, sticky='nsew')
        
        # 创建员工行
        for row_idx, emp in enumerate(self.employees, start=1):
            # 员工姓名单元格
            emp_label = tk.Label(self.table_frame, text=emp['name'], bg='#ECF0F1',
                                font=('微软雅黑', 9), width=15, height=3,
                                relief='ridge', borderwidth=1)
            emp_label.grid(row=row_idx, column=0, sticky='nsew')
            
            # 每天的班次
            for col_idx, date in enumerate(self.dates, start=1):
                cell_frame = tk.Frame(self.table_frame, relief='ridge', borderwidth=1)
                cell_frame.grid(row=row_idx, column=col_idx, sticky='nsew')
                cell_frame.grid_propagate(False)
                
                # 检查员工在该日期的班次
                shifts_today = []
                for shift_name in self.shifts:
                    if any(e['id'] == emp['id'] for e in self.schedule_result[date][shift_name]):
                        shifts_today.append(shift_name)
                
                if shifts_today:
                    # 有班次，显示班次信息
                    shift_text = '\n'.join(shifts_today)
                    bg_color = self.shifts[shifts_today[0]]['color']
                    
                    shift_label = tk.Label(cell_frame, text=shift_text, bg=bg_color,
                                          font=('微软雅黑', 8), fg='white',
                                          justify=tk.CENTER)
                    shift_label.pack(expand=True, fill=tk.BOTH)
                    
                    # 添加提示信息
                    shift_label.bind("<Enter>", lambda e, eid=emp['id'], d=date, s=shifts_today: 
                                    self.show_shift_info(eid, d, s))
                    shift_label.bind("<Leave>", lambda e: self.hide_shift_info())
                else:
                    # 无班次（休息）
                    rest_label = tk.Label(cell_frame, text="休", bg='#BDC3C7',
                                         font=('微软雅黑', 10, 'bold'), fg='white')
                    rest_label.pack(expand=True, fill=tk.BOTH)
        
        # 设置列权重
        for i in range(len(headers)):
            self.table_frame.grid_columnconfigure(i, weight=1)
        
        # 更新约束分析
        self.update_constraint_analysis()
        
        # 更新统计图表
        self.update_statistics_charts()
    
    def show_shift_info(self, emp_id, date, shifts):
        """显示班次详细信息"""
        emp_info = next((e for e in self.employees if e['id'] == emp_id), None)
        if emp_info:
            shift_info = "\n".join([f"{s}: {self.shifts[s]['time']}" for s in shifts])
            info = f"员工: {emp_info['name']}\n日期: {date}\n班次:\n{shift_info}"
            
            # 创建提示窗口
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
            
            self.tooltip = tk.Toplevel(self.root)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{self.root.winfo_pointerx()+10}+{self.root.winfo_pointery()+10}")
            
            label = tk.Label(self.tooltip, text=info, bg='yellow', relief='solid', borderwidth=1,
                            font=('微软雅黑', 9), justify=tk.LEFT)
            label.pack()
    
    def hide_shift_info(self):
        """隐藏班次信息"""
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
    
    def clear_schedule_table(self):
        """清空排班表格"""
        for widget in self.table_frame.winfo_children():
            widget.destroy()
    
    def update_constraint_analysis(self):
        """更新约束分析"""
        if not self.model:
            return
        
        analysis_text = "约束满足情况分析\n"
        analysis_text += "=" * 40 + "\n\n"
        
        # 统计班次人数满足情况
        analysis_text += "1. 班次人数满足情况:\n"
        for date in self.dates:
            for shift_name, shift_info in self.shifts.items():
                assigned = len(self.schedule_result[date][shift_name])
                required = shift_info['min_staff']
                status = "✓ 满足" if assigned >= required else f"✗ 不足 (缺{required-assigned}人)"
                analysis_text += f"   {date} {shift_name}: {assigned}/{required} {status}\n"
        
        # 统计员工工作量
        analysis_text += "\n2. 员工工作量统计:\n"
        employee_work_counts = {}
        for emp in self.employees:
            work_count = 0
            for date in self.dates:
                for shift_name in self.shifts:
                    if any(e['id'] == emp['id'] for e in self.schedule_result[date][shift_name]):
                        work_count += 1
            employee_work_counts[emp['id']] = work_count
        
        for emp in self.employees:
            count = employee_work_counts[emp['id']]
            max_days = emp['max_days']
            status = "✓" if count <= max_days else f"✗ 超限"
            analysis_text += f"   {emp['name']}: {count}天 (上限{max_days}天) {status}\n"
        
        # 统计偏好满足情况
        analysis_text += "\n3. 员工偏好满足情况:\n"
        for emp in self.employees:
            preferred_shifts = emp['pref_shifts']
            total_assigned = 0
            preferred_assigned = 0
            
            for date in self.dates:
                for shift_name in self.shifts:
                    if any(e['id'] == emp['id'] for e in self.schedule_result[date][shift_name]):
                        total_assigned += 1
                        if shift_name in preferred_shifts:
                            preferred_assigned += 1
            
            if total_assigned > 0:
                rate = preferred_assigned / total_assigned * 100
                analysis_text += f"   {emp['name']}: {preferred_assigned}/{total_assigned} ({rate:.1f}%)\n"
        
        # 统计连续休息情况
        analysis_text += "\n4. 连续休息日统计:\n"
        for emp in self.employees:
            consecutive_rest = 0
            for i in range(len(self.dates) - 1):
                date1 = self.dates[i]
                date2 = self.dates[i + 1]
                
                day1_work = any(e['id'] == emp['id'] 
                               for shift in self.shifts 
                               for e in self.schedule_result[date1][shift])
                day2_work = any(e['id'] == emp['id'] 
                               for shift in self.shifts 
                               for e in self.schedule_result[date2][shift])
                
                if not day1_work and not day2_work:
                    consecutive_rest += 1
            
            analysis_text += f"   {emp['name']}: {consecutive_rest}次连续休息\n"
        
        self.constraint_text.delete(1.0, tk.END)
        self.constraint_text.insert(tk.END, analysis_text)
    
    def update_statistics_charts(self):
        """更新统计图表"""
        if not self.model:
            return
        
        # 清空画布
        for widget in self.stats_canvas.winfo_children():
            widget.destroy()
        
        # 创建Matplotlib图表
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.subplots_adjust(hspace=0.4, wspace=0.3)
        
        # 图表1: 员工工作量分布
        ax1 = axes[0, 0]
        employee_names = [emp['name'] for emp in self.employees]
        work_counts = []
        
        for emp in self.employees:
            count = 0
            for date in self.dates:
                for shift_name in self.shifts:
                    if any(e['id'] == emp['id'] for e in self.schedule_result[date][shift_name]):
                        count += 1
            work_counts.append(count)
        
        bars = ax1.bar(employee_names, work_counts, color='skyblue')
        ax1.set_title('员工工作量分布', fontsize=12, fontweight='bold')
        ax1.set_xlabel('员工姓名')
        ax1.set_ylabel('工作天数')
        ax1.tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        # 图表2: 班次人数统计
        ax2 = axes[0, 1]
        shift_names = list(self.shifts.keys())
        shift_counts = {s: 0 for s in shift_names}
        
        for date in self.dates:
            for shift_name in shift_names:
                shift_counts[shift_name] += len(self.schedule_result[date][shift_name])
        
        colors = [self.shifts[s]['color'] for s in shift_names]
        bars2 = ax2.bar(shift_names, [shift_counts[s] for s in shift_names], color=colors)
        ax2.set_title('班次分配统计', fontsize=12, fontweight='bold')
        ax2.set_xlabel('班次类型')
        ax2.set_ylabel('总排班次数')
        
        # 图表3: 偏好满足率
        ax3 = axes[1, 0]
        preference_rates = []
        for emp in self.employees:
            total = 0
            preferred = 0
            for date in self.dates:
                for shift_name in self.shifts:
                    if any(e['id'] == emp['id'] for e in self.schedule_result[date][shift_name]):
                        total += 1
                        if shift_name in emp['pref_shifts']:
                            preferred += 1
            
            if total > 0:
                preference_rates.append(preferred / total * 100)
            else:
                preference_rates.append(0)
        
        bars3 = ax3.bar(employee_names, preference_rates, color='lightgreen')
        ax3.set_title('员工偏好满足率', fontsize=12, fontweight='bold')
        ax3.set_xlabel('员工姓名')
        ax3.set_ylabel('偏好满足率 (%)')
        ax3.set_ylim(0, 100)
        ax3.tick_params(axis='x', rotation=45)
        
        # 图表4: 每日班次分布
        ax4 = axes[1, 1]
        daily_totals = []
        for date in self.dates:
            daily_total = 0
            for shift_name in self.shifts:
                daily_total += len(self.schedule_result[date][shift_name])
            daily_totals.append(daily_total)
        
        dates_display = [d[5:] for d in self.dates]  # 只显示月/日
        ax4.plot(dates_display, daily_totals, marker='o', linestyle='-', color='orange')
        ax4.set_title('每日总排班人数', fontsize=12, fontweight='bold')
        ax4.set_xlabel('日期')
        ax4.set_ylabel('总排班人数')
        ax4.tick_params(axis='x', rotation=45)
        
        # 将图表嵌入Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.stats_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def step_by_step_demo(self):
        """逐步求解演示"""
        self.log_process("="*60)
        self.log_process("逐步求解演示", "INFO")
        self.log_process("="*60)
        
        self.log_process("\n第一步: 问题建模", "INFO")
        self.log_process("将员工排班问题转化为约束满足问题", "INFO")
        self.log_process(f"创建 {len(self.employees)} × {len(self.dates)} × {len(self.shifts)} = "
                        f"{len(self.employees)*len(self.dates)*len(self.shifts)} 个决策变量", "INFO")
        
        self.log_process("\n第二步: 定义约束", "INFO")
        self.log_process("硬约束:", "INFO")
        self.log_process("  1. 班次人数约束: 每个班次必须满足最少人数要求", "INFO")
        self.log_process("  2. 唯一性约束: 员工每天最多一个班次", "INFO")
        self.log_process("  3. 连续性约束: 禁止连续晚班", "INFO")
        self.log_process("  4. 工作量约束: 限制最大工作天数", "INFO")
        
        self.log_process("\n软约束（优化目标）:", "INFO")
        self.log_process("  1. 最大化员工偏好满足", "INFO")
        self.log_process("  2. 最小化工作量方差", "INFO")
        self.log_process("  3. 最大化连续休息日", "INFO")
        
        self.log_process("\n第三步: Z3求解过程", "INFO")
        self.log_process("Z3使用以下步骤:", "INFO")
        self.log_process("  1. 将约束转化为SMT公式", "INFO")
        self.log_process("  2. 使用CDCL算法搜索解空间", "INFO")
        self.log_process("  3. 检查约束可满足性", "INFO")
        self.log_process("  4. 使用优化器寻找最优解", "INFO")
        self.log_process("  5. 提取模型中的变量值", "INFO")
        
        self.log_process("\n第四步: 结果分析", "INFO")
        self.log_process("分析约束满足情况:", "INFO")
        self.log_process("  - 班次人数是否满足", "INFO")
        self.log_process("  - 员工工作量是否均衡", "INFO")
        self.log_process("  - 偏好满足程度", "INFO")
        self.log_process("  - 连续休息安排", "INFO")
        
        self.log_process("\n演示结束，请点击'开始排班'进行实际求解", "SUCCESS")
    
    def export_schedule(self):
        """导出排班表"""
        if not self.schedule_result:
            messagebox.showwarning("警告", "请先生成排班表！")
            return
        
        try:
            # 创建DataFrame
            data = []
            for emp in self.employees:
                row = {'员工ID': emp['id'], '姓名': emp['name'], '职位': emp['position']}
                for date in self.dates:
                    shifts_today = []
                    for shift_name in self.shifts:
                        if any(e['id'] == emp['id'] for e in self.schedule_result[date][shift_name]):
                            shifts_today.append(shift_name)
                    row[date] = ','.join(shifts_today) if shifts_today else '休'
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # 保存为Excel
            filename = f"排班表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            
            messagebox.showinfo("导出成功", f"排班表已导出到: {filename}")
            self.update_status(f"排班表已导出: {filename}")
            
        except Exception as e:
            messagebox.showerror("导出失败", f"导出过程中出错: {str(e)}")
    
    def reset_system(self):
        """重置系统"""
        if messagebox.askyesno("确认重置", "确定要重置系统吗？所有数据将恢复到初始状态。"):
            # 重新初始化
            self.initialize_data()
            
            # 清空显示
            self.clear_schedule_table()
            self.process_text.delete(1.0, tk.END)
            self.constraint_text.delete(1.0, tk.END)
            
            # 清空统计图表
            for widget in self.stats_canvas.winfo_children():
                widget.destroy()
            
            # 重置变量
            self.solver = None
            self.model = None
            self.schedule_vars = {}
            self.schedule_result = None
            self.is_solving = False
            
            # 显示欢迎信息
            self.display_welcome_message()
            self.update_status("系统已重置")

def main():
    """主函数"""
    try:
        # 检查是否安装了Z3
        from z3 import Optimize, Bool, Sum, If, Implies, Not, And, Or
    except ImportError:
        print("错误: 未找到 Z3 模块。请使用以下命令安装:")
        print("pip install z3-solver pandas matplotlib pillow")
        return
    
    # 创建主窗口
    root = tk.Tk()
    
    # 创建应用程序
    app = EmployeeSchedulingGUI(root)
    
    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    main()

  
# Z3求解器学习视频：https://www.bilibili.com/video/BV1tu4y1u7m5/?spm_id_from=333.337.search-card.all.click&vd_source=ff6b48e1c6182a1028a46dbf3ee84a88




