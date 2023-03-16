import numpy as np
#from pysim import *
from pylog import *

@pylog(mode='debug')#(mode='pysim')
def pl_range(a):
    def read_one(a):
        bufferA = np.empty((16, ), pl_fixed(16, 16))
        pragma("HLS array_partition variable=bufferA cyclic factor=16 dim=2")
        tmp_256 = np.empty((1, ), pl_fixed(256, 256))
        
        tmp_256[0] = a
        for i in range(16).unroll():
            bufferA[i][15:0] = tmp_256[0][i*16+15:i*16]

    read_one(a)

if __name__ == "__main__":
    a = np.empty((1, ), pl_fixed(256, 256))
    pl_range(a)
