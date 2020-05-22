from env import *

import numpy as np
from pylog import *

@pylog(mode='debug')
def pl_test(a, b):

    d = a[3::-2] + 3.5

    a = np.empty([3,5,7], int)
    c = np.empty([3,5,7,9], float)

    b = 10 + a

    b[:,:,:] = a
    c[:,:,:,3] = b

    a[:,:,:] = 10

    a = 10

    return b


if __name__ == "__main__":
    a = np.array([1, 3, 6, 7, 10]).astype(np.uint64)
    b = np.array([1, 3, 6, 7, 10]).astype(np.uint32)
    c = pl_test(a, b)
    print(c)
