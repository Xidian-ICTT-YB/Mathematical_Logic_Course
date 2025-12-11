/*
 * KLEE演示程序 - 用于软件安全课程作业
 * 展示KLEE如何自动发现常见安全漏洞
 */
#include <klee/klee.h>
#include <string.h>
#include <stdio.h>

#define BUFFER_SIZE 8
#define MAX_INPUT 16

/************************* 漏洞演示 *************************/

/* 漏洞1: 缓冲区溢出 */
void demo_buffer_overflow() {
    printf("[演示1] 缓冲区溢出检测\n");
    
    char buffer[BUFFER_SIZE];
    char user_input[MAX_INPUT];
    
    // 让KLEE符号化用户输入
    klee_make_symbolic(user_input, sizeof(user_input), "user_input");
    
    // 危险操作: 可能发生缓冲区溢出
    strcpy(buffer, user_input);  // 如果user_input长度超过BUFFER_SIZE-1，就会溢出
    
    // 我们可以通过检查buffer边界来发现溢出
    for (int i = 0; i < BUFFER_SIZE; i++) {
        if (buffer[i] == 0) break;
    }
}

/* 漏洞2: 整数溢出 */
void demo_integer_overflow() {
    printf("[演示2] 整数溢出检测\n");
    
    int a, b;
    klee_make_symbolic(&a, sizeof(a), "a");
    klee_make_symbolic(&b, sizeof(b), "b");
    
    // 危险操作: 可能发生整数溢出
    int result = a + b;
    
    // 检查是否发生了溢出
    // 如果a和b都是正数但结果是负数，说明发生了溢出
    if (a > 0 && b > 0 && result < 0) {
        printf("发现整数溢出!\n");
        klee_assert(0);  // 触发断言，让KLEE报告这个错误
    }
}

/* 漏洞3: 使用未初始化变量 */
void demo_uninitialized_variable() {
    printf("[演示3] 未初始化变量检测\n");
    
    int uninitialized_value;
    int condition;
    
    klee_make_symbolic(&condition, sizeof(condition), "condition");
    
    // 危险操作: 使用未初始化的变量
    if (condition) {
        // 在某些路径上，uninitialized_value可能被使用
        if (uninitialized_value == 0xdeadbeef) {
            printf("使用了未初始化的变量!\n");
            klee_assert(0);
        }
    }
}

/* 演示4: KLEE的路径探索能力 */
void demo_path_exploration() {
    printf("[演示4] 路径探索演示\n");
    
    int x, y;
    klee_make_symbolic(&x, sizeof(x), "x");
    klee_make_symbolic(&y, sizeof(y), "y");
    
    // 多个嵌套的条件分支
    if (x > 0) {
        if (y > 0) {
            // 路径1: x>0 && y>0
            printf("第一象限\n");
            klee_assert(0);  // 标记这个路径
        } else {
            // 路径2: x>0 && y<=0
            printf("第四象限\n");
        }
    } else {
        if (y > 0) {
            // 路径3: x<=0 && y>0
            printf("第二象限\n");
            klee_assert(0);  // 标记这个路径
        } else {
            // 路径4: x<=0 && y<=0
            printf("第三象限\n");
        }
    }
}

/************************* 主函数 *************************/

int main() {
    // printf("======================================\n");
    // printf("     KLEE自动漏洞检测演示程序\n");
    // printf("======================================\n\n");
    
    // 运行所有漏洞演示
    demo_buffer_overflow();
    demo_integer_overflow();
    demo_uninitialized_variable();
    demo_path_exploration();
    
    // printf("\n======================================\n");
    // printf("     演示程序运行结束\n");
    // printf("======================================\n");
    
    return 0;
}