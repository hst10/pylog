#include "dcl.h"
#include <math.h>
#include <fstream>
#include <hls_math.h>
#include <ap_fixed.h>
#include <string.h>




inline FIX_FM max(FIX_FM a, FIX_FM b, FIX_FM c, FIX_FM d)
{
	FIX_FM t1, t2;

	if(a > b) t1 = a;
	else t1 = b;

	if(c > d) t2 = c;
	else t2 = d;

	if(t1 > t2) return t1;
	else return t2;
}


void max_pooling(FIX_FM buf_in[16][22][42], FIX_FM buf_out[16][10][20])
{
#pragma HLS ARRAY_PARTITION variable=buf_in cyclic dim=1 factor=16
#pragma HLS ARRAY_PARTITION variable=buf_out cyclic dim=1 factor=16

	for(int i = 0; i < 10; i++) {
		for(int j = 0; j < 20; j++) {
#pragma HLS pipeline
			for(int ch = 0; ch < 16; ch++) {
#pragma HLS unroll
				buf_out[ch][i][j] = max(buf_in[ch][i*2+1][j*2+1], buf_in[ch][i*2+1][j*2+2],
								     	  buf_in[ch][i*2+2][j*2+1], buf_in[ch][i*2+2][j*2+2]);
			}
		}
	}
}

