#include "matrix_mul.h"
#include <string.h>

// set matmul and matadd constants in h file
//single pipeline pragma implementation
void matmul_pipeline(float * A,float * B, volatile float * C)
{
	#pragma HLS INTERFACE m_axi depth=1048576 offset=slave port=A bundle=DATA_A
    #pragma HLS INTERFACE m_axi depth=1048576 offset=slave port=B bundle=DATA_B
    #pragma HLS INTERFACE m_axi depth=1048576 offset=slave port=C bundle=DATA_C
    #pragma HLS INTERFACE s_axilite port=return

	float t_A[M][K];
	float t_B[K][N];
	float t_C[M][N];

	memcpy(t_A,(const float*)A,M*K*sizeof(float));
	memcpy(t_B,(const float*)B,K*N*sizeof(float));
	memcpy(t_C,(const float*)C,M*N*sizeof(float));

	int i,j,k;
    for(i = 0; i < M; i++)
    {

        for(j = 0; j < N; j++)
        {

            for(k = 0; k < K; k++)
            {
                #pragma HLS PIPELINE
                t_C[i][j] = t_C[i][j] + t_A[i][k]*t_B[k][j];
            }
        }
    }

	memcpy((float *)C,t_C,M*N*sizeof(float));


}

//single unroll pragma implementation
void matmul_unroll(float * A,float * B,volatile float * C)
{
    #pragma HLS INTERFACE m_axi depth=9 offset=slave port=A bundle=DATA_A
    #pragma HLS INTERFACE m_axi depth=9 offset=slave port=B bundle=DATA_B
    #pragma HLS INTERFACE m_axi depth=9 offset=slave port=C bundle=DATA_C
    #pragma HLS INTERFACE s_axilite port=return

	float t_A[M][K];
	float t_B[K][N];
	float t_C[M][N];

	#pragma HLS ARRAY_PARTITION variable=t_A complete
	#pragma HLS_ARRAY_PARTITION variable=t_B complete
	#pragma HLS_ARRAY_PARTITION variable=t_C complete

	memcpy(t_A,(const float*)A,M*K*sizeof(float));
	memcpy(t_B,(const float*)B,K*N*sizeof(float));
	memcpy(t_C,(const float*)C,M*N*sizeof(float));

	int i,j,k;
    for(i = 0; i < M; i++)
    {

        for(j = 0; j < N; j++)
        {

            for(k = 0; k < K; k++)
            {
               #pragma HLS UNROLL
                t_C[i][j] = t_C[i][j] + t_A[i][k]*t_B[k][j];
            }
        }
    }

	memcpy((float *)C,t_C,M*N*sizeof(float));
}

//unroll pragma applied to all 3 loops
void matmul_triple_unroll(float * A,float * B,volatile float * C)
{
   	#pragma HLS INTERFACE m_axi depth=1048576 offset=slave port=A bundle=DATA_A
    #pragma HLS INTERFACE m_axi depth=1048576 offset=slave port=B bundle=DATA_B
    #pragma HLS INTERFACE m_axi depth=1048576 offset=slave port=C bundle=DATA_C
    #pragma HLS INTERFACE s_axilite port=return

	float t_A[M][K];
	float t_B[K][N];
	float t_C[M][N];

    #pragma HLS ARRAY_PARTITION variable=t_A complete
	#pragma HLS_ARRAY_PARTITION variable=t_B complete
	#pragma HLS_ARRAY_PARTITION variable=t_C complete

	memcpy(t_A,(const float*)A,M*K*sizeof(float));
	memcpy(t_B,(const float*)B,K*N*sizeof(float));
	memcpy(t_C,(const float*)C,M*N*sizeof(float));

	int i,j,k;
    for(i = 0; i < M; i++)
    {
        #pragma HLS UNROLL
        for(j = 0; j < N; j++)
        {
            #pragma HLS UNROLL
            for(k = 0; k < K; k++)
            {
                #pragma HLS UNROLL
                t_C[i][j] = t_C[i][j] + t_A[i][k]*t_B[k][j];
            }
        }
    }

	memcpy((float *)C,t_C,M*N*sizeof(float));
}

// pipeline pragma added to all 3 loops
void matmul_triple_pipeline(float * A,float * B,volatile float * C)
{
   	#pragma HLS INTERFACE m_axi depth=1048576 offset=slave port=A bundle=DATA_A
    #pragma HLS INTERFACE m_axi depth=1048576 offset=slave port=B bundle=DATA_B
    #pragma HLS INTERFACE m_axi depth=1048576 offset=slave port=C bundle=DATA_C
    #pragma HLS INTERFACE s_axilite port=return

	float t_A[M][K];
	float t_B[K][N];
	float t_C[M][N];

	memcpy(t_A,(const float*)A,M*K*sizeof(float));
	memcpy(t_B,(const float*)B,K*N*sizeof(float));
	memcpy(t_C,(const float*)C,M*N*sizeof(float));

	int i,j,k;
    for(i = 0; i < M; i++)
    {
        #pragma HLS PIPELINE
        for(j = 0; j < N; j++)
        {
            #pragma HLS PIPELINE
            for(k = 0; k < K; k++)
            {
                #pragma HLS PIPELINE
                t_C[i][j] = t_C[i][j] + t_A[i][k]*t_B[k][j];
            }
        }
    }

	memcpy((float *)C,t_C,M*N*sizeof(float));
}


// simple matrix add implementations change SIZE pragma above to change matrix sizes
void matrix_add_unroll(float * arr1,float* arr2,float * arr3)
{
	#pragma HLS INTERFACE m_axi depth=9 offset=slave port=arr1 bundle=DATA_A
	#pragma HLS INTERFACE m_axi depth=9 offset=slave port=arr2 bundle=DATA_B
	#pragma HLS INTERFACE m_axi depth=9 offset=slave port=arr3 bundle=DATA_C
	#pragma HLS INTERFACE s_axilite port=return

	float t_A[SIZE];
	float t_B[SIZE];
	float t_C[SIZE];

	memcpy(t_A,(const float*)arr1,SIZE*sizeof(float));
	memcpy(t_B,(const float*)arr2,SIZE*sizeof(float));
	memcpy(t_C,(const float*)arr3,SIZE*sizeof(float));

	#pragma HLS ARRAY_PARTITION variable=t_A complete
	#pragma HLS ARRAY_PARTITION variable=t_B complete
	#pragma HLS ARRAY_PARTITION variable=t_C complete
	int i;
	for(i=0;i<SIZE;i++)
	{
		#pragma HLS UNROLL
		t_C[i]=t_A[i]+t_B[i];
	}
	memcpy((float *)arr3,t_C,SIZE*sizeof(float));
}

void matrix_add_pipeline(float * arr1,float * arr2,float * arr3)
{
	#pragma HLS INTERFACE m_axi depth=9 offset=slave port=arr1 bundle=DATA_A
	#pragma HLS INTERFACE m_axi depth=9 offset=slave port=arr2 bundle=DATA_B
	#pragma HLS INTERFACE m_axi depth=9 offset=slave port=arr3 bundle=DATA_C
	#pragma HLS INTERFACE s_axilite port=return

	float t_A[SIZE];
	float t_B[SIZE];
	float t_C[SIZE];

	memcpy(t_A,(const float*)arr1,SIZE*sizeof(float));
	memcpy(t_B,(const float*)arr2,SIZE*sizeof(float));
	memcpy(t_C,(const float*)arr3,SIZE*sizeof(float));

	int i;
	for(i=0;i<SIZE;i++)
	{
		//#pragma HLS loop_tripcount min=1 max=1000
		#pragma HLS PIPELINE
		t_C[i]=t_A[i]+t_B[i];
	}

	memcpy((float *)arr3,t_C,SIZE*sizeof(float));
}

