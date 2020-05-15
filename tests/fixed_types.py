from env import *

import numpy as np
from pylog import *

@pylog(mode='hwgen')
def pl_fixe_types(lst_a, lst_b):

    a = pl_fixed(16, 3)

    b = pl_int8(25)

    c = np.empty((3,), float)

    d = np.empty((3,), pl_fixed(8, 3))

    e = np.empty((3,), pl_int8)

    return a


if __name__ == "__main__":
    a = np.array([1, 3, 6, 7, 10])
    b = np.array([1, 3, 6, 7, 10])
    c = pl_fixe_types(a, b)
    print(c)
