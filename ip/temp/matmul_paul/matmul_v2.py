from env import *

import numpy as np
#from pysim import *
from pylog import *

@pylog#(mode='debug')#(mode='pysim')
def pl_matmul(a, b, c):
    def matmul(a, b, c):
        bufferA = np.empty((1024,), pl_fixed(16, 16))
        bufferB = np.empty((256,), pl_fixed(16, 16))
        pragma("HLS array_partition variable=bufferB complete dim=1")
        tmp = np.empty((256,), pl_fixed(16, 16))
        pragma("HLS array_partition variable=tmp complete dim=1")
        
        for i in range(1024):
            for k in range(1024).pipeline():
                bufferA[k] = a[i][k]
            for j in range(0, 1024, 256):
                for jj in range(256).unroll():
                    tmp[jj] = 0
                for k in range(1024):
                    for jj in range(256).pipeline():
                        bufferB[jj] = b[k][j+jj]
                    for jj in range(256).unroll():
                        tmp[jj] += bufferA[k] * bufferB[jj]
                for jj in range(256).pipeline():
                    c[i][j+jj] = tmp[jj]

    matmul(a, b, c)

if __name__ == "__main__":
    length = 1024
    a = np.zeros((length, length), pl_fixed(16, 16))
    b = np.zeros((length, length), pl_fixed(16, 16))
    c = np.zeros((length, length), pl_fixed(16, 16))
    pl_matmul(a, b, c)
    print(c)
