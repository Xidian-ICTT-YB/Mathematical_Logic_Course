from z3 import *

x, y = Ints('x y')


X = x > 350
Y = y > 234

R = If(X, If(Y, -1, 114), 514)

s = Solver()
s.add(R == -1) # Error Condition.

if s.check() == sat:
    print("Error condition is reachable.")
    print(s.model())

# Error condition is reachable.
# [y = 235, x = 351]

