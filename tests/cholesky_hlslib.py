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
def pl_cholesky(A,p):
    def kernel_cholesky(A,p):
        for i in range(1024):# TODO: replace hard coded with N
            x=A[i,i]
            for j in range(i):
                x=x-A[i,j]*A[i,j]
            p[i]=1.0/x**0.5
            for j in range(i+1,1024):# TODO: replace hard coded with N
                x=A[i,j]

                #replacement of loop-k

                pragma("HLS ARRAY_PARTITION variable=A cyclic factor=2 dim=2")
                pragma("HLS RESOURCE variable=A core=RAM_2P_BRAM") #we assume A is in BRAM
                buf = np.empty([16],
                               np.float)  # TODO: replace hard coded 8 in 16(2*8) with L4_UF # is a completely unrolled register
                pragma("HLS ARRAY_PARTITION variable=buf complete")
                for a in range(16):# TODO: replace hard coded 8 in 16(2*8) with L4_UF # is a completely unrolled register
                    pragma("HLS unroll complete")
                    buf[a]=0
                for k1 in range((i-1)/(2*8)+1):#TODO: replace hard coded 8  with L4_UF
                    pragma("HLS pipeline II=8")
                    for k2 in range(2*8):#TODO: replace hard coded 8 with L4_UF #fully unrolled
                        k=k1*(2*8)+k2 #TODO: replace hard coded 8 with L4_UF
                        buf[k2]+=A[j,k]*A[i,k] if (k>=0 and k<i) else 0.0
                len=i-0 if (i-0<2*8) else (2*8)#TODO: implement support to macro function (or inline function) #TODO: replace hard coded 8 with L4_UF

                if (len>4):
                    limit=3
                elif (len>2):
                    limit=2
                elif (len==2):
                    limit=1
                else:
                    limit=0

                for l in range(limit):
                    pragma("HLS pipeline II=8")
                    pragma("HLS DEPENDENCE variable = buf inter false")
                    for a in range(8):#TODO: replace hard coded 8 with L4_UF
                        buf[a]=buf[2*a]+buf[2*a+1]
                x-=buf[0]
                A[j, i] = x * p[i]
    kernel_cholesky(A,p)

if __name__=="__main__":
    A=np.empty([N,N],dtype=np.float)
    p=np.empty(N,dtype=np.float)
    init_array(A,p)
    pl_cholesky(A,p)