from pylog import *
#import numpy as np

#Based on polybench2.0/image-processing/gauss-filter/gauss-filter.c
N=1080
M=1920
T=1920

@pylog
def pl_gauss_filter(in_image, Gauss,tot,g_acc1,g_acc2,g_tmp_image,gauss_image):
    def init_array(in_image,Gauss):
        for i in range(N):
            for j in range(M):
                in_image[i,j]=(i*j+0.0)/M
        for i in range(4):
            Gauss[i]=i

    def compute(in_image, Gauss,tot,g_acc1,g_acc2,g_tmp_image,gauss_image):
        t=T
        m=M
        n=N
        tot[0]=0
        for k in range(t-1,t+2):
            tot[k+2-t]=tot[k+1-t]+Gauss[k-t+1]
        for k in range(t-1,t+2):#duplicate in original code
            tot[k+2-t]=tot[k+1-t]+Gauss[k-t+1]
        for x in range(1,n-2):
            for y in range(0,m):
                g_acc1[x,y,0]=0
                for k in range(t-1,t+2):
                    g_acc1[x,y,k+2-t]=g_acc1[x,y,k+1-t]+in_image[x+k-t,y]*Gauss[k-t+1]
                g_tmp_image[x,y]=g_acc1[x,y,3]/tot[3]
        for x in range(1,n-1):
            for y in range(1,m-1):
                g_acc2[x,y,0]=0
                for k in range(t-1,t+2):
                    g_acc2[x,y,k+2-t]=g_acc2[x,y,k+1-t]+g_tmp_image[x,y+k-t]*Gauss[k-t+1]
                gauss_image[x,y]=g_acc2[x,y,3]/tot[3]
    init_array(in_image,Gauss)
    compute(in_image, Gauss,tot,g_acc1,g_acc2,g_tmp_image,gauss_image)

if __name__=="__main__":
    tot=np.zeros(4,dtype=np.single)
    Gauss=np.zeros(4,dtype=np.single)
    g_tmp_image=np.zeros([N,M],dtype=np.single)
    g_acc1=np.zeros([N,M,4],dtype=np.single)
    g_acc2=np.zeros([N,M,4],dtype=np.single)
    in_image=np.zeros([N,M],dtype=np.single)
    gauss_image=np.zeros([N,M],dtype=np.single)
    pl_gauss_filter(in_image, Gauss, tot, g_acc1, g_acc2, g_tmp_image, gauss_image)