from env import *

import numpy as np
from pylog import *

@pylog(mode='debug')
def pl_test(a, b):

    d = a[3::-2] + 3.5

    a = np.empty([3,5,7], float)

    b = 10 + a

    return b


if __name__ == "__main__":
    a = np.array([1, 3, 6, 7, 10])
    b = np.array([1, 3, 6, 7, 10])
    c = pl_test(a, b)
    print(c)
