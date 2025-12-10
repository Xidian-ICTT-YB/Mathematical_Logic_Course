# 规则：如果（门被撬 OR 窗被破）AND（安防开启）-> 报警。
# 设定：门没被撬，但窗破了，安防开着，问是否报警。
import cvc5
from cvc5 import Kind
import time

solver = cvc5.Solver()
solver.setOption("produce-models", "true")
solver.setLogic("ALL") # 保持原文件设置

boolSort = solver.getBooleanSort()

# 变量定义
door_open = solver.mkConst(boolSort, "Door_Open")       # 门被打开
window_broken = solver.mkConst(boolSort, "Window_Broken") # 窗户破碎
system_arm = solver.mkConst(boolSort, "System_Armed")   # 系统布防
alarm_on = solver.mkConst(boolSort, "Alarm_On")         # 警报响起

# 仿照原文件定义辅助函数
def OR(*args): return solver.mkTerm(Kind.OR, *args)
def AND(*args): return solver.mkTerm(Kind.AND, *args)
def IMPLIES(x, y): return solver.mkTerm(Kind.IMPLIES, x, y)
def NOT(x): return solver.mkTerm(Kind.NOT, x)

# 逻辑规则
# 1. 入侵 = 门开 OR 窗破
intrusion = OR(door_open, window_broken)

# 2. 如果 (入侵 AND 布防) -> 警报响
trigger_rule = IMPLIES(AND(intrusion, system_arm), alarm_on)
solver.assertFormula(trigger_rule)

# 3. 如果 (没有入侵) -> 警报不响 (防止误报)
silent_rule = IMPLIES(NOT(intrusion), NOT(alarm_on))
solver.assertFormula(silent_rule)

# 4. 设定当前状态（模拟传感器输入）
solver.assertFormula(NOT(door_open))     # 门没开
solver.assertFormula(window_broken)      # 窗户破了
solver.assertFormula(system_arm)         # 系统已布防

start_time = time.time()
result = solver.checkSat()
end_time = time.time()

print("安防状态检查:", result)
if result.isSat():
    print("Alarm State:", solver.getValue(alarm_on).getBooleanValue())
    print("Details:")
    print("  Door:", solver.getValue(door_open).getBooleanValue())
    print("  Window:", solver.getValue(window_broken).getBooleanValue())
else:
    print("逻辑矛盾")