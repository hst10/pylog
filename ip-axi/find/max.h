
#include "ap_int.h"
template <class DTYPE >
DTYPE max_2(DTYPE a , DTYPE b);
template <class DTYPE>
DTYPE max_4(DTYPE a0, DTYPE a1, DTYPE a2, DTYPE a3);
template <class DTYPE>
DTYPE max_8(DTYPE a0, DTYPE a1, DTYPE a2, DTYPE a3, DTYPE a4, DTYPE a5, DTYPE a6, DTYPE a7);
template <class DTYPE>
DTYPE max_16(DTYPE a0, DTYPE a1, DTYPE a2, DTYPE a3,
        DTYPE a4, DTYPE a5, DTYPE a6, DTYPE a7,
        DTYPE a8, DTYPE a9, DTYPE a10, DTYPE a11,
        DTYPE a12, DTYPE a13, DTYPE a14, DTYPE a15);
void max(
    ap_uint<32*4>* A_DDR_PORT0,
    ap_uint<32*4>* A_DDR_PORT1,
    ap_uint<32*4>* A_DDR_PORT2,
    ap_uint<32*4>* A_DDR_PORT3,
    int* size,  // bundle to port0
float* ret_max // bundle to port1
    );

