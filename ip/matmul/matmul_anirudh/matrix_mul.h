#define M 3
#define N 3
#define K 3
#define SIZE 9 //used for matrix add
//matrix mul code of A*B=C. dimensions of matrices are A MxK B KxN C MxN
//change M,N,K to change dimensions of matrix multiplication code
//change depth = size of matrix manually to complete interface ie A = M*K B=K*N C=M*N
//this must be done manually as HLS does not compile with #define constants
//used in interface pragmas

void matmul_pipeline(float * A,float * B, volatile float * C);
void matmul_unroll(float * A,float * B,volatile float * C);
void matmul_triple_unroll(float * A,float * B,volatile float * C);
void matmul_triple_pipeline(float * A,float * B,volatile float * C);
void matrix_add_unroll(float * arr1,float * arr2,float * arr3);
void matrix_add_pipeline(float * arr1,float * arr2,float * arr3);

