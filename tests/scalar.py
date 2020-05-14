from env import *

import numpy as np
from pylog import *

@pylog(mode='hwgen')
def pl_scalar_test(a, b, c):
    a = a + b
    b = -10.2
    c += 4
    return c


if __name__ == "__main__":

    a = np.float32(4.6)
    b = np.float32(2.6)
    c = np.float32(1.3)
    pl_scalar_test(a, b, c)
    print(a)
    print(b)
    print(c)
