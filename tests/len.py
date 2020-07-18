from env import *

import numpy as np
#from pysim import *
from pylog import *

@pylog(mode='debug')#(mode='pysim')
def pl_len(a, b, c):
    def add(a, b):
        return a + b

    def test_len(a, b, c):
        tmp = np.empty((128, 256, 512, 1024), pl_fixed(16, 16))
        pragma("HLS array_partition variable=tmp complete dim=2")

        l1 = add(len(tmp), 1)
        l2 = len(tmp[0])
        l3 = len(tmp[1][2])
        l4 = len(tmp[3][2][1])

    test_len(a, b, c)

if __name__ == "__main__":
    a = np.zeros((1024, 64), pl_fixed(256, 256))
    b = np.zeros((1024, 64), pl_fixed(256, 256))
    c = np.zeros((1024, 64), pl_fixed(256, 256))
    pl_len(a, b, c)
    print(c)
