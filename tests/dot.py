from env import *

import numpy as np
from pylog import *

@pylog(mode='debug')
def pl_simple_map(a, b):

    c = dot(a, b)
    e = dot(a[3, 1:3,:-2], b[1, 3:5, :-2])

    x = 1
    y = 3
    z = dot(x, y)


    f = plmap(lambda x, y: x * y, a[3, 1:3,:-2], b[1, 3:5, :-2])

    return c

if __name__ == "__main__":
    # a = np.array([1, 3, 6, 7, 10])
    # b = np.array([1, 3, 6, 7, 10, 13])
    a = np.random.rand(4,5,6).astype(np.float32)
    b = np.random.rand(4,5,6).astype(np.float32)
    c = pl_simple_map(a, b)
    print(c)
