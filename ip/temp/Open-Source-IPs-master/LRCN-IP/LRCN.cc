#include "LRCN.h"
#include "layers_alexnet.h"
#include "layers_LSTM.h"
#define WORD_LENGTH 141269
#define LSTMFC_LENGTH 24000
#define LSTMFC_LOOP_LENGTH 6144
#define PREDICT_LENGTH 53053

FILE* test_out;

#define TOTAL_B 16


void LRCN_top(ap_int<512> *data)
{
#pragma HLS INTERFACE m_axi port=data
	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> fc8_rst[1000];
#pragma HLS ARRAY_PARTITION variable=fc8_rst dim=1 cyclic factor=8

	ap_int<32> caption[16]; //output buffer

	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> LSTM_rst[1024]; //lstm FC rst
	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> Wxc_tm1[1024]; //lstm FC loop1 rst
	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> Whc_tm1[1024]; //lstm FC loop2 rst
	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> input_sentence[256];
	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> hc_rst[256]; //update rst, lstm rst
	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> gate_input_t[1024]; //Add rst
	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> c_tm1[256];
	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> probs[8801];

#pragma HLS ARRAY_PARTITION variable=LSTM_rst dim=1 cyclic factor=8
#pragma HLS ARRAY_PARTITION variable=input_sentence dim=1 cyclic factor=8
#pragma HLS ARRAY_PARTITION variable=Wxc_tm1 dim=1 cyclic factor=8
#pragma HLS ARRAY_PARTITION variable=Whc_tm1 dim=1 cyclic factor=8
#pragma HLS ARRAY_PARTITION variable=hc_rst dim=1 cyclic factor=8
#pragma HLS ARRAY_PARTITION variable=probs dim=1 cyclic factor=8



	ALEXNET_stream_wrapper(data,fc8_rst);
//return;
	LSTMFC_stream_wrapper(fc8_rst,data+141269,LSTM_rst);

			/*FILE *xcs;
	    	xcs = fopen("Q8_xcstatic_rst.txt","w+");
	    	for(int i=0; i<1024;i++)
	    	{
	    	      fprintf(xcs, "%f\n", (float)LSTM_rst[i]);
	    	}
	    	fclose(xcs);*/

	for(int cnt=0;cnt<256;cnt++)
	{
		c_tm1[cnt]=(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> )0;
		hc_rst[cnt]=(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> )0;
	}

	int cont_input=0;
	int word_input=0;
	int LSTM_LOOP;

	for(LSTM_LOOP=0;LSTM_LOOP<15;LSTM_LOOP++){
		 if(LSTM_LOOP == 1){
			 cont_input = 1;
		 }

		Embed_Layer(word_input,data+165269,input_sentence);
					/*	FILE *ins;
		        		ins = fopen("Q8_input_sentence.txt","w+");
		            	for(int i=0; i<256;i++)
		            	{
		            	      fprintf(ins, "%f\n", (float)input_sentence[i]);
		            	}
		            	fclose(ins);*/
		LSTMFC_loop_stream_wrapper(input_sentence,data+235677, Wxc_tm1);
					/*	FILE *wxc;
						wxc = fopen("Q8_Wxc_tm1.txt","w+");
							for(int i=0; i<1024;i++)
							{
								  fprintf(wxc, "%f\n",(float) Wxc_tm1[i]);
							}
							fclose(wxc);*/
		Update_layer(cont_input, hc_rst);

		LSTMFC_loop_stream_wrapper(hc_rst,data+241821, Whc_tm1);
							/*FILE *whc;
							whc = fopen("Q8_whc.txt","w+");
								for(int i=0; i<1024;i++)
								{
									  fprintf(wxc, "%f\n",(float) Whc_tm1[i]);
								}
								fclose(whc);*/
		Add_Result_layer(gate_input_t, LSTM_rst, Wxc_tm1, Whc_tm1, data+247965);
							/*FILE *gatein;
							gatein = fopen("Q8_gatein.txt","w+");
								for(int i=0; i<1024;i++)
								{
									  fprintf(gatein, "%f\n", (float)gate_input_t[i]);
								}
								fclose(gatein);*/
		LSTM_layer(cont_input, gate_input_t, c_tm1, hc_rst);
			/* FILE *hctm1;
			hctm1 = fopen("Q8_hc_tm1.txt","w+");
				for(int i=0; i<256;i++)
				{
					  fprintf(hctm1, "%f\n", (float)hc_rst[i]);
				}
				fclose(hctm1);*/
		Predict_stream_wrapper(hc_rst, data+247997, probs);
					/*	FILE *prob;
		        		prob = fopen("Q8_prob.txt","w+");
		       			for(int i=0; i<8801;i++)
		       			{
		       				  fprintf(prob, "%f\n", (float)probs[i]);
		       			}
		       			fclose(prob);*/

	    word_input = arg_max(probs);
	    caption[LSTM_LOOP]=word_input;

	    data[301050].range(LSTM_LOOP*32+31,LSTM_LOOP*32)=caption[LSTM_LOOP].range(31,0);
	    if(word_input==0) break;
	}








/*	ap_int<512> result_tmp=0;

		for(int j=0;j<16;j++)
		{
		#pragma HLS unroll
			result_tmp.range(j*32+31,j*32)=caption[j].range(31,0);
		}
		data[2229123]=result_tmp;*/

}


void ALEXNET_stream_wrapper(ap_int<512> *data,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> fc8_rst[1000])
{
	#pragma HLS ARRAY_PARTITION variable=fc8_rst dim=1 cyclic factor=8
	#pragma HLS dataflow
		hls::stream<int512> stream512;
	#pragma HLS STREAM variable=stream512 depth=16 dim=1
		ALEXNET_stream_reader(data,stream512);
		ALEXNET_stream_body(stream512,fc8_rst);
		return;
}

void ALEXNET_stream_reader(ap_int<512> *data, hls::stream<int512> &stream512_out)
{
#pragma HLS STREAM variable=stream512_out depth=16
	for(int i=0;i<WORD_LENGTH;i++)
	{
#pragma HLS pipeline
		stream512_out.write(data[i]);
	}
}

void ALEXNET_stream_body(hls::stream<int512> &stream512_in, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> fc8_rst[1000])
{
#pragma HLS STREAM variable=stream512_in depth=16
#pragma HLS ARRAY_PARTITION variable=fc8_rst dim=1 cyclic factor=8
	ap_int<512> stream_word;


	ap_fixed <TOTAL_B,16,AP_TRN_ZERO,AP_SAT> image[3][227][227];
	#pragma HLS ARRAY_PARTITION variable=image dim=1

	ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> padded_rst_1[2][48][31][31];
#pragma HLS ARRAY_PARTITION variable=padded_rst_1 dim=2 cyclic factor=24
#pragma HLS ARRAY_PARTITION variable=padded_rst_1 dim=1
	ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> padded_rst_2[256][15][15];
#pragma HLS ARRAY_PARTITION variable=padded_rst_2 dim=1 cyclic factor=16
	ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT> padded_rst_3[2][192][15][15];
#pragma HLS ARRAY_PARTITION variable=padded_rst_3 dim=1
#pragma HLS ARRAY_PARTITION variable=padded_rst_3 dim=2 cyclic factor=24
	ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT> padded_rst_4[2][192][15][15];
#pragma HLS ARRAY_PARTITION variable=padded_rst_4 dim=1
#pragma HLS ARRAY_PARTITION variable=padded_rst_4 dim=2 cyclic factor=16
	ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> finalout[256][6][6];
#pragma HLS ARRAY_PARTITION variable=finalout dim=1 cyclic factor=8

	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> fc6_rst[256];
#pragma HLS ARRAY_PARTITION variable=fc6_rst dim=1 cyclic factor=8
	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> fc7_rst[256];
#pragma HLS ARRAY_PARTITION variable=fc7_rst dim=1 cyclic factor=8

#pragma HLS ARRAY_PARTITION variable=fc8_rst dim=1 cyclic factor=8


	for (int i=0; i<3; i++){
		 for(int j=0;j<227;j++){
			 for(int k=0;k<227;k+=32){ //8 step
				 stream_word=stream512_in.read();
				 for(int kk=0;kk<32;kk++){
					 if (k+kk<227)
						 image[i][j][k+kk].range(15,0)=stream_word.range(kk*16+15,kk*16);

				 }
			 }
		 }
	 }
	convolution1_layer(image,stream512_in,padded_rst_1);
	convolution2_layer(padded_rst_1,stream512_in,padded_rst_2);
	convolution3_layer(padded_rst_2,stream512_in,padded_rst_3);
	convolution4_layer(padded_rst_3,stream512_in,padded_rst_4);
	convolution5_layer(padded_rst_4,stream512_in,finalout);
	fullconnection6_layer(finalout, stream512_in,fc6_rst);
	fullconnection7_layer(fc6_rst, stream512_in, fc7_rst);
	fullconnection8_layer(fc7_rst,	stream512_in, fc8_rst);
}



void LSTMFC_stream_wrapper(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> bottom[1000], ap_int<512> *data, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top[1024])
{
#pragma HLS ARRAY_PARTITION variable=bottom dim=1 cyclic factor=8
#pragma HLS ARRAY_PARTITION variable=top dim=1 cyclic factor=8
#pragma HLS dataflow
	hls::stream<int512> stream512;
	LSTMFC_stream_reader(data, stream512);
	LSTMFullconnection_Layer(bottom, stream512, top);




}
void LSTMFC_stream_reader(ap_int<512> *data, hls::stream<int512> &stream512_out)
{
#pragma HLS STREAM variable=stream512_out depth=16
	for(int i=0;i<LSTMFC_LENGTH;i++)
	{
#pragma HLS pipeline
		stream512_out.write(data[i]);
	}

}


void LSTMFC_loop_stream_wrapper(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> bottom[256], ap_int<512> * data, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top[1024])
{
#pragma HLS ARRAY_PARTITION variable=bottom dim=1 cyclic factor=8
#pragma HLS ARRAY_PARTITION variable=top dim=1 cyclic factor=8
#pragma HLS dataflow
	hls::stream<int512> stream512;
	LSTMFC_loop_stream_reader(data, stream512);
	LSTMFullconnection_Layer_loop(bottom, stream512, top);
}

void LSTMFC_loop_stream_reader(ap_int<512> *data, hls::stream<int512> &stream512_out)
{
#pragma HLS STREAM variable=stream512_out depth=16
	for(int i=0;i<LSTMFC_LOOP_LENGTH;i++)
	{
#pragma HLS pipeline
		stream512_out.write(data[i]);
	}

}



void Predict_stream_reader(ap_int<512> *data, hls::stream<int512> &stream512_out)
{
#pragma HLS STREAM variable=stream512_out depth=16
	for(int i=0;i<PREDICT_LENGTH;i++)
	{
#pragma HLS pipeline
		stream512_out.write(data[i]);
	}

}

void Predict_stream_wrapper(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> bottom[256] , ap_int<512> *  data,  ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top [8801])
{
#pragma HLS ARRAY_PARTITION variable=bottom dim=1 cyclic factor=8
#pragma HLS ARRAY_PARTITION variable=top dim=1 cyclic factor=8
#pragma HLS dataflow
	hls::stream<int512> stream512;
	Predict_stream_reader(data, stream512);
	Predict_Layer(bottom, stream512, top);




}










