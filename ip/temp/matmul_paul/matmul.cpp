#include "ap_int.h"
#include "ap_fixed.h"

extern "C" {

void pl_matmul(ap_fixed<256, 256> a[1024][64], ap_fixed<256, 256> b[1024][64], ap_fixed<256, 256> c[1024][64])
{
  #pragma HLS INTERFACE m_axi port=a offset=slave bundle=data0
  #pragma HLS INTERFACE s_axilite register port=a bundle=ctrl
  #pragma HLS INTERFACE m_axi port=b offset=slave bundle=data1
  #pragma HLS INTERFACE s_axilite register port=b bundle=ctrl
  #pragma HLS INTERFACE m_axi port=c offset=slave bundle=data2
  #pragma HLS INTERFACE s_axilite register port=c bundle=ctrl
  #pragma HLS INTERFACE s_axilite register port=return bundle=ctrl

	ap_fixed<16, 16> bufferA[128][1024];
#pragma HLS array_partition variable=bufferA cyclic factor=16 dim=2
	ap_fixed<16, 16> bufferB[256];
#pragma HLS array_partition variable=bufferB complete dim=1
	ap_fixed<16, 16> tmp[128][256];
#pragma HLS array_partition variable=tmp complete dim=2
	ap_fixed<256, 256> tmp_256[1];

	
	for (int i = 0; i < 1024; i += 128) {
		for(int ii = 0; ii < 128; ii++) {
			for (int k = 0; k < 1024; k += 16) {
#pragma HLS pipeline
				tmp_256[0] = a[i+ii][k/16];
				for(int kk = 0; kk < 16; kk++) {
#pragma HLS unroll
					bufferA[ii][k+kk].range(15, 0) = tmp_256[0].range(kk*16+15, kk*16);
				}
			}
		}

		for (int j = 0; j < 1024; j += 256) {
			for(int ii = 0; ii < 128; ii++) {
#pragma HLS pipeline
				for (int jj = 0; jj < 256; jj += 1) {
#pragma HLS unroll
					tmp[ii][jj] = 0;
				}
			}

			for (int k = 0; k < 1024; k += 1) {
				for (int jj = 0; jj < 256; jj += 16) {
#pragma HLS pipeline
					tmp_256[0] = b[k][(j+jj)/16];
					for (int jjj = 0; jjj < 16; jjj += 1) {
#pragma HLS unroll
						bufferB[jj+jjj].range(15, 0) = tmp_256[0].range(jjj*16+15, jjj*16);
					}
				}

				for(int ii = 0; ii < 128; ii++) {
#pragma HLS pipeline
					for (int jj = 0; jj < 256; jj += 1) {
#pragma HLS unroll
						tmp[ii][jj] += bufferA[ii][k] * bufferB[jj];
					}
				}
			}

			for(int ii = 0; ii < 128; ii++) {
				for (int jj = 0; jj < 256; jj += 16) {
#pragma HLS pipeline
					for (int jjj = 0; jjj < 16; jjj += 1) {
#pragma HLS unroll
						tmp_256[0].range(jjj*16+15, jjj*16) = tmp[ii][jj+jjj];
					}
					c[i+ii][(j+jj)/16] = tmp_256[0];
				}
			}
		}
	}
}

}


/*void matmul(int16_t a[1024][1024], int16_t b[1024][1024], int16_t c[1024][1024])
{
	int16_t bufferA[256][1024];
#pragma HLS array_partition variable=bufferA cyclic factor=256 dim=2
	int16_t bufferB[256];
#pragma HLS array_partition variable=bufferB complete dim=1
	int16_t tmp[256][256];
#pragma HLS array_partition variable=tmp complete dim=2
	for (int i = 0; i < 1024; i += 128) {
		for(int ii = 0; ii < 128; ii++) {
			for (int k = 0; k < 1024; k += 1) {
#pragma HLS pipeline
				bufferA[ii][k] = a[i+ii][k];
			}
		}

		for (int j = 0; j < 1024; j += 256) {
			for(int ii = 0; ii < 256; ii++) {
#pragma HLS pipeline
				for (int jj = 0; jj < 256; jj += 1) {
#pragma HLS unroll
					tmp[ii][jj] = 0;
				}
			}

			for (int k = 0; k < 1024; k += 1) {
				for (int jj = 0; jj < 256; jj += 1) {
#pragma HLS pipeline
					bufferB[jj] = b[k][j+jj];
				}

				for(int ii = 0; ii < 128; ii++) {
#pragma HLS pipeline
					for (int jj = 0; jj < 256; jj += 1) {
#pragma HLS unroll
						tmp[ii][jj] += bufferA[ii][k] * bufferB[jj];
					}
				}
			}
			for(int ii = 0; ii < 128; ii++) {
				for (int jj = 0; jj < 256; jj += 1) {
#pragma HLS pipeline
					c[i+ii][j + jj] = tmp[ii][jj];
				}
			}
		}
	}
}*/
