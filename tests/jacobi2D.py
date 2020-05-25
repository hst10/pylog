from pylog import *
#import numpy as np

# Based on polybench/stencils/jacobi-2d-imper/jacobi-2d-imper.c
#N=1000
#NUM_ITER=20
#definition follows STANDARD_DATASERT in polybench/stencils/jacobi-2d-imper/jacobi-2d-imper.h
N=100
NUM_ITER=20

@pylog(mode='deploytiming',board='zedboard')
def pl_jacobi2D(input, temp, output):

    def init_array(A, B, C):
        for i in range(100):#TODO: replace hard coded with N
            for j in range(100):#TODO: replace hard coded with N
                A[i,j]=(i*(j+2)+2+0.0)/100#TODO: replace hard coded with N
                B[i, j] = (i * (j + 2) + 2 + 0.0) / 100#TODO: replace hard coded with N
                C[i, j] = (i * (j + 2) + 2 + 0.0) / 100#TODO: replace hard coded with N


    def kernel_jacobi_2d(A, B):
        for i in range(1,100-1):#TODO: replace hard coded with N
            for j in range(1,100-1):#TODO: replace hard coded with N
                B[i,j]=0.2*(A[i,j]+A[i,j-1]+A[i,j+1]+A[i+1,j]+A[i-1,j])

    def kernel_jacobi_2d_slicing(A, B):
        B[1:100-1,1:100-1]=0.2*(A[1:100-1,1:100-1]+A[1:100-1,1-1:100-1-1]+A[1:100-1,1+1:100-1+1]+A[1+1:100-1+1,1:100-1]+A[1-1:100-1-1,1:100-1])#TODO: replace hard coded with N

    def kernel_seidel_2d(A, B):
        for i in range(2,100-2):#TODO: replace hard coded with N
            for j in range(2,100-2):#TODO: replace hard coded with N
                B[i,j]=(A[i-1,j-1]+A[i-1,j]+A[i-1,j+1]+A[i,j-1]+A[i,j]+A[i,j+1]+A[i+1,j-1]+A[i+1,j]+A[i+1,j+1])/9.0

    def kernel_seidel_2d_slicing(A, B):
        B[2:100-2,2:100-2]=(A[2-1:100-2-1,2-1:100-2-1]+A[2-1:100-2-1,2:100-2]+A[2-1:100-2-1,2+1:100-2+1]+A[2:100-2,2-1:100-2-1]+A[2:100-2,2:100-2]+A[2:100-2,2+1:100-2+1]+A[2+1:100-2+1,2-1:100-2-1]+A[2+1:100-2+1,2:100-2]+A[2+1:100-2+1,2+1:100-2+1])/9.0#TODO: replace hard coded with N


    init_array(input, temp, output)
    if 20==0:#TODO: replace hard coded with NUM_ITER
        return 0
    if 20%2==0:#TODO: replace hard coded with NUM_ITER
        kernel_jacobi_2d(input, temp)
        kernel_jacobi_2d(temp, output)
        for idx_iter in range(2,20):#TODO: replace hard coded with NUM_ITER
            kernel_jacobi_2d(output, temp)
            kernel_jacobi_2d(temp, output)
        return 0
    else:
        kernel_jacobi_2d(input,output)
        for idx_iter in range(1,20):#TODO: replace hard coded with NUM_ITER
            kernel_jacobi_2d(output, temp)
            kernel_jacobi_2d(temp,output)
        return 0

#@pylog(mode='deploy',board='zedboard')
#def pl_jacobi2D(input, temp, output):
#    return pl_jacobi2D_golden(input, temp, output)

if __name__=="__main__":
    input = np.empty([N, N], dtype=np.float)
    temp = np.empty([N, N], dtype=np.float)
    output = np.empty([N, N], dtype=np.float)
    #TODO: Adding support np.single. np.zeros
    # input=np.zeros([N,N],dtype=np.single)
    # temp=np.zeros([N,N],dtype=np.single)
    # output=np.zeros([N,N],dtype=np.single)

    pl_jacobi2D(input, temp, output)
    np.save(os.path.join("tests","golden_reference","jacobi2D_input"),input)
    np.save(os.path.join("tests","golden_reference","jacobi2D_temp"),temp)
    np.save(os.path.join("tests","golden_reference","jacobi2D_output"),output)
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