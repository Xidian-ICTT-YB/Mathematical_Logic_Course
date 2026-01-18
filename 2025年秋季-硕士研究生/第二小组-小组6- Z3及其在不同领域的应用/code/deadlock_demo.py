from z3 import *

# 两个锁 L1、L2；两个线程 T1、T2
# T1：持有 L1 的开始/结束；请求 L2 的时刻
t1_acq_l1 = Int('t1_acq_l1')
t1_rel_l1 = Int('t1_rel_l1')
t1_req_l2 = Int('t1_req_l2')

# T2：持有 L2 的开始/结束；请求 L1 的时刻
t2_acq_l2 = Int('t2_acq_l2')
t2_rel_l2 = Int('t2_rel_l2')
t2_req_l1 = Int('t2_req_l1')

s = Solver()

# 时间窗口与互异，避免等时刻边界。
times = [t1_acq_l1, t1_rel_l1, t1_req_l2, t2_acq_l2, t2_rel_l2, t2_req_l1]
for t in times:
    s.add(t >= 0, t <= 20)
s.add(Distinct(times))

# 线程内顺序：
# T1 先获取 L1，在持有 L1 的期间请求 L2，然后释放 L1。
s.add(t1_acq_l1 < t1_req_l2)
s.add(t1_req_l2 < t1_rel_l1)

# T2 先获取 L2，在持有 L2 的期间请求 L1，然后释放 L2。
s.add(t2_acq_l2 < t2_req_l1)
s.add(t2_req_l1 < t2_rel_l2)

# 已持有锁的区间必须有序（获取先于释放）。
s.add(t1_acq_l1 < t1_rel_l1)
s.add(t2_acq_l2 < t2_rel_l2)

# 死锁循环等待：请求落在对方持有区间内。
s.add(t2_acq_l2 < t1_req_l2, t1_req_l2 < t2_rel_l2)
s.add(t1_acq_l1 < t2_req_l1, t2_req_l1 < t1_rel_l1)

print("正在检查可能的死锁（含请求/释放建模）...")
if s.check() == sat:
    m = s.model()
    print("可能发生死锁。示例调度：")
    events = [
        ("t1_acq_l1", m[t1_acq_l1]), ("t1_req_l2", m[t1_req_l2]), ("t1_rel_l1", m[t1_rel_l1]),
        ("t2_acq_l2", m[t2_acq_l2]), ("t2_req_l1", m[t2_req_l1]), ("t2_rel_l2", m[t2_rel_l2]),
    ]
    events_sorted = sorted(events, key=lambda kv: kv[1].as_long())
    for name, val in events_sorted:
        print(f"  {name}: {val}")
else:
    print("在此模型下未发现死锁。")
