"""
使用 cvc5 的 pythonic 接口求解斑马谜题：
有五间房子，排成一排，每间房子颜色不同，住着不同国籍的人，每个人喝不同的饮料，
抽不同牌子的烟，养不同的宠物，已知
 1. 英国人住红色房子；
 2. 瑞典人养狗；
 3. 丹麦人喝茶；
 4. 绿色房子在白色房子左边；
 5. 绿色房子主人喝咖啡
 6. 抽 Pall Mall 烟的人养鸟；
 7. 黄色房子主任抽 Dunhill 烟；
 8. 住在中间房子的人喝牛奶；
 9. 挪威人住第一间房；
10. 抽 Blends 烟的人住在养猫的人隔壁；
11. 养马的人住在抽 Dunhill 烟的人隔壁；
12. 抽 Blue Master 烟的人喝啤酒；
13. 德国人抽 Prince 烟；
14. 挪威人住在蓝色房子隔壁；
15. 抽 Blends 烟的人有一个喝水的邻居。
则谁养斑马？
"""

from cvc5.pythonic import (
    Add,
    ArithRef,
    Distinct,
    Geq,
    Int,
    IntVal,
    Leq,
    Or,
    Solver,
    Sub,
    sat,
)


def main():
    solver = Solver()  # 创建求解器

    # 根据传入的字符串列表创建相应整数符号
    def terminologies(kinds: list[str]) -> list[ArithRef]:
        terms = []

        for k in kinds:
            t = Int(k)

            solver.add(Geq(t, IntVal(1)))  # x >= 1
            solver.add(Leq(t, IntVal(5)))  # x <= 5

            terms.append(t)

        solver.add(Distinct(*terms))

        return terms

    colors = ["red", "green", "white", "yellow", "blue"]
    red, green, white, yellow, blue = terminologies(colors)
    nations = ["british", "swede", "dane", "norwegian", "german"]
    british, swede, dane, norwegian, german = terminologies(nations)
    drinks = ["tea", "coffee", "milk", "beer", "water"]
    tea, coffee, milk, beer, water = terminologies(drinks)
    cigarettes = ["pall_mall", "dunhill", "blend", "blue_master", "prince"]
    pall_mall, dunhill, blends, blue_master, prince = terminologies(cigarettes)
    pets = ["dog", "bird", "cat", "horse", "zebra"]
    dog, bird, cat, horse, zebra = terminologies(pets)

    # 1. 英国人住红色房子；
    solver.add(british == red)
    # 2. 瑞典人养狗；
    solver.add(swede == dog)
    # 3. 丹麦人喝茶；
    solver.add(dane == tea)
    # 4. 绿色房子在白色房子左边；即 green - 1 = white
    solver.add(Add(green, IntVal(1)) == white)
    # 5. 绿色房子主人喝咖啡
    solver.add(green == coffee)
    # 6. 抽 Pall Mall 烟的人养鸟；
    solver.add(pall_mall == bird)
    # 7. 黄色房子主任抽 Dunhill 烟；
    solver.add(yellow == dunhill)
    # 8. 住在中间房子的人喝牛奶；中间房子值为 3
    solver.add(IntVal(3) == milk)
    # 9. 挪威人住第一间房；第一间房值为 1
    solver.add(norwegian == IntVal(1))
    # 10. 抽 Blends 烟的人住在养猫的人隔壁；即 |blend - cat| = 1
    solver.add(Or(Add(blends, IntVal(1)) == cat, Sub(blends, IntVal(1)) == cat))
    # 11. 养马的人住在抽 Dunhill 烟的人隔壁；即 |horse - dun_hill| = 1
    solver.add(Or(Add(horse, IntVal(1)) == dunhill, Sub(horse, IntVal(1)) == dunhill))
    # 12. 抽 Blue Master 烟的人喝啤酒；
    solver.add(blue_master == beer)
    # 13. 德国人抽 Prince 烟；
    solver.add(german == prince)
    # 14. 挪威人住在蓝色房子隔壁；即 |norwegian - blue| = 1
    solver.add(Or(Add(norwegian, IntVal(1)) == blue, Sub(norwegian, IntVal(1)) == blue))
    # 15. 抽 Blends 烟的人有一个喝水的邻居。 即 |blend - water| = 1
    solver.add(Or(Add(blends, IntVal(1)) == water, Sub(blends, IntVal(1)) == water))

    if solver.check() == sat:
        model = solver.model()  # 用于获取符号的值
        for i, x in enumerate([british, swede, dane, norwegian, german]):
            if int(str(model[x])) == int(str(model[zebra])):
                print(f"{nations[i]} 养斑马")

    else:
        print("无解")


if __name__ == "__main__":
    main()
