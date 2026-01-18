from z3 import *

def buggy_bsearch(a, key):
    low = 0
    high = len(a) - 1
    while low < high:               # 错误：使用 '<' 而不是 '<='
        mid = (low + high) // 2
        if a[mid] == key:
            return mid
        elif a[mid] < key:
            low = mid + 1
        else:
            high = mid - 1
    return -1

def find_bsearch_bug(N=6, max_val=50, unroll=8):
    # 从整数到整数的 Z3 数组
    A = Array('A', IntSort(), IntSort())
    key = Int('key')

    s = Solver()

    # 将数组限制为在索引 0..N-1 上严格递增
    for i in range(N):
        s.add(Select(A, i) >= 0, Select(A, i) <= max_val)
    for i in range(N-1):
        s.add(Select(A, i) < Select(A, i+1))

    # 错误二分查找的循环展开
    low = [Int('low_0')]
    high = [Int('high_0')]
    s.add(low[0] == 0)
    s.add(high[0] == N-1)

    ret = [Int('ret_0')]
    s.add(ret[0] == -1)

    exited = [Bool('exited_0')]
    s.add(exited[0] == False)

    for t in range(unroll):
        lt = Bool(f'cond_{t}')
        s.add(lt == (low[t] < high[t]))

        mid = Int(f'mid_{t}')
        s.add(mid == (low[t] + high[t]) / 2)

        val_mid = Int(f'val_mid_{t}')
        s.add(val_mid == Select(A, mid))

        found = Bool(f'found_{t}')
        s.add(found == (val_mid == key))

        next_low = Int(f'low_{t+1}')
        next_high = Int(f'high_{t+1}')
        next_ret = Int(f'ret_{t+1}')
        next_exited = Bool(f'exited_{t+1}')

        already_ret = (ret[t] != -1)

        s.add(next_ret == If(already_ret, ret[t], If(lt, If(found, mid, -1), -1)))
        s.add(next_low == If(already_ret, low[t], If(lt, If(found, low[t], If(val_mid < key, mid + 1, low[t])), low[t])))
        s.add(next_high == If(already_ret, high[t], If(lt, If(found, high[t], If(val_mid < key, high[t], mid - 1)), high[t])))
        s.add(next_exited == If(already_ret, exited[t], If(lt, exited[t], True)))

        low.append(next_low)
        high.append(next_high)
        ret.append(next_ret)
        exited.append(next_exited)

    final_ret = ret[-1]

    # 规范：键存在于数组中
    idx = Int('idx_exists')
    s.add(idx >= 0, idx < N)
    s.add(Select(A, idx) == key)

    # 错误情况：尽管键存在，算法仍返回 -1
    s.add(final_ret == -1)

    # 在使用时将中间值限制在范围内
    for t in range(unroll):
        mid = Int(f'mid_{t}')
        cond = Bool(f'cond_{t}')
        # 在 t 之前的 ret：所有 ret[0..t] == -1
        not_returned_before = And(*[ret_i == -1 for ret_i in ret[:t+1]])
        s.add(Implies(And(cond, not_returned_before), And(mid >= 0, mid < N)))

    if s.check() == sat:
        m = s.model()
        arr = [m.evaluate(Select(A, i)).as_long() for i in range(N)]
        key_v = m.evaluate(key).as_long()
        idx_v = m.evaluate(idx).as_long()
        print("发现了有问题的二分查找的反例：")
        print({'array': arr, 'key': key_v, 'idx_where_key': idx_v, 'final_ret': m.evaluate(final_ret).as_long()})
        print("验证：buggy_bsearch 返回值 =", buggy_bsearch(arr, key_v))
    else:
        print("在当前约束下未找到反例。")

if __name__ == '__main__':
    find_bsearch_bug()