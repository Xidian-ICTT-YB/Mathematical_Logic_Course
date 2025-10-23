from z3 import *
from time import time

hexstr = "5616f5962674d26741d2810600a6c5647620c4e3d2870177f09716b2379012c342d3b584c5672195d653722443f1c39254360007010381b721c741a532b03504d2849382d375c0d6806251a2946335a67365020100f160f17640c6a05583f49645d3b557856221b2"
encrypted = list(reversed(bytes.fromhex("".join(reversed(hexstr)))))
len_message = len(encrypted) - 1
message = [Int(f"m{i}") for i in range(len_message)]
set_param(verbose=10)
s = Solver()

for i in range(len_message):
    if i == len_message - 33:
        s.add(message[i] == ord("|"))
    else:
        s.add(message[i] >= 32)
        s.add(message[i] < 127)
    s.add((message[i] + message[len_message - 32 + (i % 32)] + encrypted[i]) % 126 == encrypted[i + 1])

start = time()
if s.check() == sat:
    ans = s.model()
    print(f"Time elapsed: {time() - start}")
    res = ""
    for var in message:
        res += chr(ans[var].as_long())
    print(res)
else:
    print("No solutions.")
