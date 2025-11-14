#include <klee/klee.h>
#include <stdio.h>
#include <stdlib.h>

#define H 7
#define W 11
#define ITERS 28

char maze[H][W] = { "+-+---+---+",
                     "| |     |#|",
                     "| | --+ | |",
                     "| |   | | |",
                     "| +-- | | |",
                     "|     |   |",
                     "+-----+---+" };



void draw(char maze[H][W]) {
    for (int i = 0; i < H; i++) {
        for (int j = 0; j < W; j++) {
            printf("%c", maze[i][j]);
        }
        printf("\n");
    }
    printf("\n");
}

int main() {
    int x = 1, y = 1; 
    int ox, oy;
    char program[ITERS];
    
    maze[y][x] = 'X'; 
    
    klee_make_symbolic(program, sizeof(program), "program");
    
    for (int i = 0; i < ITERS; i++) {
        ox = x;
        oy = y;

        switch (program[i]) {
            case 'w': y--; break;
            case 's': y++; break;
            case 'a': x--; break;
            case 'd': x++; break;
            default:
                klee_assert(0);
        }

        
        if (maze[y][x] == '#') {
            printf("You win!\n");
            printf("Solution: ");
            for (int j = 0; j <= i; j++) printf("%c", program[j]);
            printf("\n");
            return 1;
        }

        
        if (maze[y][x] != ' ' &&
            !(y == 2 && maze[y][x] == '|' && x > 0 && x < W)) { 
            x = ox;
            y = oy;
        }

        if (ox == x && oy == y) {
            klee_assert(0);
        }

        maze[y][x] = 'X';
        draw(maze);
    }

    klee_assert(0);
}
