"""
Z3求解器在资源分配优化中的应用示例
场景：公司有多个项目需要分配有限的资源（人力、预算、设备）
目标：最大化总收益，同时满足各种约束条件
"""

from z3 import *

def resource_allocation_optimization():
    """
    资源分配优化问题求解
    假设：公司有4个项目，需要分配3种资源（开发人员、预算、服务器）
    目标：选择哪些项目进行投资，以最大化总收益
    """
    
    # 创建Z3求解器实例
    solver = Optimize()
    
    # ==================== 1. 定义变量 ====================
    
    # 项目决策变量：是否选择该项目 (0或1)
    project1 = Int('project1')
    project2 = Int('project2')
    project3 = Int('project3')
    project4 = Int('project4')
    
    # ==================== 2. 定义项目参数 ====================
    
    # 每个项目的收益（万元）
    profits = {
        'project1': 50,
        'project2': 80,
        'project3': 30,
        'project4': 60
    }
    
    # 每个项目的资源需求
    # 格式: [开发人员数, 预算(万元), 服务器数量]
    resource_demands = {
        'project1': [5, 20, 2],
        'project2': [8, 35, 3],
        'project3': [3, 10, 1],
        'project4': [6, 25, 2]
    }
    
    # 可用资源总量
    available_resources = {
        'developers': 12,   # 最多12名开发人员
        'budget': 50,       # 最多50万元预算
        'servers': 4        # 最多4台服务器
    }
    
    # ==================== 3. 添加约束条件 ====================
    
    print("正在添加约束条件...")
    
    # 约束1: 每个项目要么被选(1)，要么不被选(0)
    solver.add(And(project1 >= 0, project1 <= 1))
    solver.add(And(project2 >= 0, project2 <= 1))
    solver.add(And(project3 >= 0, project3 <= 1))
    solver.add(And(project4 >= 0, project4 <= 1))
    
    print("  - 项目选择约束: 每个项目只能选择(1)或不选择(0)")
    
    # 约束2: 开发人员总数不能超过可用数量
    total_developers = (project1 * resource_demands['project1'][0] + 
                       project2 * resource_demands['project2'][0] + 
                       project3 * resource_demands['project3'][0] + 
                       project4 * resource_demands['project4'][0])
    
    solver.add(total_developers <= available_resources['developers'])
    print(f"  - 开发人员约束: 总需求 ≤ {available_resources['developers']}人")
    
    # 约束3: 预算总额不能超过可用预算
    total_budget = (project1 * resource_demands['project1'][1] + 
                   project2 * resource_demands['project2'][1] + 
                   project3 * resource_demands['project3'][1] + 
                   project4 * resource_demands['project4'][1])
    
    solver.add(total_budget <= available_resources['budget'])
    print(f"  - 预算约束: 总预算 ≤ {available_resources['budget']}万元")
    
    # 约束4: 服务器总数不能超过可用数量
    total_servers = (project1 * resource_demands['project1'][2] + 
                    project2 * resource_demands['project2'][2] + 
                    project3 * resource_demands['project3'][2] + 
                    project4 * resource_demands['project4'][2])
    
    solver.add(total_servers <= available_resources['servers'])
    print(f"  - 服务器约束: 总需求 ≤ {available_resources['servers']}台")
    
    # ==================== 4. 定义目标函数 ====================
    
    # 总收益 = 各项目收益之和
    total_profit = (project1 * profits['project1'] + 
                   project2 * profits['project2'] + 
                   project3 * profits['project3'] + 
                   project4 * profits['project4'])
    
    # 告诉求解器我们要最大化总收益
    solver.maximize(total_profit)
    print(f"  - 优化目标: 最大化总收益")
    print("-" * 50)
    
    # ==================== 5. 求解问题 ====================
    
    print("正在求解优化问题...")
    
    # 检查是否存在可行解
    if solver.check() == sat:
        model = solver.model()
        
        # ==================== 6. 输出结果 ====================
        
        print("\n" + "="*60)
        print("资源分配优化结果")
        print("="*60)
        
        # 获取每个项目的选择结果
        p1_selected = model[project1].as_long()
        p2_selected = model[project2].as_long()
        p3_selected = model[project3].as_long()
        p4_selected = model[project4].as_long()
        
        selected_projects = []
        if p1_selected: selected_projects.append("项目1")
        if p2_selected: selected_projects.append("项目2")
        if p3_selected: selected_projects.append("项目3")
        if p4_selected: selected_projects.append("项目4")
        
        print(f"\n选择执行的项目: {', '.join(selected_projects) if selected_projects else '无'}")
        
        # 计算实际使用的资源
        used_developers = (p1_selected * resource_demands['project1'][0] + 
                          p2_selected * resource_demands['project2'][0] + 
                          p3_selected * resource_demands['project3'][0] + 
                          p4_selected * resource_demands['project4'][0])
        
        used_budget = (p1_selected * resource_demands['project1'][1] + 
                      p2_selected * resource_demands['project2'][1] + 
                      p3_selected * resource_demands['project3'][1] + 
                      p4_selected * resource_demands['project4'][1])
        
        used_servers = (p1_selected * resource_demands['project1'][2] + 
                       p2_selected * resource_demands['project2'][2] + 
                       p3_selected * resource_demands['project3'][2] + 
                       p4_selected * resource_demands['project4'][2])
        
        total_profit_value = (p1_selected * profits['project1'] + 
                             p2_selected * profits['project2'] + 
                             p3_selected * profits['project3'] + 
                             p4_selected * profits['project4'])
        
        print("\n资源使用情况:")
        print(f"  开发人员: {used_developers}/{available_resources['developers']}人 " + 
              f"({used_developers/available_resources['developers']*100:.1f}%)")
        print(f"  预算: {used_budget}/{available_resources['budget']}万元 " + 
              f"({used_budget/available_resources['budget']*100:.1f}%)")
        print(f"  服务器: {used_servers}/{available_resources['servers']}台 " + 
              f"({used_servers/available_resources['servers']*100:.1f}%)")
        
        print(f"\n总收益: {total_profit_value}万元")
        
        # ==================== 7. 详细分析 ====================
        
        print("\n" + "-"*60)
        print("项目详情分析:")
        print("-"*60)
        
        projects_info = [
            ("项目1", p1_selected, profits['project1'], resource_demands['project1']),
            ("项目2", p2_selected, profits['project2'], resource_demands['project2']),
            ("项目3", p3_selected, profits['project3'], resource_demands['project3']),
            ("项目4", p4_selected, profits['project4'], resource_demands['project4'])
        ]
        
        for name, selected, profit, demands in projects_info:
            status = "✓ 选择" if selected else "✗ 未选择"
            roi = profit / demands[1] if demands[1] > 0 else 0  # 投资回报率
            print(f"{name}: {status}")
            print(f"   收益: {profit}万元 | 需求: {demands[0]}人, {demands[1]}万元, {demands[2]}台")
            print(f"   投资回报率: {roi:.2f} (收益/预算)")
            print()
            
    else:
        print("无可行解！可能需要调整资源约束或项目需求。")
    
    return solver

# ==================== 8. 运行示例 ====================

if __name__ == "__main__":
    print("="*60)
    print("Z3求解器在资源分配优化中的应用演示")
    print("="*60)
    print("\n问题描述:")
    print("公司有4个项目可选，但资源有限:")
    print("  - 开发人员: 12人")
    print("  - 预算: 50万元")
    print("  - 服务器: 4台")
    print("\n目标: 选择项目组合以最大化总收益，同时不超资源限制")
    print("="*60)
    
    # 运行求解
    solver = resource_allocation_optimization()
    
    # ==================== 9. 扩展分析 ====================
    
    print("\n" + "="*60)
    print("Z3求解器在本例中的作用:")
    print("="*60)
    print("1. 约束求解: 处理整数变量和线性约束")
    print("2. 优化求解: 在满足约束的条件下最大化目标函数")
    print("3. 自动推理: 寻找满足所有约束的最优解")
    print("4. 处理0-1整数规划: 项目选择是典型的0-1决策问题")
    print("\n如果没有Z3这样的求解器，这类问题需要:")
    print("  - 手动枚举所有2^4=16种组合")
    print("  - 检查每种组合是否满足资源约束")
    print("  - 从可行解中选择收益最高的")
    print("\nZ3自动完成了这一复杂过程！")