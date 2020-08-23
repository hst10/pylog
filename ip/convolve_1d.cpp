/*
numpy.convolve(a, v, mode='full')
Reverse the order of elements in an array along the given axis.
The shape of the array is preserved, but the elements are reordered.

Parameters
    a : Input array. First one-dimensional input array.
    v : Second one-dimensional input array.
    mode : {‘full’, ‘valid’, ‘same’}, optional
    ‘full’: By default, mode is ‘full’. This returns the convolution at each point of overlap,
        with an output shape of (N+M-1,). At the end-points of the convolution, the signals do not
        overlap completely, and boundary effects may be seen.
    ‘same’: Mode ‘same’ returns output of length max(M, N). Boundary effects are still visible.
    ‘valid’: Mode ‘valid’ returns output of length max(M, N) - min(M, N) + 1. The convolution product is only
        given for points where the signals overlap completely. Values outside the signal boundary have no effect.
Returns
    outarray_like: A view of m with the entries of axis reversed. 
                Since a view is returned, this operation is done in constant time.
*/

#include "convolve_1d.h"

void convolve_1d(DTYPE A[SIZE_A] , DTYPE B[SIZE_B], DTYPE C[SIZE_C])
{
#pragma HLS ARRAY_PARTITION variable=A complete
#pragma HLS ARRAY_PARTITION variable=B complete
#pragma HLS ARRAY_PARTITION variable=C complete


    for (int i=0; i<SIZE_C; i++){
        #pragma HLS unroll
        C[i] = 0; 
    }

    for (int m=0; m<VAR1 ; m++){
        for (int n=0; n<VAR2 ; n++){
        #pragma HLS pipeline
            for ( int i=0; i< SIZE_C ; i=i+VAR1){
                for (int k=0; k< SIZE_B; k=k+VAR2 ){
                    if ( (i-k>=0)&&(i-k<SIZE_A-1)&&(i+m<SIZE_C)&&(k+n<SIZE_B) ){
                        C[i+m] += A[k+n]*B[i+m-k-n];         
                    }
                }
            }
        } 
    }
}