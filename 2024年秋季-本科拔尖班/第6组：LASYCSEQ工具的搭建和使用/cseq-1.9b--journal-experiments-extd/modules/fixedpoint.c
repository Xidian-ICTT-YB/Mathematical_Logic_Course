#define OVERFLOWCHECK 1
#define bits __CPROVER_bitvector

#define min(k)  ((bits[k])1)<<(k-1)    // one 1 and (k-1) 0's
#define max(k) (((bits[k])1)<<(k-1))-1 // one 0 and (k-1) 1's

#define error_I <i>
#define error_F <f>
#define K (error_I+error_F)
#define K1 (K+1)
#define K2 (K*2)

#define errorbound <e>

bits[K] __cs_lasterror;
bits[K] __cs_lasterrorabs;
bits[1] __cs_boundscheck = 1;

void __CSEQ_error_bound_enable(void) { __cs_boundscheck = 1; }
void __CSEQ_error_bound_disable(void) { __cs_boundscheck = 0; }

bits[K] add_error(bits[K] __cs_errorL, bits[K] __cs_errorR) {
    bits[K] m = min(K);
    bits[K] M = max(K);

    if (__cs_errorL>0 && __cs_errorR>0 && __cs_errorL>M-__cs_errorR)
        __CPROVER_assert(0, "error overflow (insufficient integer precision) (case A)");

    if (__cs_errorL<0 && __cs_errorR<0 && __cs_errorL<m-__cs_errorR)
        __CPROVER_assert(0, "error overflow (insufficient integer precision) (case B)");

    __cs_lasterror = __cs_errorL+__cs_errorR;
    __cs_lasterrorabs = __cs_lasterror>=0?__cs_lasterror:-__cs_lasterror;

    bits[K] __cs_mask = ~0;
    __cs_mask = __cs_mask << errorbound;
    __cs_mask = __cs_mask&__cs_lasterrorabs;

    if (__cs_boundscheck && __cs_mask!=0)
        __CPROVER_assert(0, "---> error bound violation <---");

    return __cs_lasterror;
}

bits[K] mul_error(bits[K] __cs_errorL, bits[K] __cs_errorR) {
    bits[K] m = min(K);
    bits[K] M = max(K);

    bits[K2] temp = (bits[K2])__cs_errorL*(bits[K2])__cs_errorR;

    if (__cs_errorL>0 && __cs_errorR>0 || __cs_errorL<0 && __cs_errorR<0)
        if ((bits[error_I+1])(temp >> (error_I+error_F+error_F-1)) != 0) 
            __CPROVER_assert(0, "error overflow (insufficient integer precision) (case C)");

    if (__cs_errorL<0 && __cs_errorR>0 || __cs_errorL>0 && __cs_errorR<0)
        if ((bits[error_I+1])(temp >> (error_I+error_F+error_F-1)) != ~0)
            __CPROVER_assert(0, "error overflow (insufficient integer precision) (case D)");
    
    if ((bits[error_F])temp != 0)
        __CPROVER_assert(0, "error underflow (insufficient fractional precision) (case E)");

    __cs_lasterror = temp >> error_F;
    __cs_lasterrorabs = __cs_lasterror>=0?__cs_lasterror:-__cs_lasterror;

    bits[K] __cs_mask = ~0;
    __cs_mask = __cs_mask << errorbound;
    __cs_mask = __cs_mask&__cs_lasterrorabs;

    if (__cs_boundscheck && __cs_mask!=0)
        __CPROVER_assert(0, "----> error bound violation <----");

    return __cs_lasterror;
}
