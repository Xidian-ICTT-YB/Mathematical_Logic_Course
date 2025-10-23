#include <klee/klee.h>
void KLEE_assume(int x) {while(!(x));}
int KLEE_nondet_int() { int x; klee_make_symbolic(&x, sizeof(x), "x"); return x; }
unsigned int KLEE_nondet_uint() { unsigned int x; klee_make_symbolic(&x, sizeof(x), "x"); return x; }
_Bool KLEE_nondet_bool() { _Bool x; klee_make_symbolic(&x, sizeof(x), "x"); return x; }
char KLEE_nondet_char() { char x; klee_make_symbolic(&x, sizeof(x), "x"); return x; }
unsigned char KLEE_nondet_uchar() { unsigned char x; klee_make_symbolic(&x, sizeof(x), "x"); return x; }
