import sys
sys.path.extend(['/home/shuang91/pylog/'])

import numpy as np
from pylog import *

@pylog
def pl_add(a, b):

    for i in range(4, 15, 2):
        a[b[i]][f(a * b + 13)][csdf*w34 - 1] = b
    # a[1, :b:s, 3] = b
    return c


if __name__ == "__main__":
    a = np.array([1, 3, 6, 7, 10])
    b = np.array([1, 3, 6, 7, 10])
    c = pl_add(a, b)
    print(c)
