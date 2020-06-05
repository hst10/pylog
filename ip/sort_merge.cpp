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
sort_merge is modified from the code in the book Parallel Programming for FPGAs by Chengyue
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

// #include <stdio.h>

//Maximum Array Size
#define MAX_SIZE 16

//TRIPCOUNT identifier
const unsigned int c_size = MAX_SIZE;

const static int SIZE = 16; // ？ 
typedef float DTYPE;
const static int STAGES = 4;

extern "C" {
void sort_merge(DTYPE a[SIZE], // Read-Only Input array
           DTYPE b[SIZE]       // Output Result
                       // size of the array
) { 
   #pragma HLS INTERFACE m_axi port=a offset=slave bundle=gmem
   #pragma HLS INTERFACE m_axi port=b offset=slave bundle=gmem

   #pragma HLS INTERFACE s_axilite port=a bundle=control
   #pragma HLS INTERFACE s_axilite port=b bundle=control
   #pragma HLS INTERFACE s_axilite port=size bundle=control
   #pragma HLS INTERFACE s_axilite port=return bundle=control

   merge_sort_parallel(a,b) ;

}


void merge_arrays(DTYPE in[SIZE], int width, DTYPE out[SIZE]) {
  int f1 = 0;
  int f2 = width;
  int i2 = width;
  int i3 = 2*width;
  if(i2 >= SIZE) i2 = SIZE;
  if(i3 >= SIZE) i3 = SIZE;
 merge_arrays:
  for (int i = 0; i < SIZE; i++) {
#pragma HLS pipeline II=1
      DTYPE t1 = in[f1];
      DTYPE t2 = (f2 == i3) ? 0 : in[f2];
    if(f2 == i3 || (f1 < i2 && t1 <= t2)) {
	  out[i] = t1;
	  f1++;
	} else {
	  assert(f2 < i3);
	  out[i] = t2;
	  f2++;
	}
	if(f1 == i2 && f2 == i3) {
      f1 = i3;
	  i2 += 2*width;
	  i3 += 2*width;
	  if(i2 >= SIZE) i2 = SIZE;
	  if(i3 >= SIZE) i3 = SIZE;
      f2 = i2;
 	}
  }
}

void merge_sort_parallel(DTYPE A[SIZE], DTYPE B[SIZE]) {
#pragma HLS dataflow

	DTYPE temp[STAGES-1][SIZE];
#pragma HLS array_partition variable=temp complete dim=1
	int width = 1;

	merge_arrays(A, width, temp[0]);
	width *= 2;

	for (int stage = 1; stage < STAGES-1; stage++) {
#pragma HLS unroll
		merge_arrays(temp[stage-1], width, temp[stage]);
		width *= 2;
	}

	merge_arrays(temp[STAGES-2], width, B);
}

}



