#include "max.h"

void max(DTYPE A[SIZE] , DTYPE* max ){
    DTYPE temp[STAGE][BATCH/2];
    DTYPE max_value = A[0];
#pragma HLS ARRAY_PARTITION variable=temp complete
#pragma HLS ARRAY_PARTITION variable=A complete

    for (int i=0; i<ITERATION; i++){
        #pragma HLS pipeline
        for(int b=0;b<BATCH;b=b+2){ // BATCH = 2^n
        	if( i*BATCH+b+1 <SIZE ){
            temp[0][b/2] = max_unit(A[i*BATCH+b],A[i*BATCH+b+1]);
        	}else if(i*BATCH+b<SIZE && i*BATCH+b+1>=SIZE ){
        	temp[0][b/2] = max_unit(A[i*BATCH+b],0);
        	}else {
        		temp[0][b/2] = 0 ;
        	}
        }

        for (int s=0; s<STAGE-1; s++){
            for(int m=0; m<BATCH/2; m=m+2){
                temp[s+1][m/2]= max_unit(temp[s][m],temp[s][m+1]);
        }    }
        
        if(temp[STAGE-1][0]>max_value)
            max_value = temp[STAGE-1][0];
        if(temp[STAGE-1][1]>max_value)
            max_value = temp[STAGE-1][1];
    }        
    *max= max_value;
}

DTYPE max_unit(DTYPE a , DTYPE b){
    return a>b?a:b ;
}