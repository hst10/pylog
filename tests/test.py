from env import *

import numpy as np
from pylog import *

@pylog(mode='cgen')
def pl_test(a, b):

    # def add_one(a, b):
    #     b = a + 1

    res = np.empty([3,5,7], int)

    # add_one(a, res)

    d = a[3::-2] + 3.5

    a = np.empty([3,5,7], int)
    c = np.empty([3,5,7,9], float)

    b = 10 + a

    x = a * b

    b[:,:,:] = a
    c[:,:,:,3] = b

    a[:,:,:] = 10

    a = 10

if __name__ == "__main__":
    a = np.array([1, 3, 6, 7, 10]).astype(np.int64)
    b = np.array([1, 3, 6, 7, 10]).astype(np.int32)
    pl_test(a, b)
