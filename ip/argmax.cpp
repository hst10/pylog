/*
numpy.argmax(a, axis=None, out=None)
Returns the indices of the maximum values along an axis.

Parameters
    a : Input array. 
    axis : int, optional
        By default, the index is into the flattened array, otherwise along the specified axis.
    out: array, optional
        If provided, the result will be inserted into this array. It should be of the appropriate shape and dtype.    
Returns
    index_array: Array of indices into the array.
        It has the same shape as a.shape with the dimension along axis removed.
*/


//Maximum Array Size
#define MAX_SIZE 16

//TRIPCOUNT identifier
typedef float DTYPE;

// one-dimensional version
extern "C" {
void argmax(const int *a, // Read-Only array A
           int *maxindex,       // Output Result
           int size    // array A Size
) {
   #pragma HLS INTERFACE m_axi port=a offset=slave bundle=gmem
   #pragma HLS INTERFACE m_axi port=maxindex offset=slave bundle=gmem

   #pragma HLS INTERFACE s_axilite port=a bundle=control
   #pragma HLS INTERFACE s_axilite port=maxindex bundle=control
   #pragma HLS INTERFACE s_axilite port=size bundle=control
   #pragma HLS INTERFACE s_axilite port=return bundle=control

    int max = a[0];
    *maxindex = 0;
    
    for (int i=0; i<size; i++){
        if (a[i]>max){
            max = a[i] ; 
            *maxindex = i ; 
        }
    }
}
}