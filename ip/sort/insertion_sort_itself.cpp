#include "insertion_sort_itself.h"

void insertion_sort_itself(DTYPE A[SIZE]) {
 L1:
    for(int i = 1; i < SIZE; i++) {
	#pragma HLS LOOP_TRIPCOUNT min=MAX_SIZE max=MAX_SIZE
        DTYPE item = A[i];
        int j = i;
        DTYPE t = A[j-1];
    L2:
        while(j > 0 && t > item) {
			#pragma HLS LOOP_TRIPCOUNT min=0 max=MAX_SIZE
			#pragma HLS pipeline II=2
            A[j] = t;
            t = A[j-2];
            j--;
        }
        A[j] = item;
    }
}