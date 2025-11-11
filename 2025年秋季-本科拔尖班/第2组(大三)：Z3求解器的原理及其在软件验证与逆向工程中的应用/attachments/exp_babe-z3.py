from z3 import *
from Crypto.Util.number import *

x = [BitVec(f"x{i}", 64) for i in range(4)]
s = Solver()

a1 = x[0]
a2 = x[1]
a3 = x[2]
a4 = x[3]

# This Condition Is Fake!(!=)
s.add((a3 & a1 & (~(a4 + a2) | a2 & a2 | a4 & a1 & ~a4) ^ a4 & a3) != 0xd81ac01fbba91837)

# These Are True.
s.add((a1 & a2 & (~(a1 | a2) | a3 & a2 | a4 & a1 & ~a4) | a4 & a1 & a3) == 2316015897844654385)
s.add(((a2 ^ (a4 & ~a1 | a4 & ~a3 | (a1 + a3) & a3 | (a2 + a4) & a2 & ~a1))) == 8102257287365753684)
s.add(((a1 - a2) ^ (a3 - a4)) == 287668530830180307)
s.add(((a1 + a2 - a3 + a4) * (a1 + a3 - a4 + a2)) == 1840182356754417097)
s.add((a1 + a2 + a3 + a4) % 114514 == 21761)
s.add((a1 * a2 * a3 * a4) % 1919810 == 827118)

print(s.check())
m = s.model()
result = b""
for i in x:
    result += long_to_bytes(m[i].as_long())[::-1]
print(result)
# b'9c0525dcbadf4cbd9715067159453e74'