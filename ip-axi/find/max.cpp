#include "max.h"

template <class DTYPE >
DTYPE max_2(DTYPE a , DTYPE b){
    return a>b?a:b ;
}

template <class DTYPE>
DTYPE max_4(DTYPE a0, DTYPE a1, DTYPE a2, DTYPE a3){
    DTYPE b0,b1;
    if (a0>a1)
        b0 = a0;
    else
        b0 = a1;

    if (a2>a3)
        b1 = a2;
    else
        b1 = a3;

    if (b0>b1)
        return b0;
    else
        return b1;
}

template <class DTYPE>
DTYPE max_8(DTYPE a0, DTYPE a1, DTYPE a2, DTYPE a3, DTYPE a4, DTYPE a5, DTYPE a6, DTYPE a7){
    DTYPE c0,c1;
    c0 = max_4<DTYPE>(a0,a1,a2,a3);
    c1 = max_4<DTYPE>(a4,a5,a6,a7);
    if (c0>c1)
        return c0;
    else
        return c1;
}

template <class DTYPE>
DTYPE max_16(DTYPE a0, DTYPE a1, DTYPE a2, DTYPE a3,
        DTYPE a4, DTYPE a5, DTYPE a6, DTYPE a7,
        DTYPE a8, DTYPE a9, DTYPE a10, DTYPE a11,
        DTYPE a12, DTYPE a13, DTYPE a14, DTYPE a15){

    DTYPE d0,d1;
    d0 = max_8<DTYPE>(a0,a1,a2,a3,a4,a5,a6,a7);
    d1 = max_8<DTYPE>(a8,a9,a10,a11,a12,a13,a14,a15);
    if (d0>d1)
        return d0;
    else
        return d1;
}

#define DTYPE float
#define BITWIDTH 32
#define BATCH 16

void max(
    ap_uint<32*4>* A_DDR_PORT0,
    ap_uint<32*4>* A_DDR_PORT1,
    ap_uint<32*4>* A_DDR_PORT2,
    ap_uint<32*4>* A_DDR_PORT3,
    int* size,  // bundle to port0
    DTYPE* ret_max // bundle to port1
    )
{
    #pragma HLS interface m_axi port=A_DDR_PORT0 depth=2500 offset=slave bundle=HP0
    #pragma HLS interface m_axi port=A_DDR_PORT1 depth=2500 offset=slave bundle=HP1
    #pragma HLS interface m_axi port=A_DDR_PORT2 depth=2500 offset=slave bundle=HP2
    #pragma HLS interface m_axi port=A_DDR_PORT3 depth=2500 offset=slave bundle=HP3
    #pragma HLS interface m_axi port=size depth=1 offset=slave bundle=HP0
    #pragma HLS interface m_axi port=ret_max depth=1 offset=slave bundle=HP1
    #pragma HLS INTERFACE s_axilite port=return

    int size_buffer = *size;
    int iteration = (size_buffer%BATCH==0) ? size_buffer/BATCH : size_buffer/BATCH+1;
    DTYPE ret_max_buffer = A_DDR_PORT0[0].range(BITWIDTH-1,0);

    LOOP_PIPELINE: for(int i=0; i<iteration; i++){
        #pragma HLS pipeline
        ap_uint<128> elem0=A_DDR_PORT0[i];
        ap_uint<128> elem1=A_DDR_PORT1[i];
        ap_uint<128> elem2=A_DDR_PORT2[i];
        ap_uint<128> elem3=A_DDR_PORT3[i];

      //  DTYPE temp_A[BATCH];

        DTYPE temp_max = max_16<DTYPE>(
                elem0.range(31,0),elem0.range(63,32),elem0.range(95,64),elem0.range(127,96),
                elem1.range(31,0),elem1.range(63,32),elem1.range(95,64),elem1.range(127,96),
                elem2.range(31,0),elem2.range(63,32),elem2.range(95,64),elem2.range(127,96),
                elem3.range(31,0),elem3.range(63,32),elem3.range(95,64),elem3.range(127,96)
            );

        if(temp_max > ret_max_buffer)
            ret_max_buffer = temp_max;
    }
    *ret_max = ret_max_buffer;
}



@DTYPE@

@DTYPE@ int
@BITWIDTH@ 32
@BATCH@ 16

$IF_1$


@if@

if DTYPE = 1


if DTYPE 

@ 16 

$ IF_1$ 
IF

$if DTYPE == 1:


$DTYPE/4$
$

$

$


