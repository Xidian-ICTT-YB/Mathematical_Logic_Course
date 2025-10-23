from z3 import *
from time import time

len_bits = 1024
x = BitVec('x', len_bits)
powers = [2 ** i for i in range(len_bits)]
hack = And(x != 0, x & (x - 1) == 0)
brute = Or([x == p for p in powers])
s = Solver()
s.add(hack)
s.add(Not(brute))
set_param(verbose=10)
start = time()
if s.check() == unsat:
    print(f"Time elapsed: {time() - start}")
    print(f"Hack succeeds under {len_bits} bits.")
