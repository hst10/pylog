/*
numpy.argmin(a, axis=None, out=None)
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
#include "argmin.h"
void argmin(DTYPE A[SIZE] , int* min_index )
{
    DTYPE min = min_f1(A);
    DTYPE temp[VAR2];
    for (int i=0; i<VAR2; i++){
    #pragma HLS unroll
    	temp[i] = SIZE;}

    for (int i=BOUND-1; i>=0; i--){
    #pragma HLS pipeline
        for (int j=0 ; j< VAR2 ; j++){
            if ( i*VAR2+j< SIZE && A[i*VAR2+j] == min ){
                temp[j] = i*VAR2+j ;
    }   }   }

    for (int i=0;i<VAR2;i++)
        *min_index = min_f2(temp);
}



DTYPE min_f1(DTYPE A[SIZE]){
    DTYPE temp[STAGE][BATCH/2];
    DTYPE min_value = A[0];
    #pragma HLS ARRAY_PARTITION variable=temp complete
    #pragma HLS ARRAY_PARTITION variable=A complete

    for (int i=0; i<ITERATION; i++){
        #pragma HLS pipeline
        for(int b=0;b<BATCH;b=b+2){ // BATCH = 2^n
        	if( i*BATCH+b+1 <SIZE ){
                temp[0][b/2] = min_unit(A[i*BATCH+b],A[i*BATCH+b+1]);
        	}else if(i*BATCH+b<SIZE && i*BATCH+b+1>=SIZE ){
        	    temp[0][b/2] = min_unit(A[i*BATCH+b],A[0]);
        	}else {
        		temp[0][b/2] = A[0] ;
        }   }

        for (int s=0; s<STAGE-1; s++){
            for(int m=0; m<BATCH/2; m=m+2){
                temp[s+1][m/2]= min_unit(temp[s][m],temp[s][m+1]);
        }   }

        if(temp[STAGE-1][0]<min_value)
                min_value = temp[STAGE-1][0];
        if(temp[STAGE-1][1]< min_value)
            min_value = temp[STAGE-1][1];
    }
    return min_value;
}


int min_f2(int A[VAR2]){
    int temp[STAGE_2][VAR2/2];
    int min_value = A[0];
#pragma HLS ARRAY_PARTITION variable=temp complete
#pragma HLS ARRAY_PARTITION variable=A complete

    #pragma HLS pipeline
    for(int b=0;b<VAR2;b=b+2){ // VAR2 = 2^n
        temp[0][b/2] = min_unit(A[b],A[b+1]);}

    for (int s=0; s<STAGE_2-1; s++){
        for(int m=0; m<VAR2/2; m=m+2){
            temp[s+1][m/2]= min_unit(temp[s][m],temp[s][m+1]);
    }   }

    if(temp[STAGE_2-1][0]<min_value)
        min_value = temp[STAGE_2-1][0];
    if(temp[STAGE_2-1][1]<min_value)
        min_value = temp[STAGE_2-1][1];
    return min_value;
}

DTYPE min_unit(DTYPE a , DTYPE b){
    return a<b?a:b ;
}

