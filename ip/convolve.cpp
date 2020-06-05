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


//Maximum Array Size
#define MAX_SIZE 16

//TRIPCOUNT identifier
typedef float DTYPE;


extern "C" {
void convolve(const int *a, // Read-Only array A, signal
           const int *b, // Read-Only array B, filter
           int *c,       // Output Result
           int a_size,    // array A Size
           int b_size    // array B Size
) {
   #pragma HLS INTERFACE m_axi port=a offset=slave bundle=gmem
   #pragma HLS INTERFACE m_axi port=b offset=slave bundle=gmem
   #pragma HLS INTERFACE m_axi port=c offset=slave bundle=gmem

   #pragma HLS INTERFACE s_axilite port=a bundle=control
   #pragma HLS INTERFACE s_axilite port=b bundle=control
   #pragma HLS INTERFACE s_axilite port=c bundle=control
   #pragma HLS INTERFACE s_axilite port=a_size bundle=control
   #pragma HLS INTERFACE s_axilite port=b_size bundle=control
   #pragma HLS INTERFACE s_axilite port=return bundle=control

    int c_size = a_size+b_size-1;
    for (int i=0; i<c_size; i++){
        int kmin = (i>=b_size-1)? i-b_size+1 : 0;
        int kmax = (i>=a_size-1)? a_size-1 : i;
        c[i] = 0 ;
        for (int k = kmin ; k<=kmax ; k++){
            c[i] += a[k]*b[i-k];
        }
    }


}

}