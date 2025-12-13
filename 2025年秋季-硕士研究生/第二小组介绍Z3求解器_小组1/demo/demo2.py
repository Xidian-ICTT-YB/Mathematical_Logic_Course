from z3 import *
def demo_bitvector():
    print("\n--- Demo 2: 位向量与逆向求解 ---")
    
    #input XOR 0x1234 = 0x5678

    secret = BitVec('secret', 16)
    key = 0x1234
    target = 0x5678

    s = Solver()

    s.add(secret ^ key == target)

    s.add(secret > 0)
    
    if s.check() == sat:
        m = s.model()
        print(f"破解成功，Secret 是: {hex(m[secret].as_long())}")
    else:
        print("无法破解")

demo_bitvector()