#include "LRCN.h"
#define TOTAL_B 16


ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> compute_engine_LSTM(ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight0,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot0,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight1,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot1,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight2,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot2,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight3,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot3,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight4,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot4,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight5,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot5,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight6,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot6,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight7,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot7

								)
{
#pragma HLS pipeline
	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> mul0,mul1,mul2,mul3,mul4,mul5,mul6,mul7;

	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> add00,add01,add02,add03;

	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> add10,add11;

	mul0=weight0*bot0;
	mul1=weight1*bot1;
	mul2=weight2*bot2;
	mul3=weight3*bot3;
	mul4=weight4*bot4;
	mul5=weight5*bot5;
	mul6=weight6*bot6;
	mul7=weight7*bot7;


	add00=mul0+mul1;
	add01=mul2+mul3;
	add02=mul4+mul5;
	add03=mul6+mul7;


	add10=add00+add01;
	add11=add02+add03;


	return add10+add11;
}


void LSTMFullconnection_Layer(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> bottom[1000], hls::stream<int512> &stream512_in, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top[1024])
{


	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight[2][8][8];

#pragma HLS ARRAY_PARTITION variable=weight dim=1
#pragma HLS ARRAY_PARTITION variable=weight dim=2
#pragma HLS ARRAY_PARTITION variable=bottom dim=1 cyclic factor=8
#pragma HLS ARRAY_PARTITION variable=top dim=1 cyclic factor=8

ap_int<512> stream_temp;
    for(int i=0;i<1024;i+=8)
    {
#pragma HLS pipeline
    	for(int j=0;j<8;j++)
    	{
#pragma HLS unroll factor=8
    			top[i+j]=0;
    	}
    }

                for(int c=0;c<1000;c+=8){
                  for(int n=0;n<1024 ;n+=16){
#pragma HLS pipeline
                	  stream_temp=stream512_in.read();
						  for(int i=0;i<8;i++)
							{

					#pragma HLS unroll
								for(int j=0;j<8;j++)
								{
					#pragma HLS unroll
									weight[0][i][j].range(3,0)=stream_temp.range( (i*8+j)*8+3,(i*8+j)*8);
									weight[1][i][j].range(3,0)=stream_temp.range( (i*8+j)*8+7,(i*8+j)*8+4);
								}

							}

						  stream_temp=stream512_in.read();
							for(int i=0;i<8;i++)
							{

					#pragma HLS unroll
								for(int j=0;j<8;j++)
								{
					#pragma HLS unroll
									weight[0][i][j].range(7,4)=stream_temp.range( (i*8+j)*8+3,(i*8+j)*8);
									weight[1][i][j].range(7,4)=stream_temp.range( (i*8+j)*8+7,(i*8+j)*8+4);
								}

							}

							stream_temp=stream512_in.read();
							for(int i=0;i<8;i++)
							{

					#pragma HLS unroll
								for(int j=0;j<8;j++)
								{
					#pragma HLS unroll
									weight[0][i][j].range(11,8)=stream_temp.range( (i*8+j)*8+3,(i*8+j)*8);
									weight[1][i][j].range(11,8)=stream_temp.range( (i*8+j)*8+7,(i*8+j)*8+4);
								}

							}


						for(int nn=0;nn<8;nn++)
						{
							/*for(int cc=0;cc<8;cc++){
								top[n+nn]+=weight[0][nn][cc]*bottom[c+cc];
							}*/
						#pragma HLS unroll
							top[n+nn]+=compute_engine_LSTM(
									weight[0][nn][0],    bottom[c+0],
									weight[0][nn][1],    bottom[c+1],
									weight[0][nn][2],    bottom[c+2],
									weight[0][nn][3],    bottom[c+3],
									weight[0][nn][4],    bottom[c+4],
									weight[0][nn][5],    bottom[c+5],
									weight[0][nn][6],    bottom[c+6],
									weight[0][nn][7],    bottom[c+7]);
						}


						for(int nn=0;nn<8;nn++)
						{
							/*for(int cc=0;cc<8;cc++){
								top[n+8+nn]+=weight[1][nn][cc]*bottom[c+cc];
							}*/
						#pragma HLS unroll
							top[n+8+nn]+=compute_engine_LSTM(
									weight[1][nn][0],    bottom[c+0],
									weight[1][nn][1],    bottom[c+1],
									weight[1][nn][2],    bottom[c+2],
									weight[1][nn][3],    bottom[c+3],
									weight[1][nn][4],    bottom[c+4],
									weight[1][nn][5],    bottom[c+5],
									weight[1][nn][6],    bottom[c+6],
									weight[1][nn][7],    bottom[c+7]);
						}
                    }
}




}



ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> compute_engine_LSTM_loop(ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight0,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot0,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight1,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot1,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight2,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot2,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight3,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot3,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight4,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot4,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight5,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot5,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight6,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot6,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight7,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot7

								)
{
#pragma HLS pipeline
	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> mul0,mul1,mul2,mul3,mul4,mul5,mul6,mul7;

	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> add00,add01,add02,add03;

	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> add10,add11;

	mul0=weight0*bot0;
	mul1=weight1*bot1;
	mul2=weight2*bot2;
	mul3=weight3*bot3;
	mul4=weight4*bot4;
	mul5=weight5*bot5;
	mul6=weight6*bot6;
	mul7=weight7*bot7;


	add00=mul0+mul1;
	add01=mul2+mul3;
	add02=mul4+mul5;
	add03=mul6+mul7;


	add10=add00+add01;
	add11=add02+add03;


	return add10+add11;
}
void LSTMFullconnection_Layer_loop(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> bottom[256], hls::stream<int512> &stream512_in, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top[1024])
{


	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight[2][8][8];

#pragma HLS ARRAY_PARTITION variable=weight dim=1
#pragma HLS ARRAY_PARTITION variable=weight dim=2
#pragma HLS ARRAY_PARTITION variable=bottom dim=1 cyclic factor=8
#pragma HLS ARRAY_PARTITION variable=top dim=1 cyclic factor=8
	ap_int<512> stream_temp;

    for(int i=0;i<1024;i+=8)
    {
#pragma HLS pipeline
    	for(int j=0;j<8;j++)
    	{
#pragma HLS unroll factor=8
    			top[i+j]=0;
    	}
    }

                for(int c=0;c<256;c+=8){
                  for(int n=0;n<1024 ;n+=16){
#pragma HLS pipeline
                	  stream_temp=stream512_in.read();
						  for(int i=0;i<8;i++)
							{

					#pragma HLS unroll
								for(int j=0;j<8;j++)
								{
					#pragma HLS unroll
									weight[0][i][j].range(3,0)=stream_temp.range( (i*8+j)*8+3,(i*8+j)*8);
									weight[1][i][j].range(3,0)=stream_temp.range( (i*8+j)*8+7,(i*8+j)*8+4);
								}

							}
						  stream_temp=stream512_in.read();

							for(int i=0;i<8;i++)
							{

					#pragma HLS unroll
								for(int j=0;j<8;j++)
								{
					#pragma HLS unroll
									weight[0][i][j].range(7,4)=stream_temp.range( (i*8+j)*8+3,(i*8+j)*8);
									weight[1][i][j].range(7,4)=stream_temp.range( (i*8+j)*8+7,(i*8+j)*8+4);
								}

							}
							stream_temp=stream512_in.read();

							for(int i=0;i<8;i++)
							{

					#pragma HLS unroll
								for(int j=0;j<8;j++)
								{
					#pragma HLS unroll
									weight[0][i][j].range(11,8)=stream_temp.range( (i*8+j)*8+3,(i*8+j)*8);
									weight[1][i][j].range(11,8)=stream_temp.range( (i*8+j)*8+7,(i*8+j)*8+4);
								}

							}


						for(int nn=0;nn<8;nn++)
						{
							/*for(int cc=0;cc<8;cc++){
								top[n+nn]+=weight[0][nn][cc]*bottom[c+cc];
							}*/
						#pragma HLS unroll
							top[n+nn]+=compute_engine_LSTM_loop(
									weight[0][nn][0],    bottom[c+0],
									weight[0][nn][1],    bottom[c+1],
									weight[0][nn][2],    bottom[c+2],
									weight[0][nn][3],    bottom[c+3],
									weight[0][nn][4],    bottom[c+4],
									weight[0][nn][5],    bottom[c+5],
									weight[0][nn][6],    bottom[c+6],
									weight[0][nn][7],    bottom[c+7]);
						}


						for(int nn=0;nn<8;nn++)
						{
							/*for(int cc=0;cc<8;cc++){
								top[n+8+nn]+=weight[1][nn][cc]*bottom[c+cc];
							}*/
						#pragma HLS unroll
							top[n+8+nn]+=compute_engine_LSTM_loop(
									weight[1][nn][0],    bottom[c+0],
									weight[1][nn][1],    bottom[c+1],
									weight[1][nn][2],    bottom[c+2],
									weight[1][nn][3],    bottom[c+3],
									weight[1][nn][4],    bottom[c+4],
									weight[1][nn][5],    bottom[c+5],
									weight[1][nn][6],    bottom[c+6],
									weight[1][nn][7],    bottom[c+7]);
						}
                    }
}


}


void Embed_Layer(int word_input, ap_int<512> *  data, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> input_sentence[256])
{

	//load required embed_weights
	//8801*1000 array is mapped into AXI addr.
	//1000 16-bit data need 32 rows AXI addr.
	//8801*1000 need 281632 rows

	if (word_input < 0 || word_input >= 8801) { printf("illegal input\n"); return; }
	data = data + word_input*8;
	for(int i=0;i<256;i+=32){
		for (int ii=0;ii<32;ii++){
#pragma HLS pipeline
			ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> temp;
			temp.range(11,0)=(*data).range((ii)*12+11,(ii)*12);
			input_sentence[i+ii]=temp;
		}
		data++;
	}
              //printf("choice word: %d", word_input);
              /*FILE *buf_file;
                  buf_file = fopen("tx_stence_buf.txt","w+");
                  for (int iii=0; iii<1000; iii++){
                    fprintf(buf_file, "%f\n", (float)input_sentence[iii]);
                  }
                fclose(buf_file);*/

              ///////////////
}

void Predict_Layer(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> bottom[256] , hls::stream<int512> &stream512_in,  ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top [8801])
{


	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight[2][8][8];
	ap_int<512> stream_temp;
#pragma HLS ARRAY_PARTITION variable=weight dim=1
#pragma HLS ARRAY_PARTITION variable=weight dim=2

#pragma HLS ARRAY_PARTITION variable=bottom dim=1 cyclic factor=8
#pragma HLS ARRAY_PARTITION variable=top dim=1 cyclic factor=8

	for(int i=0;i<8800;i+=40)
	{
#pragma HLS pipeline
		stream_temp=stream512_in.read();
    	for(int j=0;j<40;j+=8)
    	{
#pragma HLS unroll
    		for(int k=0;k<8;k++)
    		{
#pragma HLS unroll factor=8
    			ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> temp;
    			temp.range(11,0)=stream_temp.range((j+k)*12+11,(j+k)*12);
    			top[i+j+k]=temp;
    		}
    	}


    }
	stream_temp=stream512_in.read();
	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> temp2;
	temp2.range(11,0)=stream_temp.range(11,0);
	top[8800]=temp2;


  ///////////////////////
  /*FILE *buf_file;
    buf_file = fopen("tx_predic_b.txt","w+");
    for (int iii=0; iii<8801; iii++){
      fprintf(buf_file, "%f\n", (float)top[iii]);
    }
  fclose(buf_file);*/
  /////////////////////////


			for( int n = 0; n < 8800; n+=16)
			{
			for(int c = 0; c < 256; c+=8){
#pragma HLS pipeline
				stream_temp=stream512_in.read();
          		for(int i=0;i<8;i++)
				{

			#pragma HLS unroll
						for(int j=0;j<8;j++)
						{
			#pragma HLS unroll
							weight[0][i][j].range(3,0)=stream_temp.range( (i*8+j)*8+3,(i*8+j)*8);
							weight[1][i][j].range(3,0)=stream_temp.range( (i*8+j)*8+7,(i*8+j)*8+4);
						}

					}
          		stream_temp=stream512_in.read();


					for(int i=0;i<8;i++)
					{

			#pragma HLS unroll
						for(int j=0;j<8;j++)
						{
			#pragma HLS unroll
							weight[0][i][j].range(7,4)=stream_temp.range( (i*8+j)*8+3,(i*8+j)*8);
							weight[1][i][j].range(7,4)=stream_temp.range( (i*8+j)*8+7,(i*8+j)*8+4);
						}

					}
					stream_temp=stream512_in.read();

					for(int i=0;i<8;i++)
					{

			#pragma HLS unroll
						for(int j=0;j<8;j++)
						{
			#pragma HLS unroll
							weight[0][i][j].range(11,8)=stream_temp.range( (i*8+j)*8+3,(i*8+j)*8);
							weight[1][i][j].range(11,8)=stream_temp.range( (i*8+j)*8+7,(i*8+j)*8+4);
						}

					}





				for(int nn=0;nn<8;nn++)
				{
					/*for(int cc=0;cc<8;cc++){
						top[n+nn]+=weight[0][nn][cc]*bottom[c+cc];
					}*/
				#pragma HLS unroll
					top[n+nn]+=compute_engine_LSTM_loop(
							weight[0][nn][0],    bottom[c+0],
							weight[0][nn][1],    bottom[c+1],
							weight[0][nn][2],    bottom[c+2],
							weight[0][nn][3],    bottom[c+3],
							weight[0][nn][4],    bottom[c+4],
							weight[0][nn][5],    bottom[c+5],
							weight[0][nn][6],    bottom[c+6],
							weight[0][nn][7],    bottom[c+7]);
				}


				for(int nn=0;nn<8;nn++)
				{
					/*for(int cc=0;cc<8;cc++){
						top[n+8+nn]+=weight[1][nn][cc]*bottom[c+cc];
					}*/
				#pragma HLS unroll
					top[n+8+nn]+=compute_engine_LSTM_loop(
							weight[1][nn][0],    bottom[c+0],
							weight[1][nn][1],    bottom[c+1],
							weight[1][nn][2],    bottom[c+2],
							weight[1][nn][3],    bottom[c+3],
							weight[1][nn][4],    bottom[c+4],
							weight[1][nn][5],    bottom[c+5],
							weight[1][nn][6],    bottom[c+6],
							weight[1][nn][7],    bottom[c+7]);
				}
			}
			}


		for(int c=0;c<256;c+=8)
			{
			stream_temp=stream512_in.read();
				for(int j=0;j<8;j++)
				{
				#pragma HLS unroll
					weight[0][0][j].range(11,0)=stream_temp.range(j*12+11,j*12);
				}

				/*for(int cc=0;cc<8;cc++){
					top[8800]+=weight[0][0][cc]*bottom[c+cc];
				}*/
				top[8800]+=compute_engine_LSTM( weight[0][0][0],    bottom[c+0],
												weight[0][0][1],    bottom[c+1],
												weight[0][0][2],    bottom[c+2],
												weight[0][0][3],    bottom[c+3],
												weight[0][0][4],    bottom[c+4],
												weight[0][0][5],    bottom[c+5],
												weight[0][0][6],    bottom[c+6],
												weight[0][0][7],    bottom[c+7]);
			}



}



void Update_layer( int cont_input,  ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> hc_rst[256]){

	for(int i = 0; i < 256; i++){
		hc_rst[i] = cont_input* hc_rst[i];
	}
}




void Add_Result_layer(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> gate_input_t[1024], ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> xcstatic_rst[1024], ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> Wxc_tm1[1024], ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> Whc_tm1[1024],ap_int<512> *  data )
{


  //float bias_buf[4000];
	for(int i = 0; i < 1024; i+=32){
		for(int j=0;j<32;j++)
		{
			ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> temp;
			temp.range(11,0)=(*data).range(j*12+11,j*12);
			gate_input_t[i+j] = xcstatic_rst[i+j]+Wxc_tm1[i+j]+Whc_tm1[i+j]+temp;
		}
		data++;
	}
  ///////////////////////
  /*FILE *buf_file;
    buf_file = fopen("tx_xc_b.txt","w+");
    for (int iii=0; iii<4000; iii++){
      fprintf(buf_file, "%f\n", (float)bias_buf[iii]);
    }
  fclose(buf_file);*/
  /////////////////////////
}



int arg_max(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>  probs[8801]){
	int rst  = -1;
	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> max = -31;

	for(int i = 0; i < 8801; i++){
		if(max < probs[i]){
			max  = probs[i];
			rst = i;
		}
	}
	return rst;
}


ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> sigmoid_hls(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> x)
{

	return 1./(1.+ exp(-1* (float)(x)));
	/*if(x> (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) 0.5)
	return (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) 1;
else if (x< (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) -0.5)
		return 0;
else
	return (x+1)/2;*/
/////////////////////
/*if(x> (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) 2)
	return (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) 1;
else if (x< (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) -2)
		return 0;
else
	return (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)0.19*x+(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)0.5;
*/
	if(x> (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) 4)
		return (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) 1;
	else if(x> (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) 2 && x<= (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) 4)
		return (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) 0.05*x + (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)0.78;
	else if(x< (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) -2 && x>= (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) -4)
		return (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) 0.051*x + (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)0.22;
	else if(x< (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) -4)
			return (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) 0;
	else
		return (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)0.19*x+(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)0.5;


}


ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> tanh_hls(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> x)
{
	return (exp(2* (float)(x))-1)/(exp(2* (float)(x))+1);
/*if(x> (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) 1)
	return (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) 1;
else if (x< (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) -1)
		return -1;
else
	return x;*/
	if(x> (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) 4)
		return (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>) 1;
	else if (x<= (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)4 && x> (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)2)
		return (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)0.018*x+(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)0.928;
	else if (x<= (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)2 && x> (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)1)
		return (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)0.202*x+(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)0.559;
	else if (x<= (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)1 && x> (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)-1)
		return (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)0.762*x;
	else if (x<= (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)-1 && x> (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)-2)
		return (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)0.202*x+(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)-0.559;
	else if (x<= (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)-2 && x> (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)-4)
		return (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)0.018*x+(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)-0.928;
	else
		return (ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>)-1;


}


void LSTM_layer(int cont_input, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> gate_input_t[1024],ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> c_tm1[256],ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> hc_tm1[256]){
//#pragma HLS ARRAY_PARTITION variable=gate_input_t cyclic factor=400 dim=1




	ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> it, ft, ot, gt;
	for(int i = 0; i < 256; i++){
#pragma HLS pipeline
		it = sigmoid_hls(gate_input_t[i]);
		ft = sigmoid_hls(gate_input_t[i+256]);
		ot = sigmoid_hls(gate_input_t[i+512]);
		gt = tanh_hls(gate_input_t[i+768]);
		c_tm1[i] = cont_input * (ft*c_tm1[i]) + it*gt;
		hc_tm1[i]  =ot*tanh_hls(c_tm1[i]);
	}
}






