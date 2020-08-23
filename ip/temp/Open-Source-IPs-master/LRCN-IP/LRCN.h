#ifndef _LRCN_H_
#define _LRCN_H_
#include <stdio.h>
#include <math.h>
#include <ap_fixed.h>
#include "hls_stream.h"
#define TOTAL_B 16

typedef ap_int<512> int512;

void LRCN_top(ap_int<512> *data);

void ALEXNET_stream_wrapper(ap_int<512> *data,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> fc8_rst[1000]);
void ALEXNET_stream_reader(ap_int<512> *data, hls::stream<int512> &stream512_out);
void ALEXNET_stream_body(hls::stream<int512> &stream512_in, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> fc8_rst[1000]);

void LSTMFC_stream_wrapper(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> bottom[1000], ap_int<512> *data, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top[1024]);
void LSTMFC_stream_reader(ap_int<512> *data, hls::stream<int512> &stream512_out);

void LSTMFC_loop_stream_wrapper(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> bottom[256], ap_int<512> * data, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top[1024]);
void LSTMFC_loop_stream_reader(ap_int<512> *data, hls::stream<int512> &stream512_out);

void Predict_stream_wrapper(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> bottom[256] , ap_int<512> *  data,  ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top [8801]);
void Predict_stream_reader(ap_int<512> *data, hls::stream<int512> &stream512_out);
#endif
