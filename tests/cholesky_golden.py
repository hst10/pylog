import sys
sys.path.extend(['.', '..', '../..'])

from pylog import *

# follows STANDARD DATASET in trisolv
#  ifdef STANDARD_DATASET /* Default if unspecified. */
#   define N 1024
#  endif
N=1024

def init_array(A,p):
    for i in range(1024):# TODO: replace hard coded with N
        p[i]=1/1024# TODO: replace hard coded with N
        for j in range(1024):# TODO: replace hard coded with N
            A[i,j]=1/1024 # TODO: replace hard coded with N

    return 0# TODO: compiler signature return type void if no return

@pylog(mode='hwgen',board='zedboard')
def pl_cholesky_golden(A,p):
    def kernel_cholesky_golden(A,p):
        for i in range(1024):# TODO: replace hard coded with N
            x=A[i,i]
            for j in range(i):
                x=x-A[i,j]*A[i,j]
            p[i]=1.0/x**0.5
            for j in range(i+1,1024):# TODO: replace hard coded with N
                x=A[i,j]
                for k in range(i):
                    x=x-A[j,k]*A[i,k]
                A[j,i]=x*p[i]
    kernel_cholesky_golden(A,p)

if __name__=="__main__":
    A=np.empty([N,N],dtype=np.float)
    p=np.empty(N,dtype=np.float)
    init_array(A,p)
    pl_cholesky_golden(A,p)