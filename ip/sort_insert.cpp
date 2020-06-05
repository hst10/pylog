/**********
numpy.sort(a, axis=-1, kind=None, order=None)
Parameter
    a : array to be sorted
    axis : int or None, optional
        Axis along which to sort. 
        If None, the array is flattened before sorting. 
        The default is -1, which sorts along the last axis.
    kind : {‘quicksort’, ‘mergesort’, ‘heapsort’, ‘stable’}, optional
        Sorting algorithm. The default is ‘quicksort’. Note that both ‘stable’ and ‘mergesort’ use timsort or radix sort 
        under the covers and, in general, the actual implementation will vary with data type. The ‘mergesort’ option is 
        retained for backwards compatibility.Changed in version 1.15.0.: The ‘stable’ option was added.
    order : str or list of str, optional
        When a is an array with fields defined, this argument specifies which fields to compare first, second, etc. 
        A single field can be specified as a string, and not all fields need be specified, but unspecified fields will 
        still be used, in the order in which they come up in the dtype, to break ties.
Returns
    sorted_array : Array of the same type and shape as a.
**********/


/**********
sort_insert is modified from the code in the book Parallel Programming for FPGAs by Chengyue
https://github.com/KastnerRG/pp4fpgas/blob/master/examples
@misc{kastner2018parallel,
    title={Parallel Programming for FPGAs},
    author={Ryan Kastner and Janarbek Matai and Stephen Neuendorffer},
    year={2018},
    eprint={1805.03648},
    archivePrefix={arXiv},
    primaryClass={cs.AR}
}
**********/

#include "assert.h"



//Maximum Array Size
#define MAX_SIZE 16

//TRIPCOUNT identifier
typedef float DTYPE;


extern "C" {
void sort_insert(const int *a, // Read-Only Input array
           int *b,       // Output Result
           int size    // size of the array
) { 
   #pragma HLS INTERFACE m_axi port=a offset=slave bundle=gmem
   #pragma HLS INTERFACE m_axi port=b offset=slave bundle=gmem

   #pragma HLS INTERFACE s_axilite port=a bundle=control
   #pragma HLS INTERFACE s_axilite port=b bundle=control
   #pragma HLS INTERFACE s_axilite port=size bundle=control
   #pragma HLS INTERFACE s_axilite port=return bundle=control

copy_a_to_b:
    for (int i = 0; i< size ; i++) {
       #pragma HLS LOOP_TRIPCOUNT min=MAX_SIZE max=MAX_SIZE
       #pragma HLS PIPELINE II=1
        b[i] = a[i];
    }

L1:
    for(int i = 1; i < size; i++) {
      DTYPE item = b[i];
	  int j = i;
      DTYPE t = b[j-1];
    L2:
        while(j > 0 && b[j-1] > item && j > 0) {
            #pragma HLS pipeline II=1
	        b[j] = b[j-1];
	        j--;
	    }
	    b[j] = item;
  }
}
}


/*
void insertion_sort_parallel(DTYPE A[SIZE], DTYPE B[SIZE]) {
#pragma HLS array_partition variable=B complete
 L1:
    for(int i = 0; i < SIZE; i++) {
#pragma HLS pipeline II=1
        DTYPE item = A[i];
    L2:
        for(int j = SIZE-1; j >= 0; j--) {
            DTYPE t;
            if(j > i) {
                t = B[j];
            } else if(j > 0 && B[j-1] > item) {
                t = B[j-1];
            } else {
                t = item;
                if (j > 0)
                    item = B[j-1];
            }
            B[j] = t;
        }
    }
}
*/