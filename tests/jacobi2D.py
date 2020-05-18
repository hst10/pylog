from pylog import *
#import numpy as np

# Based on polybench/stencils/jacobi-2d-imper/jacobi-2d-imper.c
N=1000
NUM_ITER=20
#definition follows STANDARD_DATASERT in polybench/stencils/jacobi-2d-imper/jacobi-2d-imper.h

@pylog
def pl_jacobi2D(input, temp, output):

    def init_array(A, B, C):
        for i in range(N):
            for j in range(N):
                A[i,j]=(i*(j+2)+2+0.0)/N
                B[i, j] = (i * (j + 2) + 2 + 0.0) / N
                C[i, j] = (i * (j + 2) + 2 + 0.0) / N
                #B[i,j]=(i*(j+3)+3+0.0)/N

    def kernel_jacobi_2d(A, B):
        for i in range(1,N-1):
            for j in range(1,N-1):
                B[i,j]=0.2*(A[i,j]+A[i,j-1]+A[i,j+1]+A[i+1,j]+A[i-1,j])

    def kernel_seidel_2d(A, B):
        for i in range(2,N-2):
            for j in range(2,N-2):
                B[i,j]=(A[i-1,j-1]+A[i-1,j]+A[i-1,j+1]+A[i,j-1]+A[i,j]+A[i,j+1]+A[i+1,j-1]+A[i+1,j]+A[i+1,j+1])/9.0
    #init_array(input, temp, output)
    if NUM_ITER==0:
        return 0
    if NUM_ITER%2==0:
        kernel_jacobi_2d(input, temp)
        kernel_jacobi_2d(temp, output)
        for idx_iter in range(2,NUM_ITER):
            kernel_jacobi_2d(output, temp)
            kernel_jacobi_2d(temp, output)
        return 0
    else:
        kernel_jacobi_2d(input,output)
        for idx_iter in range(1,NUM_ITER):
            kernel_jacobi_2d(output, temp)
            kernel_jacobi_2d(temp,output)
        return 0

if __name__=="__main__":
    input=np.zeros([N,N],dtype=np.single)
    temp=np.zeros([N,N],dtype=np.single)
    output=np.zeros([N,N],dtype=np.single)
    input[50,50]=1.0
    pl_jacobi2D(input, temp, output)
    # import seaborn as sns
    # import matplotlib.pylab as plt
    #
    # ax = sns.heatmap(input, linewidth=0.5)
    # plt.show()
    # ax = sns.heatmap(temp, linewidth=0.5)
    # plt.show()
    # ax = sns.heatmap(output, linewidth=0.5)
    # plt.show()
    # pass