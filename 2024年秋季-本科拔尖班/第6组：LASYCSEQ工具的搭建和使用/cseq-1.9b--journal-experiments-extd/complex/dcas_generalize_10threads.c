#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>


extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);
extern void __VERIFIER_atomic_begin(void);
extern void __VERIFIER_atomic_end(void);

typedef struct Node {
    int V;
    struct Node *R;
    struct Node *L;
} Node;

#define true 1
#define false 0
#define OKAY 1
#define EMPTY -2
#define FULL -1
#define null 0


int
atomic_DCAS(Node **addr1, Node **addr2, Node *old1, Node *old2, Node *new1, Node *new2) {
    int ret;
    __VERIFIER_atomic_begin();
    if (*addr1 == old1 && *addr2 == old2) {
        *addr1 = new1;
        *addr2 = new2;
        ret = true;
    } else {
        ret = false;
    }
    __VERIFIER_atomic_end();
    return ret;
}


Node *Dummy, *LeftHat, *RightHat;

int
pushRight(int v) {
    Node *nd, *rh, *lh, *rhR;
    nd = malloc(sizeof(Node));
    if (!nd) return FULL;
    nd->R = Dummy;
    nd->V = v;
    while (true) {
        rh = RightHat;
        rhR = rh->R;
        if (rhR == rh) {
            nd->L = Dummy;
            lh = LeftHat;
            if (atomic_DCAS(&RightHat, &LeftHat, rh, lh, nd, nd))
                return OKAY;
        } else {
            nd->L = rh;
            if (atomic_DCAS(&RightHat, &rh->R, rh, rhR, nd, nd))
                return OKAY;
        }
    }
}

int
popRight(void) {
    Node *rh, *lh, *rhL;
    int result;
    while (true) {
        rh = RightHat;
        lh = LeftHat;
        if (rh->R == rh)
            return EMPTY;
        if (rh == lh) {
            if (atomic_DCAS(&RightHat, &LeftHat, rh, lh, Dummy, Dummy))
                return rh->V;
        } else {
            rhL = rh->L;
            if (atomic_DCAS(&RightHat, &rh->L, rh, rhL, rhL, rh)) {
                result = rh->V;
                rh->R = Dummy;
                rh->V = null;
                return result;
            }
        }
    }
}


int
pushLeft(int v) {
    Node *nd, *lh, *rh, *lhL;
    nd = malloc(sizeof(Node)); /* Allocate new Node structure */
    if (nd == NULL) return FULL;
    nd->L = Dummy;
    nd->V = v;
    while (true) {
        lh = LeftHat;
        lhL = lh->L;
        if (lhL == lh) {
            nd->R = Dummy;
            rh = RightHat;
            if (atomic_DCAS(&LeftHat, &RightHat, lh, rh, nd, nd)) /* A’ */
                return OKAY;
        } else {
            nd->R = lh;
            if (atomic_DCAS(&LeftHat, &lh->L, lh, lhL, nd, nd)) /* B’ */
                return OKAY;
        }
    }
}

int
popLeft() {
    int result;
    Node *lh, *rh, *lhR;
    while (true) {
        lh = LeftHat; // Delicate order of operations
        rh = RightHat; // here (see proof of Theorem 4
        if (lh->L == lh) return EMPTY; // and the Conclusions section)
        if (lh == rh) {
            if (atomic_DCAS(&LeftHat, &RightHat, lh, rh, Dummy, Dummy)) /* C’ */
                return lh->V;
        } else {
            lhR = lh->R;
            if (atomic_DCAS(&LeftHat, &lh->R, lh, lhR, lhR, lh)) { /* D’ */
                result = lh->V;
                lh->L = Dummy; /* E’ */
                lh->V = null; /* optional (see text) */
                return result;
            }
        }
    }
} // Better to stack braces than to omit a lemma

#define MAX_N   3

char received[MAX_N];   // non-zero when the corresponding value is received

#define check_value(v) if(!(v >= 0 && v < MAX_N && received[v] == 0)) __VERIFIER_error(); received[v] = 1;

void initialize(void) {
    Dummy = malloc(sizeof(Node));
    Dummy->L = Dummy;
    Dummy->R = Dummy;
    LeftHat = Dummy;
    RightHat = Dummy;
}

int to_send = 0;

void *
producer(void * arg) {
    int rv = 0;

    __VERIFIER_assume(RightHat);

    while (true) {
        __VERIFIER_atomic_begin();
        __VERIFIER_assume (to_send < MAX_N);
        rv = to_send;
        to_send++;
        __VERIFIER_atomic_end();

        if (__VERIFIER_nondet_bool()) {
            pushLeft(rv);
        } else {
            pushRight(rv);
        }
        printf("sent %d\n", rv);
    }
    return 0;
}

void *
consumer(void * arg) {
    int rv = 0;

    __VERIFIER_assume(RightHat);

    while (true) {
        if (__VERIFIER_nondet_bool()) {
            rv = popLeft();
            if (rv != EMPTY) {
                printf("p1_rv=%d\n", rv);
                check_value(rv);
            }
        } else {
            rv = popRight();
            if (rv != EMPTY) {
                printf("p2_rv=%d\n", rv);
                check_value(rv);
            }
        }
    }
    return 0;
}

#define PRODUCER 5
#define CONSUMER 5

int main(void) {
    int i;

    // pthread_t t[THREADS];
    pthread_t p;
    pthread_t c;

    initialize();

    for (i = 0; i < PRODUCER; i++) {
        pthread_create(&p, 0, producer, 0);
    }
    for (i = 0; i < CONSUMER; i++) {
        pthread_create(&c, 0, consumer, 0);
    }

    return 0;
}
