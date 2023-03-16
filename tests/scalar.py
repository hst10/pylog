import numpy as np
from pylog import *

@pylog(mode='debug')
def pl_scalar(a, b, c):
    a = a + b
    b = -10.2
    c += 4
    d = np.float32(a + b)

if __name__ == "__main__":

    a = np.float32(4.6)
    b = np.float32(2.6)
    c = np.float32(1.3)
    pl_scalar(a, b, c)
    print(a)
    print(b)
    print(c)
