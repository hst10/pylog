/*
numpy.argmax(a, axis=None, out=None)
Returns the indices of the minimum values along an axis.

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
           int* minindex,       // Output Result
           int size    // array A Size
) {
   #pragma HLS INTERFACE m_axi port=a offset=slave bundle=gmem
   #pragma HLS INTERFACE m_axi port=minindex offset=slave bundle=gmem

   #pragma HLS INTERFACE s_axilite port=a bundle=control
   #pragma HLS INTERFACE s_axilite port=minindex bundle=control
   #pragma HLS INTERFACE s_axilite port=size bundle=control
   #pragma HLS INTERFACE s_axilite port=return bundle=control

    int min = a[0];
    *minindex = 0;
    
    for (int i=0; i<size; i++){
        if (a[i]<min){
            min = a[i] ; 
            *minindex = i ; 
        }
    }
}
}