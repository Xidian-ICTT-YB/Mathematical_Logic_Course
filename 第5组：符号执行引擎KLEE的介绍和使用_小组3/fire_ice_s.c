#include <stdio.h>
#include "klee.h"
#include "assert.h"
#define STEPS 8   // 总共 8 步，每步只选谁动

// 4 x 9 地图
// 行列索引: map[y][x]
const char map[4][10] = {
    "#########",   // y = 0
    "#F.S.1###",   // y = 1
    "#2.DI###",    // y = 2
    "#########"    // y = 3
};

int main() {
    // 初始位置
    int fx = 1, fy = 1;   // F 在 (1,1)
    int ix = 4, iy = 2;   // I 在 (4,2)
    int switch_on = 0;

    // 每一步决定“谁动”：0=Fire 右移，1=Ice 左移
    unsigned char moves[STEPS];
    klee_make_symbolic(moves, sizeof(moves), "moves");

    // 限制取值范围，避免乱值
    for (int i = 0; i < STEPS; i++) {
        klee_assume(moves[i] == 0 || moves[i] == 1);
    }

    for (int step = 0; step < STEPS; step++) {
        unsigned char m = moves[step];

        // ---- 根据 m 选择移动谁 ----
        if (m == 0) {
            // Fire 向右走一格
            fx += 1;
        } else {
            // Ice 向左走一格
            ix -= 1;
        }

        // 边界保护（防止越界访问 map）
        klee_assert(fx >= 0 && fx < 9);
        klee_assert(fy >= 0 && fy < 4);
        klee_assert(ix >= 0 && ix < 9);
        klee_assert(iy >= 0 && iy < 4);

        char fcell = map[fy][fx];
        char icell = map[iy][ix];

        // 不能撞墙
        klee_assert(fcell != '#');
        klee_assert(icell != '#');

        // 开关：谁踩都行
        if (fcell == 'S' || icell == 'S')
            switch_on = 1;

        // 门：只有开关打开后才允许踩
        if (fcell == 'D' || icell == 'D')
            klee_assert(switch_on);

        // 成功条件：开关已开启 + Fire 在 '2' + Ice 在 '1'
        if (switch_on && fcell == '2' && icell == '1') {
            return 0;  // 找到一条成功路径
        }
    }

    // 没在有限步数内成功，视为失败路径
    klee_assert(0 && "level not solved");
    return 0;
}
