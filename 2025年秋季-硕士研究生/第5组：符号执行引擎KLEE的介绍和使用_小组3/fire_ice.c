#include <stdio.h>
#include "klee.h"
#include "assert.h"

#define STEPS 12   // 控制规模，确保 KLEE 能跑完

const char map[8][15] = {
    "##############",
    "#F..R....D..2#",
    "#.##.g.##....#",
    "#..w....S....#",
    "#..f..B..##..#",
    "#....##....#.#",
    "#....g....1..#",
    "##############"
};

int main() {

    int fx = 1, fy = 1;   // fire start
    int ix = 12, iy = 3;  // ice start

    int R = 1, B = 1;
    int switch_on = 0;

    char moves[STEPS * 2];
    klee_make_symbolic(moves, sizeof(moves), "moves");

    // ✅ 限制可选输入，避免状态爆炸
    for (int i = 0; i < STEPS * 2; i++)
        klee_assume(moves[i] == 'w' ||
                    moves[i] == 'a' ||
                    moves[i] == 's' ||
                    moves[i] == 'd');

    for (int step = 0; step < STEPS; step++) {

        // ✅ Fire move
        char fm = moves[2*step];

        // ✅ 不允许反向走（极大减少状态）
        if (step > 0) {
            char prev = moves[2*(step-1)];
            klee_assume(!(prev == 'w' && fm == 's'));
            klee_assume(!(prev == 's' && fm == 'w'));
            klee_assume(!(prev == 'a' && fm == 'd'));
            klee_assume(!(prev == 'd' && fm == 'a'));
        }

        if (fm == 'w') fy--;
        else if (fm == 's') fy++;
        else if (fm == 'a') fx--;
        else if (fm == 'd') fx++;

        // ✅ 边界保护
        klee_assert(fx >= 0 && fx < 14);
        klee_assert(fy >= 0 && fy < 8);

        char fcell = map[fy][fx];

        // ✅ 死亡条件
        klee_assert(fcell != '#');
        klee_assert(fcell != 'w');
        klee_assert(fcell != 'g');

        if (fcell == 'R' && R) R = 0;
        if (fcell == 'B' && B) B = 0;
        if (fcell == 'S') switch_on = 1;
        if (fcell == 'D') klee_assert(switch_on);


        // ✅ Ice move
        char im = moves[2*step + 1];

        if (step > 0) {
            char prev = moves[2*(step-1) + 1];
            klee_assume(!(prev == 'w' && im == 's'));
            klee_assume(!(prev == 's' && im == 'w'));
            klee_assume(!(prev == 'a' && im == 'd'));
            klee_assume(!(prev == 'd' && im == 'a'));
        }

        if (im == 'w') iy--;
        else if (im == 's') iy++;
        else if (im == 'a') ix--;
        else if (im == 'd') ix++;

        klee_assert(ix >= 0 && ix < 14);
        klee_assert(iy >= 0 && iy < 8);

        char icell = map[iy][ix];

        klee_assert(icell != '#');
        klee_assert(icell != 'f');
        klee_assert(icell != 'g');

        if (icell == 'R' && R) R = 0;
        if (icell == 'B' && B) B = 0;
        if (icell == 'S') switch_on = 1;
        if (icell == 'D') klee_assert(switch_on);


        // ✅ WIN condition
        if (!R && !B && fcell == '1' && icell == '2')
            return 0;
    }

    klee_assert(0 && "not solved");
    return 0;
}