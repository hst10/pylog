//variables to be scheduled
#define VAR1_ 1  
#define VAR2_ 16
//variables to be defined
#define SIZE_A_ 16
#define SIZE_B_ 16
#define DTYPE_ int
//invariant variables
#define MAX_SIZE_ 1024

const static int VAR1 = VAR1_;
const static int VAR2 = VAR2_;
const static int SIZE_A = SIZE_A_;
const static int SIZE_B = SIZE_B_;
const static int SIZE_C = SIZE_A_+ SIZE_B_-1;
const static int MAX_SIZE = MAX_SIZE_;
typedef DTYPE_ DTYPE;

void convolve_1d(DTYPE A[SIZE_A] , DTYPE B[SIZE_B], DTYPE C[SIZE_C]);

