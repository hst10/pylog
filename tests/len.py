import numpy as np
#from pysim import *
from pylog import *

@pylog(mode='debug')#(mode='pysim')
def pl_len(a:'buffer', b:'buffer', c):
    def multiply(a):
        result = 1
        for i in a:
            result = result * i
        return result

    def test_len(a, b, c):
        tmp = np.empty((128,), pl_fixed(16, 16))
        tmp2 = np.empty((256,), pl_fixed(16, 16))
        pragma("HLS array_partition variable=tmp complete")
        multiply(tmp)
        multiply(tmp2)

    test_len(a, b, c)

if __name__ == "__main__":
    a = np.zeros((1024, 64), pl_fixed(256, 256))
    b = np.zeros((1024, 64), pl_fixed(256, 256))
    c = np.zeros((1024, 64), pl_fixed(256, 256))
    pl_len(a, b, c)
    print(c)
