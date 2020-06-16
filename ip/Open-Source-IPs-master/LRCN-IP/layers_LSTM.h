#ifndef _LSTM_H_
#define _LSTM_H_

#include "LRCN.h"
#define TOTAL_B 16

void LSTMFullconnection_Layer(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> bottom[1000], hls::stream<int512> &stream512_in, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top[1024]);
void Embed_Layer(int word_input, ap_int<512> *  data, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> input_sentence[256]);

void LSTMFullconnection_Layer_loop(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> bottom[256], hls::stream<int512> &stream512_in, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top[1024]);
void Update_layer( int cont_input,  ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> hc_rst[256]);
void Add_Result_layer(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> gate_input_t[1024], ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> xcstatic_rst[1024], ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> Wxc_tm1[1024], ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> Whc_tm1[1024],ap_int<512> *  data );
void LSTM_layer(int cont_input, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> gate_input_t[1024],ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> c_tm1[256],ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> hc_tm1[256]);
void Predict_Layer(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> bottom[256] , hls::stream<int512> &stream512_in,  ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top [8801]);

int arg_max(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>  probs[8801]);





#endif
