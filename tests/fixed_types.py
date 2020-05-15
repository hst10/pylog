from env import *

import numpy as np
from pylog import *

@pylog(mode='debug')
def pl_add(a, b):

    c = pl_fixed(16, 3)

    c = pl_int8(25)

    a = np.empty((3,), float)

    a = np.empty((3,), pl_fixed(8, 3))

    a = np.empty((3,), pl_int8)

    return c


if __name__ == "__main__":
    a = np.array([1, 3, 6, 7, 10])
    b = np.array([1, 3, 6, 7, 10])
    c = pl_add(a, b)
    print(c)
