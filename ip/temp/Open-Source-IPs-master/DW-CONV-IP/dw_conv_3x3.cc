

// conv 3x3 for group (depth-wise convolutions)

#include <stdio.h>
#include <math.h>
#include <ap_fixed.h>
#include "hls_stream.h"
#include "dcl.h"


void load_weights(FIX_WT weight_buf[DEPTH],
				  FIX_WT weights[DEPTH][3][3],
				  int i, int j)
{
#pragma HLS ARRAY_PARTITION variable=weights dim=1 factor=16

	for(int coo = 0; coo < 16; coo++){
#pragma HLS unroll
		weight_buf[coo] = weights[coo][i][j];
	}
}


void CONV_3x3_group(FIX_FM bottom[DEPTH][HEIGH][WIDTH],
					FIX_FM top[DEPTH][HEIGH][WIDTH],
					FIX_WT weights[DEPTH][3][3])
{

	FIX_WT weight_buf[DEPTH];

#pragma HLS ARRAY_PARTITION variable=bottom cyclic dim=1 factor=16
#pragma HLS ARRAY_PARTITION variable=top cyclic dim=1 factor=16
#pragma HLS ARRAY_PARTITION variable=weight_buf complete


	for(int i = 0; i < 3; i++){
		for(int j = 0; j < 3; j++){

#pragma HLS dataflow

			load_weights(weight_buf, weights, i, j);

			for(int h = 1; h <= HEIGH-2; h++){
				for(int w = 1; w <= WIDTH-2; w++){
#pragma HLS pipeline
					for(int co = 0; co < 16; co++){
#pragma HLS unroll
						top[co][h][w] += weight_buf[co] * bottom[co][h+i-1][w+j-1];
					}
				}
			}
		}
	}
}

