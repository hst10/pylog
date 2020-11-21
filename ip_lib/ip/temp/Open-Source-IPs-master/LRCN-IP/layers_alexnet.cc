#include "LRCN.h"
#define TOTAL_B 16

ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> compute_engine_1(ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight1,
													ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>  bot1,
													ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight2,
													ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>  bot2,
													ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight3,
													ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>  bot3)
{
#pragma HLS pipeline
	ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> temp1,temp2,temp3;
	temp1=weight1*bot1;
	temp2=weight2*bot2;
	temp3=weight3*bot3;
	return temp1+temp2+temp3;
}


ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> max_engine_1(ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> a0,
												ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> a1,
												ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> a2,
												ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> a3,
												ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> a4,
												ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> a5,
												ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> a6,
												ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> a7,
												ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> a8)
{
#pragma HLS pipeline
	ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> tmp1,tmp2,tmp3,tmp4,tmp5;
	ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> tmp11,tmp12;
	ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> tmp21;

	tmp1=(a0>a1)?a0:a1;
	tmp2=(a2>a3)?a2:a3;
	tmp3=(a4>a5)?a4:a5;
	tmp4=(a6>a7)?a6:a7;
	tmp5=(a8 > ((ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>) 0))?a8: ((ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>) 0);

	tmp11=(tmp1>tmp2)?tmp1:tmp2;
	tmp12=(tmp3>tmp4)?tmp3:tmp4;

	tmp21=(tmp11>tmp12)?tmp11:tmp12;
	return (tmp5>tmp21)?tmp5:tmp21;
}

void load_weights(ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight_buf[96][3], hls::stream<int512> &stream512_in)
{
#pragma HLS pipeline
#pragma HLS ARRAY_PARTITION variable=weight_buf dim=1
#pragma HLS ARRAY_PARTITION variable=weight_buf dim=2

	//need 9 cycles
	for (int j=0; j<3; j++){
		for(int i=0;i<96;i+=32){
			ap_int<512> stream_temp=stream512_in.read();
			for(int ii=0;ii<32;ii++){
#pragma HLS unroll
				weight_buf[i+ii][j].range(11,0)=stream_temp.range(ii*12+11,ii*12);
			}
		}
	}
}

void convolution1_layer(ap_fixed <TOTAL_B,16,AP_TRN_ZERO,AP_SAT> bottom[3][227][227],
						hls::stream<int512> &stream512_in,
                        ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> padded_rst[2][48][31][31])
{
//#pragma HLS INTERFACE m_axi port=data depth=256
	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight_buf[96][3];
	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> bias_buf[96];
	ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT> top[96][55][55];

#pragma HLS ARRAY_PARTITION variable=bias_buf
#pragma HLS ARRAY_PARTITION variable=top dim=1
#pragma HLS ARRAY_PARTITION variable=weight_buf dim=1
#pragma HLS ARRAY_PARTITION variable=weight_buf dim=2
	ap_int<512> stream_temp;

	for(int h=0;h<31;h++){
		for(int w=0;w<31;w++){
#pragma HLS pipeline
			for(int c=0;c<48;c++){
#pragma HLS unroll
				padded_rst[0][c][h][w]=0;
				padded_rst[1][c][h][w]=0;
			}
		}
	}

	//load bias
	for (int i=0;i<3;i++){
		stream_temp=stream512_in.read();
		for(int j=0;j<32;j++){
			bias_buf[i*32+j].range(11,0) = stream_temp.range(j*12+11,j*12);
		}

	}

	for(int h=0;h<55;h++)
		for(int w=0;w<55;w++){
#pragma HLS pipeline
			for(int co=0;co<96;co++){
#pragma HLS unroll
				top[co][h][w]=bias_buf[co];
			}
		}

	for(int i=0; i<11; i++){
		for(int j=0; j<11; j++){
#pragma HLS dataflow
			load_weights(weight_buf,stream512_in);

			//Reading from AXI needs 9 cycles
			for(int h=0;h<55;h++){
				for(int w=0;w<55;w++){
#pragma HLS pipeline
					for(int cii=0;cii<3;cii++){
						for(int coo=0;coo<96;coo+=3){
#pragma HLS unroll
							top[coo+0][h][w] += weight_buf[coo+0][cii]*bottom[cii][h*4+i][w*4+j];
							top[coo+1][h][w] += weight_buf[coo+1][cii]*bottom[cii][h*4+i][w*4+j];
							top[coo+2][h][w] += weight_buf[coo+2][cii]*bottom[cii][h*4+i][w*4+j];
						}
					}
				}
			}
		}
	}

	/*FILE *conv1_file;
	conv1_file = fopen("Q8_conv1_top.txt","w+");
	for(int i=0;i<96;i++){
		for(int j=0; j<55;j++){
		for(int k=0; k<55;k++){
		  fprintf(conv1_file, "%f\n", (float)top[i][j][k]);
		}
		}
	}
	fclose(conv1_file);*/


	for(int ii=0;ii<48;ii+=16)
		for(int h=0;h<27;h++)
			for(int w=0;w<27;w++)
#pragma HLS pipeline
				for(int i=0;i<16;i++){
#pragma HLS unroll
					padded_rst[0][ii+i][h+2][w+2]=max_engine_1(top[ii+i][h*2][w*2],  top[ii+i][h*2][w*2+1],  top[ii+i][h*2][w*2+2],
															   top[ii+i][h*2+1][w*2],top[ii+i][h*2+1][w*2+1],top[ii+i][h*2+1][w*2+2],
															   top[ii+i][h*2+2][w*2],top[ii+i][h*2+2][w*2+1],top[ii+i][h*2+2][w*2+2]);
					padded_rst[1][ii+i][h+2][w+2]=max_engine_1(top[ii+i+48][h*2][w*2],  top[ii+i+48][h*2][w*2+1],  top[ii+i+48][h*2][w*2+2],
															   top[ii+i+48][h*2+1][w*2],top[ii+i+48][h*2+1][w*2+1],top[ii+i+48][h*2+1][w*2+2],
															   top[ii+i+48][h*2+2][w*2],top[ii+i+48][h*2+2][w*2+1],top[ii+i+48][h*2+2][w*2+2]);
				}

}




ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> compute_engine_2(
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight0,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot0,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight1,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot1,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight2,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot2,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight3,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot3,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight4,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot4,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight5,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot5,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight6,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot6,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight7,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot7,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight8,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot8,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight9,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot9,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight10,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot10,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight11,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot11,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight12,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot12,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight13,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot13,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight14,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot14,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight15,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot15,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight16,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot16,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight17,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot17,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight18,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot18,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight19,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot19,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight20,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot20,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight21,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot21,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight22,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot22,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight23,ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>   bot23
							)
{
#pragma HLS pipeline
	ap_fixed <TOTAL_B,12> mul0,mul1,mul2,mul3,mul4,mul5,mul6,mul7;
	ap_fixed <TOTAL_B,12> mul8,mul9,mul10,mul11,mul12,mul13,mul14,mul15;
	ap_fixed <TOTAL_B,12> mul16,mul17,mul18,mul19,mul20,mul21,mul22,mul23;

	ap_fixed <TOTAL_B,13> add00,add01,add02,add03,add04,add05,add06,add07,add08,add09,add010,add011;
	ap_fixed <TOTAL_B,13> add10,add11,add12,add13,add14,add15;
	ap_fixed <TOTAL_B,13> add20,add21,add22;
	mul0=weight0*bot0;
	mul1=weight1*bot1;
	mul2=weight2*bot2;
	mul3=weight3*bot3;
	mul4=weight4*bot4;
	mul5=weight5*bot5;
	mul6=weight6*bot6;
	mul7=weight7*bot7;
	mul8=weight8*bot8;
	mul9=weight9*bot9;
	mul10=weight10*bot10;
	mul11=weight11*bot11;
	mul12=weight12*bot12;
	mul13=weight13*bot13;
	mul14=weight14*bot14;
	mul15=weight15*bot15;
	mul16=weight16*bot16;
	mul17=weight17*bot17;
	mul18=weight18*bot18;
	mul19=weight19*bot19;
	mul20=weight20*bot20;
	mul21=weight21*bot21;
	mul22=weight22*bot22;
	mul23=weight23*bot23;
	
	add00=mul0+mul1;
	add01=mul2+mul3;
	add02=mul4+mul5;
	add03=mul6+mul7;
	add04=mul8+mul9;
	add05=mul10+mul11;
	add06=mul12+mul13;
	add07=mul14+mul15;
	add08=mul16+mul17;
	add09=mul18+mul19;
	add010=mul20+mul21;
	add011=mul22+mul23;
	
	add10=add00+add01;
	add11=add02+add03;
	add12=add04+add05;
	add13=add06+add07;
	add14=add08+add09;
	add15=add010+add011;
	
	add20=add10+add11;
	add21=add12+add13;
	add22=add14+add15;
	return add20+add21+add22;
}

void load_weights_2(ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight_buf[2][16][24],
		hls::stream<int512> &stream512_in)
{
ap_int<512> stream_temp;
#pragma HLS ARRAY_PARTITION variable=weight_buf   dim=1
#pragma HLS ARRAY_PARTITION variable=weight_buf   dim=2
#pragma HLS ARRAY_PARTITION variable=weight_buf   dim=3
	for(int cii=0;cii<24;cii++){ //solution2: 16->24
		stream_temp=stream512_in.read();
		for(int ct=0;ct<2;ct++){
#pragma HLS unroll
			for(int coo=0;coo<16;coo+=2){ //need to be 16
#pragma HLS unroll
				weight_buf[ct][coo][cii].range(11,0)=stream_temp.range((coo+ct*16)*12+11,(coo+ct*16)*12);
				weight_buf[ct][coo+1][cii].range(11,0)=stream_temp.range((coo+(ct*16)+1)*12+11,(coo+(ct*16)+1)*12);
			}
		}

	}
}

ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> max_engine_2(ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> a0,
												ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> a1,
												ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> a2,
												ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> a3,
												ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> a4,
												ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> a5,
												ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> a6,
												ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> a7,
												ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> a8)
{
#pragma HLS pipeline
	ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> tmp1,tmp2,tmp3,tmp4,tmp5;
	ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> tmp11,tmp12;
	ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> tmp21;

	tmp1=(a0>a1)?a0:a1;
	tmp2=(a2>a3)?a2:a3;
	tmp3=(a4>a5)?a4:a5;
	tmp4=(a6>a7)?a6:a7;
	tmp5=(a8 > ((ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>) 0))?a8: ((ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>) 0);

	tmp11=(tmp1>tmp2)?tmp1:tmp2;
	tmp12=(tmp3>tmp4)?tmp3:tmp4;

	tmp21=(tmp11>tmp12)?tmp11:tmp12;
	return (tmp5>tmp21)?tmp5:tmp21;

}

void convolution2_layer(ap_fixed <TOTAL_B,12,AP_TRN_ZERO,AP_SAT>  bottom[2][48][31][31], hls::stream<int512> &stream512_in, ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> padded_rst[256][15][15])
{
	ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT> top[2][128][27][27];
	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight_buf[2][16][24];//weight_buf=[2][16][16] -> weight_buf=[2][16][16]
	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> bias_buff[2][16];//bias_buff=[2][16] -> bias_buff=[2][16]

#pragma HLS ARRAY_PARTITION variable=top dim=1
#pragma HLS ARRAY_PARTITION variable=top cyclic dim=2 factor=16 //need to be 16
#pragma HLS ARRAY_PARTITION variable=weight_buf  dim=1
#pragma HLS ARRAY_PARTITION variable=weight_buf   dim=2
#pragma HLS ARRAY_PARTITION variable=weight_buf   dim=3

ap_int<512> stream_temp;
	for(int co=0;co<128;co+=16){ //need to be 16
		stream_temp=stream512_in.read();
		for(int coo=0;coo<16;coo++){
#pragma HLS unroll
			bias_buff[0][coo].range(11,0)=stream_temp.range(coo*24+11,coo*24);
			bias_buff[1][coo].range(11,0)=stream_temp.range(coo*24+23,coo*24+12);
		}


		for(int h=0;h<27;h++){
			for(int w=0;w<27;w++)
			{
#pragma HLS pipeline
				for(int coo=0;coo<16;coo++)//need to be 16
				{
#pragma HLS unroll
					top[0][co+coo][h][w]=bias_buff[0][coo];
					top[1][co+coo][h][w]=bias_buff[1][coo];
				}
			}
		}
	}
	//checked top with bias
/*	FILE *conv2b_file;
	conv2b_file = fopen("conv2_b.txt","w+");
	for(int ct=0;ct<2;ct++){
	for(int i=0;i<128;i++){
		for(int j=0; j<27;j++){
		for(int k=0; k<27;k++){
		  fprintf(conv2b_file, "%f\n", (float)top[ct][i][j][k]);
		}
		}
	}
	}
	fclose(conv2b_file);*/

	for(int h=0;h<15;h++)
		for(int w=0;w<15;w++)
		{
			for(int co=0;co<256;co+=16){//need to be 16
#pragma HLS pipeline
				for(int coo=0;coo<16;coo++)//need to be 16
				{
#pragma HLS unroll
					padded_rst[co+coo][h][w]=0;
				}
			}
		}

	for(int ci=0;ci<48;ci+=24) //solution2: 16->24
		for(int co=0;co<128;co+=16)  //need to be 16
			for(int i=0; i<5; i++){
				for(int j=0; j<5; j++){
#pragma HLS dataflow
					load_weights_2(weight_buf,stream512_in);

					for(int h=0;h<27;h++){
						for(int w=0;w<27;w++){
#pragma HLS pipeline
							for(int coo=0;coo<16;coo++){//need to be 16
#pragma HLS unroll
                                for(int ct=0;ct<2;ct++){

                                	/*for(int cii=0;cii<16;cii++){
#pragma HLS unroll
                                		top[ct][co+coo][h][w]+=weight_buf[ct][coo][cii]*bottom[ct][ci+cii][h+i][w+j];
                                	} //Same as fix-point reference*/
#pragma HLS unroll
                                	top[ct][co+coo][h][w]+=compute_engine_2(
											weight_buf[ct][coo][0] , bottom[ct][ci+0][h+i][w+j],
											weight_buf[ct][coo][1] , bottom[ct][ci+1][h+i][w+j],
                                            weight_buf[ct][coo][2] , bottom[ct][ci+2][h+i][w+j],
                                            weight_buf[ct][coo][3] , bottom[ct][ci+3][h+i][w+j],
                                            weight_buf[ct][coo][4] , bottom[ct][ci+4][h+i][w+j],
                                            weight_buf[ct][coo][5] , bottom[ct][ci+5][h+i][w+j],
                                            weight_buf[ct][coo][6] , bottom[ct][ci+6][h+i][w+j],
                                            weight_buf[ct][coo][7] , bottom[ct][ci+7][h+i][w+j],
                                            weight_buf[ct][coo][8] , bottom[ct][ci+8][h+i][w+j],
                                            weight_buf[ct][coo][9] , bottom[ct][ci+9][h+i][w+j],
                                            weight_buf[ct][coo][10] , bottom[ct][ci+10][h+i][w+j],
                                            weight_buf[ct][coo][11] , bottom[ct][ci+11][h+i][w+j],
                                            weight_buf[ct][coo][12] , bottom[ct][ci+12][h+i][w+j],
                                            weight_buf[ct][coo][13] , bottom[ct][ci+13][h+i][w+j],
                                            weight_buf[ct][coo][14] , bottom[ct][ci+14][h+i][w+j],
                                            weight_buf[ct][coo][15] , bottom[ct][ci+15][h+i][w+j],
                                            weight_buf[ct][coo][16] , bottom[ct][ci+16][h+i][w+j],
                                            weight_buf[ct][coo][17] , bottom[ct][ci+17][h+i][w+j],
                                            weight_buf[ct][coo][18] , bottom[ct][ci+18][h+i][w+j],
                                            weight_buf[ct][coo][19] , bottom[ct][ci+19][h+i][w+j],
                                            weight_buf[ct][coo][20] , bottom[ct][ci+20][h+i][w+j],
                                            weight_buf[ct][coo][21] , bottom[ct][ci+21][h+i][w+j],
                                            weight_buf[ct][coo][22] , bottom[ct][ci+22][h+i][w+j],
                                            weight_buf[ct][coo][23] , bottom[ct][ci+23][h+i][w+j]);

                               }
							}
						}
					}
				}
            }
	/*FILE *conv2_file;
		conv2_file = fopen("Q8_conv2_top.txt","w+");
		for(int ct=0;ct<2;ct++){
		for(int i=0;i<128;i++){
			for(int j=0; j<27;j++){
			for(int k=0; k<27;k++){
			  fprintf(conv2_file, "%f\n", (float)top[ct][i][j][k]);
			}
			}
		}
		}
	fclose(conv2_file);*/




		for(int ii=0;ii<128;ii+=16)//need to be 16 //coo
		for(int h=0;h<13;h++)
			for(int w=0;w<13;w++){
#pragma HLS pipeline
				for(int i=0;i<16;i++) //need to be 16
				{
#pragma HLS unroll
					padded_rst[ii+i][h+1][w+1]=max_engine_2(top[0][ii+i][h*2][w*2],  top[0][ii+i][h*2][w*2+1],  top[0][ii+i][h*2][w*2+2],
															top[0][ii+i][h*2+1][w*2],top[0][ii+i][h*2+1][w*2+1],top[0][ii+i][h*2+1][w*2+2],
															top[0][ii+i][h*2+2][w*2],top[0][ii+i][h*2+2][w*2+1],top[0][ii+i][h*2+2][w*2+2]);

					padded_rst[128+ii+i][h+1][w+1]=max_engine_2(top[1][ii+i][h*2][w*2],  top[1][ii+i][h*2][w*2+1],  top[1][ii+i][h*2][w*2+2],
															    top[1][ii+i][h*2+1][w*2],top[1][ii+i][h*2+1][w*2+1],top[1][ii+i][h*2+1][w*2+2],
															    top[1][ii+i][h*2+2][w*2],top[1][ii+i][h*2+2][w*2+1],top[1][ii+i][h*2+2][w*2+2]);
				}
			}
	/*	FILE *conv2_file;
			conv2_file = fopen("LRCN_test_conv2_pooling_rst.txt","w+");
			for(int i=0;i<256;i++){
				for(int j=0; j<13;j++){
				for(int k=0; k<13;k++){
				  fprintf(conv2_file, "%f\n", (float)padded_rst[i][j+1][k+1]);
				}
				}
			}
		fclose(conv2_file);*/

 }



void load_weights_3(ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight_buf[2][24][16], //solution2: weight_buf[2][12][16]->weight_buf[2][12][16]
	 				hls::stream<int512> &stream512_in)
{
#pragma HLS ARRAY_PARTITION variable=weight_buf  dim=1
#pragma HLS ARRAY_PARTITION variable=weight_buf  dim=2
#pragma HLS ARRAY_PARTITION variable=weight_buf  dim=3
ap_int<512> stream_temp;
	 for(int coo=0;coo<24;coo++){
		 stream_temp=stream512_in.read();
		for(int ct=0;ct<2;ct++){
#pragma HLS unroll
			for(int cii=0;cii<16;cii+=2){
#pragma HLS unroll
				weight_buf[ct][coo][cii].range(11,0)=stream_temp.range((cii+ct*16)*12+11,(cii+ct*16)*12);
				weight_buf[ct][coo][cii+1].range(11,0)=stream_temp.range((cii+(ct*16)+1)*12+11,(cii+(ct*16)+1)*12);

			}
		}
	}
}

 ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT> compute_engine_3(
		 	 	 	 	 	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight0,ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>   bot0,
 							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight1,ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>   bot1,
 							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight2,ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>   bot2,
 							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight3,ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>   bot3,
 							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight4,ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>   bot4,
 							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight5,ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>   bot5,
 							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight6,ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>   bot6,
 							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight7,ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>   bot7,
 							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight8,ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>   bot8,
 							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight9,ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>   bot9,
 							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight10,ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>   bot10,
 							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight11,ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>   bot11,
 							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight12,ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>   bot12,
 							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight13,ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>   bot13,
 							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight14,ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>   bot14,
 							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight15,ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>   bot15)
 {
 #pragma HLS pipeline
 	ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT> mul0,mul1,mul2,mul3,mul4,mul5,mul6,mul7,mul8,mul9,mul10,mul11,mul12,mul13,mul14,mul15;
 	ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT> add00,add01,add02,add03,add04,add05,add06,add07;
 	ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT> add10,add11,add12,add13;
 	ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT> add20,add21/*,add22,add23*/;
 	mul0=weight0*bot0;
 	mul1=weight1*bot1;
 	mul2=weight2*bot2;
 	mul3=weight3*bot3;
 	mul4=weight4*bot4;
 	mul5=weight5*bot5;
 	mul6=weight6*bot6;
 	mul7=weight7*bot7;
 	mul8=weight8*bot8;
 	mul9=weight9*bot9;
 	mul10=weight10*bot10;
 	mul11=weight11*bot11;
 	mul12=weight12*bot12;
 	mul13=weight13*bot13;
 	mul14=weight14*bot14;
 	mul15=weight15*bot15;
    /*mul16=weight16*bot16;
    mul17=weight17*bot17;
    mul18=weight18*bot18;
    mul19=weight19*bot19;
    mul20=weight20*bot20;
    mul21=weight21*bot21;
    mul22=weight22*bot22;
    mul23=weight23*bot23;
    mul24=weight24*bot24;
    mul25=weight25*bot25;
    mul26=weight26*bot26;
    mul27=weight27*bot27;
    mul28=weight28*bot28;
    mul29=weight29*bot29;
    mul30=weight10*bot30;
    mul31=weight11*bot31;*/
 	add00=mul0+mul1;
 	add01=mul2+mul3;
 	add02=mul4+mul5;
 	add03=mul6+mul7;
 	add04=mul8+mul9;
 	add05=mul10+mul11;
 	add06=mul12+mul13;
 	add07=mul14+mul15;
    /*add08=mul16+mul17;
    add09=mul18+mul19;
    add010=mul20+mul21;
    add011=mul22+mul23;
    add012=mul24+mul25;
    add013=mul26+mul27;
    add014=mul28+mul29;
    add015=mul30+mul31;*/
 	add10=add00+add01;
 	add11=add02+add03;
 	add12=add04+add05;
 	add13=add06+add07;
    /*add14=add08+add09;
    add15=add010+add011;
    add16=add012+add013;
    add17=add014+add015;*/
 	add20=add10+add11;
 	add21=add12+add13;
    /*add22=add14+add15;
    add23=add16+add17;
    add30=add20+add21;
    add31=add22+add23;*/
 	return add20+add21;
 }


void convolution3_layer(ap_fixed <TOTAL_B,9,AP_TRN_ZERO,AP_SAT>  bottom[256][15][15], hls::stream<int512> &stream512_in, ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT> top[2][192][15][15])
{
//#pragma HLS INTERFACE m_axi port=data depth=256
	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight_buf[2][24][16];//solution2: weight_buf[2][12][16]->weight_buf[2][12][16]
	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  bias_buf[2][16];

#pragma HLS ARRAY_PARTITION variable=weight_buf dim=1
#pragma HLS ARRAY_PARTITION variable=weight_buf dim=2
#pragma HLS ARRAY_PARTITION variable=weight_buf dim=3
#pragma HLS ARRAY_PARTITION variable=bias_buf dim=1
#pragma HLS ARRAY_PARTITION variable=bias_buf dim=2
	ap_int<512> stream_temp;
//#pragma HLS ARRAY_PARTITION variable=bottom_padded cyclic dim=1 factor=4
    for(int co=0;co<192;co+=16) //need to be 24: 12->12
    {
    	 stream_temp=stream512_in.read();
        for(int coo=0;coo<16;coo++) //need to be 12: 12->12
        {
#pragma HLS unroll
			bias_buf[0][coo].range(11,0)=stream_temp.range(coo*24+11,coo*24); //=bias[0][co+coo];
			bias_buf[1][coo].range(11,0)=stream_temp.range(coo*24+23,coo*24+12); //=bias[1][co+coo];
        }


		for(int h=0;h<13;h++)
			for(int w=0;w<13;w++)
            {
                #pragma HLS pipeline
                for(int coo=0;coo<16;coo++) //need to 12 16: 12->12
                {
#pragma HLS unroll
					top[0][co+coo][1+h][1+w]=bias_buf[0][coo];
					top[1][co+coo][1+h][1+w]=bias_buf[1][coo];
                }
            }
    }

    for(int co=0;co<192;co+=24) //need to be 12: 12->12
    {
		for(int w=0;w<15;w++)
        {
#pragma HLS pipeline
			for(int coo=0;coo<24;coo++) //need to be 12: 12->12
			{
#pragma HLS unroll
				top[0][co+coo][0][w]=0;
				top[0][co+coo][14][w]=0;
				top[1][co+coo][0][w]=0;
				top[1][co+coo][14][w]=0;
			}
		}
    }

    for(int co=0;co<192;co+=24) //need to be 12: 12->12
    {
		for(int h=1;h<14;h++)
		{
#pragma HLS pipeline
			for(int coo=0;coo<24;coo++) //need to be 12: 12->12
			{
#pragma HLS unroll
				top[0][co+coo][h][0]=0;
				top[0][co+coo][h][14]=0;
				top[1][co+coo][h][0]=0;
				top[1][co+coo][h][14]=0;
			}
		}
    }

    for (int ci = 0; ci < 256; ci+=16){ //solution2:16->16
    	for(int i=0; i<3; i++){
    		for(int j=0; j<3; j++){
    			for(int co=0;co<192;co+=24){  //need to be 192/12
#pragma HLS dataflow
                    load_weights_3(weight_buf, stream512_in);//need to be 16: 12->12

                    for(int h=0;h<13;h++){
                        for(int w=0;w<13;w++){
#pragma HLS pipeline
                            for (int coo = 0; coo < 24; coo++){ //need to be 16: 12->12
#pragma HLS unroll
                                for(int ct=0;ct<2;ct++){
                                	/*for(int cii=0;cii<16;cii++){
								#pragma HLS unroll
										top[ct][co+coo][1+h][1+w]+=weight_buf[ct][coo][cii]*bottom[ci+cii][h+i][w+j];
										}*/

#pragma HLS unroll
									top[ct][co+coo][1+h][1+w]+=compute_engine_3(
											weight_buf[ct][coo][0] , bottom[ci+0][h+i][w+j],
											weight_buf[ct][coo][1] , bottom[ci+1][h+i][w+j],
											weight_buf[ct][coo][2] , bottom[ci+2][h+i][w+j],
											weight_buf[ct][coo][3] , bottom[ci+3][h+i][w+j],
											weight_buf[ct][coo][4] , bottom[ci+4][h+i][w+j],
											weight_buf[ct][coo][5] , bottom[ci+5][h+i][w+j],
											weight_buf[ct][coo][6] , bottom[ci+6][h+i][w+j],
											weight_buf[ct][coo][7] , bottom[ci+7][h+i][w+j],
											weight_buf[ct][coo][8] , bottom[ci+8][h+i][w+j],
											weight_buf[ct][coo][9] , bottom[ci+9][h+i][w+j],
											weight_buf[ct][coo][10] , bottom[ci+10][h+i][w+j],
											weight_buf[ct][coo][11] , bottom[ci+11][h+i][w+j],
											weight_buf[ct][coo][12] , bottom[ci+12][h+i][w+j],
											weight_buf[ct][coo][13] , bottom[ci+13][h+i][w+j],
											weight_buf[ct][coo][14] , bottom[ci+14][h+i][w+j],
											weight_buf[ct][coo][15] , bottom[ci+15][h+i][w+j]);

                                }
                            }
                        }
                    }
                }
            }
        }
    }
  /*  FILE *conv3_file;
    	conv3_file = fopen("Q8_conv3_top.txt","w+");
    	for(int ct=0;ct<2;ct++){
    	for(int i=0; i<192;i++)
    	{
    		for(int j=0; j<13;j++)
    		{
    		for(int k=0; k<13;k++)
    		{
    		  fprintf(conv3_file, "%f\n", (float)top[ct][i][1+j][1+k]);
    		}
    		}
    	}
    	}
    	fclose(conv3_file);*/

    for(int co=0;co<192;co+=24)//need to be 12: 12->12
    {
		for(int h=0;h<13;h++)
			for(int w=0;w<13;w++)
            {
#pragma HLS pipeline
                for(int coo=0;coo<24;coo++)//need to be 12: 12->12
                {
#pragma HLS unroll
                	if(top[0][co+coo][1+h][1+w]<0)
                		top[0][co+coo][1+h][1+w]=0;
                	if(top[1][co+coo][1+h][1+w]<0)
						top[1][co+coo][1+h][1+w]=0;
                }
            }
    }


}


ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT> compute_engine_4(
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>   weight0,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot0,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>   weight1,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot1,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight2,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot2,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight3,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot3,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight4,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot4,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight5,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot5,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight6,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot6,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight7,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot7,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight8,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot8,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight9,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot9,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight10,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot10,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight11,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot11,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight12,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot12,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight13,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot13,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight14,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot14,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight15,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot15,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight16,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot16,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight17,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot17,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight18,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot18,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight19,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot19,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight20,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot20,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight21,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot21,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight22,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot22,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT>  weight23,ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT>   bot23
							)
{
#pragma HLS pipeline
	ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT> mul0,mul1,mul2,mul3,mul4,mul5,mul6,mul7,mul8,mul9,mul10,mul11;
	ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT> mul12,mul13,mul14,mul15,mul16,mul17,mul18,mul19,mul20,mul21,mul22,mul23;
	ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT> add00,add01,add02,add03,add04,add05;
	ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT> add06,add07,add08,add09,add010,add011;
	ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT> add10,add11,add12;
	ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT> add13,add14,add15;
	ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT> add20,add21,add22;

	mul0=weight0*bot0;
	mul1=weight1*bot1;
	mul2=weight2*bot2;
	mul3=weight3*bot3;
	mul4=weight4*bot4;
	mul5=weight5*bot5;
	mul6=weight6*bot6;
	mul7=weight7*bot7;
	mul8=weight8*bot8;
	mul9=weight9*bot9;
	mul10=weight10*bot10;
	mul11=weight11*bot11;
	mul12=weight12*bot12;
	mul13=weight13*bot13;
	mul14=weight14*bot14;
	mul15=weight15*bot15;
	mul16=weight16*bot16;
	mul17=weight17*bot17;
	mul18=weight18*bot18;
	mul19=weight19*bot19;
	mul20=weight20*bot20;
	mul21=weight21*bot21;
	mul22=weight22*bot22;
	mul23=weight23*bot23;
	
	add00=mul0+mul1;
	add01=mul2+mul3;
	add02=mul4+mul5;
	add03=mul6+mul7;
	add04=mul8+mul9;
	add05=mul10+mul11;
	add06=mul12+mul13;
	add07=mul14+mul15;
	add08=mul16+mul17;
	add09=mul18+mul19;
	add010=mul20+mul21;
	add011=mul22+mul23;
	
	add10=add00+add01;
	add11=add02+add03;
	add12=add04+add05;
	add13=add06+add07;
	add14=add08+add09;
	add15=add010+add011;

	add20=add10+add11;
	add21=add12+add13;
	add22=add14+add15;

	return add20+add21+add22;
}



void load_weights_4(ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight_buf[2][16][24],//solution3: weight_buf[2][16][12]->weight_buf[2][16][12]
					hls::stream<int512> &stream512_in)
{
ap_int<512> stream_temp;

#pragma HLS ARRAY_PARTITION variable=weight_buf  dim=1
#pragma HLS ARRAY_PARTITION variable=weight_buf  dim=2
#pragma HLS ARRAY_PARTITION variable=weight_buf  dim=3
	for(int cii=0;cii<24;cii++){
		stream_temp=stream512_in.read();
		for(int ct=0;ct<2;ct++){
#pragma HLS unroll
			for(int coo=0;coo<16;coo+=2){//need to be 16: 16->16		
#pragma HLS unroll
				weight_buf[ct][coo][cii].range(11,0)=stream_temp.range((coo+ct*16)*12+11,(coo+ct*16)*12);
				weight_buf[ct][coo+1][cii].range(11,0)=stream_temp.range((coo+(ct*16)+1)*12+11,(coo+(ct*16)+1)*12);
			}
		}

	}
}

void convolution4_layer(ap_fixed <TOTAL_B,8,AP_TRN_ZERO,AP_SAT> bottom[2][192][15][15],hls::stream<int512> &stream512_in, ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT> top[2][192][15][15])
{
//#pragma HLS INTERFACE m_axi port=data depth=256
	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight_buf[2][16][24];//solution3: weight_buf[2][16][12]->weight_buf[2][16][12]
	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> bias_buf[2][16];//solution2: bias_buf[2][16]->bias_buf[2][16]
	ap_int<512> stream_temp;
#pragma HLS ARRAY_PARTITION variable=weight_buf dim=1
#pragma HLS ARRAY_PARTITION variable=weight_buf dim=2
#pragma HLS ARRAY_PARTITION variable=weight_buf dim=3
#pragma HLS ARRAY_PARTITION variable=bias_buf dim=1
#pragma HLS ARRAY_PARTITION variable=bias_buf dim=2
//#pragma HLS ARRAY_PARTITION variable=bottom_padded cyclic dim=1 factor=4
    for(int co=0;co<192;co+=16) //need to be 16: 16->16
    {
    	stream_temp=stream512_in.read();
        for(int coo=0;coo<16;coo++)//need to be 16: 16->16
        {
            #pragma HLS unroll
            bias_buf[0][coo].range(11,0)=stream_temp.range(coo*24+11,coo*24);
            bias_buf[1][coo].range(11,0)=stream_temp.range(coo*24+23,coo*24+12);
        }

		for(int h=0;h<13;h++)
			for(int w=0;w<13;w++)
            {
                #pragma HLS pipeline
                for(int coo=0;coo<16;coo++)//need to be 16: 16->16
                {
                    #pragma HLS unroll
                            top[0][co+coo][1+h][1+w]=bias_buf[0][coo];
                            top[1][co+coo][1+h][1+w]=bias_buf[1][coo];
                }
            }
    }

    for(int co=0;co<192;co+=16)//need to be 16: 16->16
    {
		for(int w=0;w<15;w++)
		{
#pragma HLS pipeline
			for(int coo=0;coo<16;coo++)//need to be 16: 16->16
			{
#pragma HLS unroll
				top[0][co+coo][0][w]=0;
				top[0][co+coo][14][w]=0;
				top[1][co+coo][0][w]=0;
				top[1][co+coo][14][w]=0;
			}
		}
    }

    for(int co=0;co<192;co+=16)//need to be 16: 16->16
    {
		for(int h=1;h<14;h++)
        {
 #pragma HLS pipeline
			for(int coo=0;coo<16;coo++)//need to be 16: 16->16
			{
#pragma HLS unroll
				top[0][co+coo][h][0]=0;
				top[0][co+coo][h][14]=0;
				top[1][co+coo][h][0]=0;
				top[1][co+coo][h][14]=0;
			}
		}
    }

    for (int ci = 0; ci < 192; ci+=24){//solution2: 12->12
    	for(int i=0; i<3; i++){
			for(int j=0; j<3; j++){
				for(int co=0;co<192;co+=16){//need to be (192/16): 12->12
#pragma HLS dataflow
				load_weights_4(weight_buf,stream512_in);//need to be 16: 16->16


				for(int h=0;h<13;h++){
					for(int w=0;w<13;w++){
#pragma HLS pipeline
						for (int coo = 0; coo < 16; coo++){//need to be 16: 16->16
#pragma HLS unroll
							for(int ct=0;ct<2;ct++){

								/*for(int cii=0;cii<12;cii++){
								#pragma HLS unroll
									top[ct][co+coo][1+h][1+w]+=weight_buf[ct][coo][cii]*bottom[ct][ci+cii][h+i][w+j];
								}*/

#pragma HLS unroll
								top[ct][co+coo][1+h][1+w]+=compute_engine_4(
										weight_buf[ct][coo][0] , bottom[ct][ci+0][h+i][w+j],
										weight_buf[ct][coo][1] , bottom[ct][ci+1][h+i][w+j],
										weight_buf[ct][coo][2] , bottom[ct][ci+2][h+i][w+j],
										weight_buf[ct][coo][3] , bottom[ct][ci+3][h+i][w+j],
										weight_buf[ct][coo][4] , bottom[ct][ci+4][h+i][w+j],
										weight_buf[ct][coo][5] , bottom[ct][ci+5][h+i][w+j],
										weight_buf[ct][coo][6] , bottom[ct][ci+6][h+i][w+j],
										weight_buf[ct][coo][7] , bottom[ct][ci+7][h+i][w+j],
										weight_buf[ct][coo][8] , bottom[ct][ci+8][h+i][w+j],
										weight_buf[ct][coo][9] , bottom[ct][ci+9][h+i][w+j],
										weight_buf[ct][coo][10] , bottom[ct][ci+10][h+i][w+j],
										weight_buf[ct][coo][11] , bottom[ct][ci+11][h+i][w+j],
										weight_buf[ct][coo][12] , bottom[ct][ci+12][h+i][w+j],
										weight_buf[ct][coo][13] , bottom[ct][ci+13][h+i][w+j],
										weight_buf[ct][coo][14] , bottom[ct][ci+14][h+i][w+j],
										weight_buf[ct][coo][15] , bottom[ct][ci+15][h+i][w+j],
										weight_buf[ct][coo][16] , bottom[ct][ci+16][h+i][w+j],
										weight_buf[ct][coo][17] , bottom[ct][ci+17][h+i][w+j],
										weight_buf[ct][coo][18] , bottom[ct][ci+18][h+i][w+j],
										weight_buf[ct][coo][19] , bottom[ct][ci+19][h+i][w+j],
										weight_buf[ct][coo][20] , bottom[ct][ci+20][h+i][w+j],
										weight_buf[ct][coo][21] , bottom[ct][ci+21][h+i][w+j],
										weight_buf[ct][coo][22] , bottom[ct][ci+22][h+i][w+j],
										weight_buf[ct][coo][23] , bottom[ct][ci+23][h+i][w+j]);

                                }
                            }
                        }
                    }
                }
            }
        }
    }
    /*FILE *conv4_1_file;
	conv4_1_file = fopen("Q8_conv4_top1.txt","w+");
	for(int i=0; i<192;i++)
	{
		for(int j=0; j<13;j++)
		{
		for(int k=0; k<13;k++)
		{
		  fprintf(conv4_1_file, "%f\n", (float)top[0][i][j+1][k+1]);
		}
		}
	}
	fclose(conv4_1_file);*/




    for(int co=0;co<192;co+=16)//need to be 16
    {
		for(int h=0;h<13;h++)
			for(int w=0;w<13;w++)
            {
#pragma HLS pipeline
                for(int coo=0;coo<16;coo++)//need to be 16
                {
#pragma HLS unroll
                	if(top[0][co+coo][1+h][1+w]<0)
                            top[0][co+coo][1+h][1+w]=0;
                	if(top[1][co+coo][1+h][1+w]<0)
                            top[1][co+coo][1+h][1+w]=0;
                }
            }
    }



}
//**CONV4**END**//


//**CONV5**//
void load_weights_5(ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight_buf[2][8][16],//solution2: 16->16
		hls::stream<int512> &stream512_in)
{
ap_int<512> stream_temp;
#pragma HLS ARRAY_PARTITION variable=weight_buf  dim=1
#pragma HLS ARRAY_PARTITION variable=weight_buf  dim=2
#pragma HLS ARRAY_PARTITION variable=weight_buf  dim=3
	for(int coo=0;coo<8;coo++){ //solution2:
		stream_temp=stream512_in.read();
		for(int ct=0;ct<2;ct++){
#pragma HLS unroll
			for(int cii=0;cii<16;cii+=2){
#pragma HLS unroll
				weight_buf[ct][coo][cii].range(11,0)=stream_temp.range((cii+ct*16)*12+11,(cii+ct*16)*12);
				weight_buf[ct][coo][cii+1].range(11,0)=stream_temp.range((cii+(ct*16)+1)*12+11,(cii+(ct*16)+1)*12);

			}
		}
     }
}

ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> compute_engine_5(ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight0,ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT>   bot0,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight1,ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT>   bot1,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight2,ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT>   bot2,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight3,ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT>   bot3,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight4,ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT>   bot4,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight5,ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT>   bot5,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight6,ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT>   bot6,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight7,ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT>   bot7,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight8,ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT>   bot8,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight9,ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT>   bot9,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight10,ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT>   bot10,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight11,ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT>   bot11,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight12,ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT>   bot12,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight13,ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT>   bot13,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight14,ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT>   bot14,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight15,ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT>   bot15)
{
#pragma HLS pipeline
	ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> mul0,mul1,mul2,mul3,mul4,mul5,mul6,mul7,mul8,mul9,mul10,mul11,mul12,mul13,mul14,mul15;
//	ap_fixed <TOTAL_B,11> mul16,mul17,mul18,mul19,mul20,mul21,mul22,mul23;
	ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> add00,add01,add02,add03,add04,add05,add06,add07;
//	ap_fixed <TOTAL_B,11> add08,add09,add010,add011;
	ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> add10,add11,add12,add13;
//	ap_fixed <TOTAL_B,11> add14,add15;
	ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> add20,add21/*,add22*/;
	mul0=weight0*bot0;
	mul1=weight1*bot1;
	mul2=weight2*bot2;
	mul3=weight3*bot3;
	mul4=weight4*bot4;
	mul5=weight5*bot5;
	mul6=weight6*bot6;
	mul7=weight7*bot7;
	mul8=weight8*bot8;
	mul9=weight9*bot9;
	mul10=weight10*bot10;
	mul11=weight11*bot11;
	mul12=weight12*bot12;
	mul13=weight13*bot13;
	mul14=weight14*bot14;
	mul15=weight15*bot15;
/*	mul16=weight16*bot16;
	mul17=weight17*bot17;
	mul18=weight18*bot18;
	mul19=weight19*bot19;
	mul20=weight20*bot20;
	mul21=weight21*bot21;
	mul22=weight22*bot22;
	mul23=weight23*bot23;*/
	add00=mul0+mul1;
	add01=mul2+mul3;
	add02=mul4+mul5;
	add03=mul6+mul7;
	add04=mul8+mul9;
	add05=mul10+mul11;
	add06=mul12+mul13;
	add07=mul14+mul15;
/*	add08=mul16+mul17;
	add09=mul18+mul19;
	add010=mul20+mul21;
	add011=mul22+mul23;*/

	add10=add00+add01;
	add11=add02+add03;
	add12=add04+add05;
	add13=add06+add07;
/*	add14=add08+add09;
	add15=add010+add011;*/

	add20=add10+add11;
	add21=add12+add13;
//	add22=add14+add15;
	return add20+add21/*+add22*/;
}

ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> max_engine_5(ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> a0,
												ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> a1,
												ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> a2,
												ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> a3,
												ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> a4,
												ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> a5,
												ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> a6,
												ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> a7,
												ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> a8)
{
#pragma HLS pipeline
	ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> tmp1,tmp2,tmp3,tmp4,tmp5;
	ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> tmp11,tmp12;
	ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> tmp21;
	tmp1=(a0>a1)?a0:a1;
	tmp2=(a2>a3)?a2:a3;
	tmp3=(a4>a5)?a4:a5;
	tmp4=(a6>a7)?a6:a7;
	tmp5=(a8 > ((ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT>) 0))?a8: ((ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT>) 0);
	tmp11=(tmp1>tmp2)?tmp1:tmp2;
	tmp12=(tmp3>tmp4)?tmp3:tmp4;
	tmp21=(tmp11>tmp12)?tmp11:tmp12;
	return (tmp5>tmp21)?tmp5:tmp21;
}

void convolution5_layer(ap_fixed <TOTAL_B,7,AP_TRN_ZERO,AP_SAT> bottom[2][192][15][15],hls::stream<int512> &stream512_in,ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> finalout[256][6][6])
{
	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight_buf[2][8][16];//solution2: 16->16
	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> bias_buf[2][8];
	ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> top[2][128][13][13];
	ap_int<512> stream_temp;
//#pragma HLS INTERFACE m_axi port=data depth=256
#pragma HLS ARRAY_PARTITION variable=weight_buf dim=1
#pragma HLS ARRAY_PARTITION variable=weight_buf dim=2
#pragma HLS ARRAY_PARTITION variable=weight_buf dim=3
#pragma HLS ARRAY_PARTITION variable=bottom dim=1
#pragma HLS ARRAY_PARTITION variable=bottom dim=2 cyclic factor=16 //solution2: 16->24
#pragma HLS ARRAY_PARTITION variable=top dim=2 cyclic factor=8
#pragma HLS ARRAY_PARTITION variable=top dim=1
#pragma HLS ARRAY_PARTITION variable=bias_buf dim=1
#pragma HLS ARRAY_PARTITION variable=bias_buf dim=2
//#pragma HLS ARRAY_PARTITION variable=finalout dim=1 cyclic factor=8
//#pragma HLS ARRAY_PARTITION variable=bottom_padded cyclic dim=1 factor=4
	for(int co=0;co<128;co+=8)
    {
		stream_temp=stream512_in.read();
        for(int coo=0;coo<8;coo++)
        {
#pragma HLS pipeline
            bias_buf[0][coo].range(11,0)=stream_temp.range(coo*24+11,coo*24);
            bias_buf[1][coo].range(11,0)=stream_temp.range(coo*24+23,coo*24+12);
        }


		for(int h=0;h<13;h++)
			for(int w=0;w<13;w++)
            {
#pragma HLS pipeline
                for(int coo=0;coo<8;coo++)
                {
#pragma HLS unroll
					top[0][co+coo][h][w]=bias_buf[0][coo];
					top[1][co+coo][h][w]=bias_buf[1][coo];
                }
            }
    }
/*	FILE *conv5_file;
	conv5_file = fopen("LRCN_test_conv5_bias2.txt","w+");
	for(int i=0; i<128;i++)
	{
		for(int j=0; j<13;j++)
		{
		for(int k=0; k<13;k++)
		{
		  fprintf(conv5_file, "%f\n", (float)top[1][i][j][k]);
		}
		}
	}
	fclose(conv5_file);*/

    for (int ci = 0; ci < 192; ci+=16){//solution2: 16->16
    	for(int i=0; i<3; i++){
    		for(int j=0; j<3; j++){
    			for(int co=0;co<128;co+=8){
#pragma HLS dataflow
                    load_weights_5(weight_buf,stream512_in);


                    for(int h=0;h<13;h++){
                        for(int w=0;w<13;w++){
#pragma HLS pipeline
                            for (int coo = 0; coo < 8; coo++){ //try actuall factor 16
#pragma HLS unroll
                                for(int ct=0;ct<2;ct++){

                                	/*for(int cii=0;cii<16;cii++){
									#pragma HLS unroll
										top[ct][co+coo][h][w]+=weight_buf[ct][coo][cii]*bottom[ct][ci+cii][h+i][w+j];
									}*/
#pragma HLS unroll
									top[ct][co+coo][h][w]+=compute_engine_5(weight_buf[ct][coo][0] , bottom[ct][ci+0][h+i][w+j],//try actuall factor 16
                                                                    weight_buf[ct][coo][1] , bottom[ct][ci+1][h+i][w+j],
                                                                    weight_buf[ct][coo][2] , bottom[ct][ci+2][h+i][w+j],
                                                                    weight_buf[ct][coo][3] , bottom[ct][ci+3][h+i][w+j],
                                                                    weight_buf[ct][coo][4] , bottom[ct][ci+4][h+i][w+j],
                                                                    weight_buf[ct][coo][5] , bottom[ct][ci+5][h+i][w+j],
                                                                    weight_buf[ct][coo][6] , bottom[ct][ci+6][h+i][w+j],
                                                                    weight_buf[ct][coo][7] , bottom[ct][ci+7][h+i][w+j],
                                                                    weight_buf[ct][coo][8] , bottom[ct][ci+8][h+i][w+j],
                                                                    weight_buf[ct][coo][9] , bottom[ct][ci+9][h+i][w+j],
                                                                    weight_buf[ct][coo][10] , bottom[ct][ci+10][h+i][w+j],
																	weight_buf[ct][coo][11] , bottom[ct][ci+11][h+i][w+j],
																	weight_buf[ct][coo][12] , bottom[ct][ci+12][h+i][w+j],
																	weight_buf[ct][coo][13] , bottom[ct][ci+13][h+i][w+j],
																	weight_buf[ct][coo][14] , bottom[ct][ci+14][h+i][w+j],
																	weight_buf[ct][coo][15] , bottom[ct][ci+15][h+i][w+j]);

                                }
                            }
                        }
                    }
                }
            }
        }
    }

   /* FILE *conv5_file1;
    conv5_file1 = fopen("Q8_conv5_rst.txt","w+");
	for(int ct=0; ct<2;ct++)
	for(int i=0; i<128;i++)
	{
		for(int j=0; j<13;j++)
		{
		for(int k=0; k<13;k++)
		{
		  fprintf(conv5_file1, "%f\n", (float)top[ct][i][j][k]);
		}
		}
	}
	fclose(conv5_file1);*/

	for(int ii=0;ii<128;ii+=8)
	for(int h=0;h<6;h++)
		for(int w=0;w<6;w++){
#pragma HLS pipeline
			for(int i=0;i<8;i++)
			{
#pragma HLS unroll
				finalout[ii+i][h][w]=max_engine_5(	top[0][ii+i][h*2][w*2],top[0][ii+i][h*2][w*2+1],top[0][ii+i][h*2][w*2+2],
													top[0][ii+i][h*2+1][w*2],top[0][ii+i][h*2+1][w*2+1],top[0][ii+i][h*2+1][w*2+2],
													top[0][ii+i][h*2+2][w*2],top[0][ii+i][h*2+2][w*2+1],top[0][ii+i][h*2+2][w*2+2]);

				finalout[128+ii+i][h][w]=max_engine_5(	top[1][ii+i][h*2][w*2],top[1][ii+i][h*2][w*2+1],top[1][ii+i][h*2][w*2+2],
														top[1][ii+i][h*2+1][w*2],top[1][ii+i][h*2+1][w*2+1],top[1][ii+i][h*2+1][w*2+2],
														top[1][ii+i][h*2+2][w*2],top[1][ii+i][h*2+2][w*2+1],top[1][ii+i][h*2+2][w*2+2]);

			}
		}

		/*FILE *conv5_file;
		conv5_file = fopen("LRCN_test_conv5_pooling_rst.txt","w+");
		for(int i=0; i<256;i++)
		{
			for(int j=0; j<6;j++)
			{
			for(int k=0; k<6;k++)
			{
			  fprintf(conv5_file, "%f\n", (float)finalout[i][j][k]);
			}
			}
		}
		fclose(conv5_file);*/

}

ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> compute_engine_6(ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight0,ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> bot0,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight1,ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT>   bot1,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight2,ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT>   bot2,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight3,ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT>   bot3,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight4,ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT>   bot4,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight5,ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT>   bot5,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight6,ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT>   bot6,
							ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight7,ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT>   bot7

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




void fullconnection6_layer(ap_fixed <TOTAL_B,6,AP_TRN_ZERO,AP_SAT> bottom[256][6][6], hls::stream<int512> &stream512_in, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top[256])
{

//#pragma HLS INTERFACE m_axi port=data depth=256
	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight[2][8][8];

#pragma HLS ARRAY_PARTITION variable=weight dim=1
#pragma HLS ARRAY_PARTITION variable=weight dim=2
#pragma HLS ARRAY_PARTITION variable=bottom dim=1 cyclic factor=8
#pragma HLS ARRAY_PARTITION variable=top dim=1 cyclic factor=8
ap_int<512> stream_temp;
    for(int i=0;i<256;i+=32)
    {
#pragma HLS pipeline
    	stream_temp=stream512_in.read();
    	for(int j=0;j<32;j+=8)
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

                    for(int h=0;h<6 ;h++)
                    for(int w=0;w<6 ;w++){
                      	for(int c=0;c<256 ;c+=16)
                    	for(int n=0;n<256 ;n+=8){ //4096->256
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
                			/*for(int ii=0;ii<8;ii++)
                			{
                				top[n+nn]+=weight[0][nn][ii]*bottom[c+ii][h][w];

                			}*/
                			#pragma HLS unroll
                			top[n+nn]+=compute_engine_6(
                					weight[0][nn][0],    bottom[c+0][h][w],
                					weight[0][nn][1],    bottom[c+1][h][w],
									weight[0][nn][2],    bottom[c+2][h][w],
									weight[0][nn][3],    bottom[c+3][h][w],
									weight[0][nn][4],    bottom[c+4][h][w],
									weight[0][nn][5],    bottom[c+5][h][w],
									weight[0][nn][6],    bottom[c+6][h][w],
									weight[0][nn][7],    bottom[c+7][h][w]);
                		}


                		for(int nn=0;nn<8;nn++)
                		{
                			/*for(int ii=0;ii<8;ii++)
							{
								top[n+nn]+=weight[1][nn][ii]*bottom[c+ii+8][h][w];

							}*/

							#pragma HLS unroll
                			top[n+nn]+=compute_engine_6(
                					weight[1][nn][0],    bottom[c+8][h][w],
                					weight[1][nn][1],    bottom[c+9][h][w],
									weight[1][nn][2],    bottom[c+10][h][w],
									weight[1][nn][3],    bottom[c+11][h][w],
									weight[1][nn][4],    bottom[c+12][h][w],
									weight[1][nn][5],    bottom[c+13][h][w],
									weight[1][nn][6],    bottom[c+14][h][w],
									weight[1][nn][7],    bottom[c+15][h][w]);
                		}
                    }

            	}


	for(int i=0;i<256;i++)
	{
#pragma HLS pipeline
		if(top[i]<0) top[i]=0;
	}

	/*FILE *conv6_file;
	    conv6_file = fopen("fc6_rst.txt","w+");
	    	for(int i=0; i<256;i++)
	    	{
	    		 fprintf(conv6_file, "%f\n", (float)top[i]);
	    	}
	    	fclose(conv6_file);*/

}






ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> compute_engine_7(ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight0,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot0,
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





void fullconnection7_layer(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> bottom[256], hls::stream<int512> &stream512_in, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top[256])
{

//#pragma HLS INTERFACE m_axi port=data depth=256
	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight[2][8][8];

#pragma HLS ARRAY_PARTITION variable=weight dim=1
#pragma HLS ARRAY_PARTITION variable=weight dim=2
#pragma HLS ARRAY_PARTITION variable=bottom dim=1 cyclic factor=8
#pragma HLS ARRAY_PARTITION variable=top dim=1 cyclic factor=8
	ap_int<512> stream_temp;
    for(int i=0;i<256;i+=32)
    {
#pragma HLS pipeline
    	stream_temp=stream512_in.read();
    	for(int j=0;j<32;j+=8)
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


                      	for(int c=0;c<256;c+=16)
                    	for(int n=0;n<256;n+=8){
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
                    	                			/*for(int ii=0;ii<8;ii++)
													{
														top[n+nn]+=weight[0][nn][ii]*bottom[c+ii];

													}*/
                    							#pragma HLS unroll
                    	                			top[n+nn]+=compute_engine_7(
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
                    	                			/*for(int ii=0;ii<8;ii++)
													{
														top[n+nn]+=weight[1][nn][ii]*bottom[c+ii+8];

													}*/
                    							#pragma HLS unroll
                    	                			top[n+nn]+=compute_engine_7(
                    	                					weight[1][nn][0],    bottom[c+8],
                    	                					weight[1][nn][1],    bottom[c+9],
                    										weight[1][nn][2],    bottom[c+10],
                    										weight[1][nn][3],    bottom[c+11],
                    										weight[1][nn][4],    bottom[c+12],
                    										weight[1][nn][5],    bottom[c+13],
                    										weight[1][nn][6],    bottom[c+14],
                    										weight[1][nn][7],    bottom[c+15]);
                    	                		}
                    }




	for(int i=0;i<256;i+=8)
	{
#pragma HLS pipeline
		for(int ii=0;ii<8;ii++)
		{

			#pragma HLS unroll
			if(top[i+ii]<0) top[i+ii]=0;
		}
	}

	/*FILE *conv7_file;
	conv7_file = fopen("fc7_rst.txt","w+");
	    	for(int i=0; i<256;i++)
	    	{
	    		 fprintf(conv7_file, "%f\n", (float)top[i]);
	    	}
	    	fclose(conv7_file);*/
}



ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> compute_engine_8(ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight0,ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT>   bot0,
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






void fullconnection8_layer(ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> bottom[256], hls::stream<int512> &stream512_in, ap_fixed <TOTAL_B,5,AP_TRN_ZERO,AP_SAT> top[1000])
{
//#pragma HLS INTERFACE m_axi port=data depth=256

	ap_fixed<12,1,AP_TRN_ZERO,AP_SAT> weight[2][8][8];
	ap_int<512> stream_temp;
#pragma HLS ARRAY_PARTITION variable=weight dim=1
#pragma HLS ARRAY_PARTITION variable=weight dim=2
#pragma HLS ARRAY_PARTITION variable=bottom dim=1 cyclic factor=8
#pragma HLS ARRAY_PARTITION variable=top dim=1 cyclic factor=8

    for(int i=0;i<1000;i+=40)
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



						for(int c=0;c<256;c+=16)
                    	for(int n=0;n<1000 ;n+=8)
                    		{
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
                        	                			/*for(int ii=0;ii<8;ii++)
														{
															top[n+nn]+=weight[0][nn][ii]*bottom[c+ii];

														}*/
                        							#pragma HLS unroll
                        	                			top[n+nn]+=compute_engine_8(
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
                        	                			/*for(int ii=0;ii<8;ii++)
														{
															top[n+nn]+=weight[1][nn][ii]*bottom[c+ii+8];

														}*/
                        							#pragma HLS unroll
                        	                			top[n+nn]+=compute_engine_8(
                        	                					weight[1][nn][0],    bottom[c+8],
                        	                					weight[1][nn][1],    bottom[c+9],
                        										weight[1][nn][2],    bottom[c+10],
                        										weight[1][nn][3],    bottom[c+11],
                        										weight[1][nn][4],    bottom[c+12],
                        										weight[1][nn][5],    bottom[c+13],
                        										weight[1][nn][6],    bottom[c+14],
                        										weight[1][nn][7],    bottom[c+15]);
                        	                		}
                    }

/*FILE *conv8_file;
conv8_file = fopen("fc8_rst.txt","w+");
		for(int i=0; i<1000;i++)
		{
			 fprintf(conv8_file, "%f\n", (float)top[i]);
		}
		fclose(conv8_file);*/

//Relu is not needed
/*	for(int i=0;i<1000;i+=8)
	{
#pragma HLS pipeline
		for(int ii=0;ii<8;ii++)
		{

			#pragma HLS unroll
			if(top[i+ii]<0) top[i+ii]=0;
		}
	}*/
}

