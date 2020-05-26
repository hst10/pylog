from env import *

import numpy as np
from pylog import *

@pylog
def pl_subscript(a, b):

    for i in range(4, 15, 2):
        a[b[i]][f(a * b + 13)][csdf*w34 - 1] = b
    # a[1, :b:s, 3] = b


if __name__ == "__main__":
    a = np.array([1, 3, 6, 7, 10])
    b = np.array([1, 3, 6, 7, 10])
    pl_subscript(a, b)
    print(c)
