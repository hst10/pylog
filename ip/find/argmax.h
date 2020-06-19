#include <math.h>  
//variables to be scheduled
#define BATCH_ 16  // need to be 2^n 
#define VAR2_ 16
//variables to be defined
#define SIZE_ 20
#define DTYPE_ int
//invariant variables
#define MAX_SIZE_ 1024


const static int BATCH = BATCH_;
const static int ITERATION = (SIZE_%BATCH_==0) ? SIZE_/BATCH_ : SIZE_/BATCH_+1;
const static int STAGE = log2(BATCH)-1; 

const static int VAR2 = VAR2_;
const static int STAGE_2 = log2(VAR2_)-1; 
const static int BOUND = (SIZE_%VAR2_==0) ? SIZE_/VAR2_ : SIZE_/VAR2_+1;

const static int SIZE = SIZE_;
const static int MAX_SIZE = MAX_SIZE_;


typedef DTYPE_ DTYPE;


void argmax(DTYPE A[SIZE] , int* max_index );
DTYPE min_unit(DTYPE a , DTYPE b);
int min_f2(int A[VAR2]);
DTYPE max_unit(DTYPE a , DTYPE b);
DTYPE max_f1(DTYPE A[SIZE]);
