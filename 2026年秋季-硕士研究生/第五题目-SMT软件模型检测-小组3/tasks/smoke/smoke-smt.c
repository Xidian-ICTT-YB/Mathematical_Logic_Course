extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_error(void);

int main(void) {
    int x = __VERIFIER_nondet_int();
    int y = __VERIFIER_nondet_int();

    if (x >= 10 && x <= 20 && y >= 0 && y <= 5) {
        if (x + y == 30) {
            __VERIFIER_error();
        }
    }

    return 0;
}
