import sys
sys.path.extend(['/home/shuang91/pylog/'])

import numpy as np
from pysim import *
from pylog import *

@pylog
def pl_top(a, b, c, d):
    
    buf = np.empty([16, 16], int)
    pragma("HLS array_partition variable=buf")

    def matmul(a, b, c):
        for i in range(32):
            for j in range(32).unroll(4):
                tmp = 0.
                for k in range(32).pipeline():
                    tmp += a[i][k] * b[k][j]
                c[i][j] = tmp


    def vecadd(a, b, c):
        for i in range(32):
            c[i] = a[i] + b[i]


    matmul(a, b, c)

    return 0


if __name__ == "__main__":
    length = 32
    a = np.random.rand(length, length)
    b = np.random.rand(length, length)
    c = np.zeros((length, length))
    d = np.random.rand(1)
    pl_top(a, b, c, d)
    print(c)
