#ifndef _ALEX_H_
#define _ALEX_H_

#include "LRCN.h"
#define TOTAL_B 16

void convolution1_layer(ap_fixed <TOTAL_B,16,AP_TRN_ZERO,AP_SAT> bottom[3][227][227],
						hls::stream<int512> &stream512_in,
                        ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> padded_rst[2][48][31][31]);

void convolution2_layer(ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>  bottom[2][48][31][31],
						hls::stream<int512> &stream512_in,
						ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> padded_rst[256][15][15]);

void convolution3_layer(ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>  bottom[256][15][15],
						hls::stream<int512> &stream512_in,
						ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT> top[2][192][15][15]);

void convolution4_layer(ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT> bottom[2][192][15][15],
						hls::stream<int512> &stream512_in,
						ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT> top[2][192][15][15]);

void convolution5_layer(ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT> bottom[2][192][15][15],
						hls::stream<int512> &stream512_in,
						ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> finalout[256][6][6]);

void fullconnection6_layer(ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> bottom[256][6][6], hls::stream<int512> &stream512_in, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top[256]);
void fullconnection7_layer(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> bottom[256], hls::stream<int512> &stream512_in, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top[256]);
void fullconnection8_layer(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> bottom[256], hls::stream<int512> &stream512_in, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top[1000]);


#endif
