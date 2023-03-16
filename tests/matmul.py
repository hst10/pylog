import numpy as np
# from pysim import *
from pylog import *

@pylog(mode='debug')#(mode='pysim')
def pl_matmul(a, b, c):
    def matmul(a, b, c):
        bufferA = np.empty((128, 1024), pl_fixed(16, 16))
        pragma("HLS array_partition variable=bufferA cyclic factor=16 dim=2")
        bufferB = np.empty((256,), pl_fixed(16, 16))
        pragma("HLS array_partition variable=bufferB complete dim=1")
        tmp = np.empty((128, 256), pl_fixed(16, 16))
        pragma("HLS array_partition variable=tmp complete dim=2")
        tmp_256 = pl_fixed(256, 256)
        
        for i in range(0, 1024, 128):
            for ii in range(128):
                for k in range(0, 1024, 16).pipeline():
                    tmp_256 = a[i+ii][k/16]
                    for kk in range(16).unroll():
                        bufferA[ii][k+kk][15:0] = tmp_256[kk*16+15:kk*16]
            for j in range(0, 1024, 256):
                for ii in range(128).pipeline():
                    for jj in range(256).unroll():
                        tmp[ii][jj] = 0
                for k in range(1024):
                    for jj in range(0, 256, 16).pipeline():
                        tmp_256 = b[k][(j+jj)/16]
                        for jjj in range(16).unroll():
                            bufferB[jj+jjj][15:0] = tmp_256[jjj*16+15:jjj*16]
                    for ii in range(128).pipeline():
                        for jj in range(256).unroll():
                            tmp[ii][jj] += bufferA[ii][k] * bufferB[jj]
                for ii in range(128):
                    for jj in range(0, 256, 16).pipeline():
                        for jjj in range(16).unroll():
                            tmp_256[jjj*16+15:jjj*16] = tmp[ii][jj+jjj][15:0]
                        c[i+ii][(j+jj)/16] = tmp_256

    matmul(a, b, c)

if __name__ == "__main__":
    a = np.zeros((1024, 64), pl_fixed(256, 256))
    b = np.zeros((1024, 64), pl_fixed(256, 256))
    c = np.zeros((1024, 64), pl_fixed(256, 256))
    pl_matmul(a, b, c)
    print(c)
