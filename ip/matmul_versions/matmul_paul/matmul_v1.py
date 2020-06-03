import sys
sys.path.extend(['.', '..', '../..'])

import numpy as np
from pylog import *

@pylog(mode='hwgen')
def gemm_v1(a, b, c):

    bufferA = np.empty((1024,), pl_fixed(16, 12))

    for i in range(1024):
        for k in range(1024).pipeline():
            bufferA[k] = a[i][k]
        for j in range(1024).unroll(16):
            tmp = pl_fixed(16, 12)
            tmp = 0.0
            for k in range(1024).pipeline():
                tmp += bufferA[k] * b[k][j]
            c[i][j] = tmp

if __name__ == "__main__":
    length = 1024
    a = np.zeros((length, length), pl_fixed(16, 12))
    b = np.zeros((length, length), pl_fixed(16, 12))
    c = np.zeros((length, length), pl_fixed(16, 12))
    gemm_v1(a, b, c)
