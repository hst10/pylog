/*
numpy.flip(m, axis=None)
Reverse the order of elements in an array along the given axis.
The shape of the array is preserved, but the elements are reordered.

Parameters
    m : Input array.
    axis : None or int or tuple of ints, optional
        Axis or axes along which to flip over. The default, axis=None, will flip over all of the 
        axes of the input array. If axis is negative it counts from the last to the first axis.
        If axis is a tuple of ints, flipping is performed on all of the axes specified in the tuple.
Returns
    outarray_like: A view of m with the entries of axis reversed. Since a view is returned, this operation is done in constant time.

*/


//Maximum Array Size
#define MAX_SIZE 16

//TRIPCOUNT identifier
typedef float DTYPE;


extern "C" {
void reversed(const int *a, // Read-Only Input array
           int *b,       // Output Result
           int size    // size of the array
) { 
   #pragma HLS INTERFACE m_axi port=a offset=slave bundle=gmem
   #pragma HLS INTERFACE m_axi port=b offset=slave bundle=gmem

   #pragma HLS INTERFACE s_axilite port=a bundle=control
   #pragma HLS INTERFACE s_axilite port=b bundle=control
   #pragma HLS INTERFACE s_axilite port=size bundle=control
   #pragma HLS INTERFACE s_axilite port=return bundle=control

    for (int i = 0; i< size ; i++) {
       #pragma HLS LOOP_TRIPCOUNT min=MAX_SIZE max=MAX_SIZE
       #pragma HLS PIPELINE II=1
        b[i] = a[size-i-1];
    }
}
}
