from env import *

import numpy as np
from pylog import *

@pylog(mode='debug')
def pl_test(a, b):

    a = np.empty([3,5,7], float)

    if 10 > 4:
        c = 4
    else:
        c = 9

    b = 10 + c

    return b


if __name__ == "__main__":
    a = np.array([1, 3, 6, 7, 10])
    b = np.array([1, 3, 6, 7, 10])
    c = pl_test(a, b)
    print(c)
