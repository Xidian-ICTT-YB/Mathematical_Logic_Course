"""
使用 cvc5 的 pythonic 接口求解一个基本的逻辑问题：
三个人 Alice、Bob 和 Charlie 中有人做了一件事，他们的陈述如下。
- Alice：不是我做的；
- Bob：是 Alice 做的；
- Charlie：不是我做的。
已知其中有一个人说谎，那么是谁做了这件事。
"""

from cvc5.pythonic import And, Bool, Not, Or, Solver, sat


def main():
    solver = Solver()  # 创建求解器

    a_did, b_did, c_did = (
        Bool("a_did"),
        Bool("b_did"),
        Bool("c_did"),
    )  # 创建三个布尔符号 a_did、b_did、c_did

    # 仅有一个人做了，所以 (AD && !BD && !CD) || (!AD && B D&& !CD) || (!AD && !BD && CD)
    term1 = And(a_did, Not(b_did), Not(c_did))
    term2 = And(Not(a_did), b_did, Not(c_did))
    term3 = And(Not(a_did), Not(b_did), c_did)
    solver.add(Or(term1, term2, term3))

    a_stmt = Not(a_did)  # Alice 说不是自己做的
    b_stmt = a_did  # Bob 说是 Alice 做的
    c_stmt = Not(c_did)  # Charlie 说不是自己做的

    # 仅有一个人说谎，所以 (!AS && BS && CS) || (AS && !BS && CS) || (AS && BS && !CS)
    term1 = And(Not(a_stmt), b_stmt, c_stmt)
    term2 = And(a_stmt, Not(b_stmt), c_stmt)
    term3 = And(a_stmt, b_stmt, Not(c_stmt))
    solver.add(Or(term1, term2, term3))

    if solver.check() == sat:
        model = solver.model()  # 用来获取符号的值

        who: str
        if bool(str(model[a_did])):
            who = "Alice"
        elif bool(str(model[b_did])):
            who = "Bob"
        else:
            who = "Charlie"
        print(f"有解，是 {who} 做的")
    else:
        print("无解")


if __name__ == "__main__":
    main()
