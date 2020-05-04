import sys
sys.path.extend(['/home/shuang91/pylog/'])

import numpy as np
from pylog import *

@pylog
def pl_add(a, b):

    def func_inside(c):
        return c + 1

    a = func_inside(another_func(b))

    for ii in range(100, 20, -4):
        for jj in range(10, 245, 3):
            a = b+c

    while (a > 100):
        if (a < foo(b)):
            test += 1
        elif (b > c):
            join -= -9
            asdf = swr34cv_1 + 1
        else:
            return 0
        c = (foo(a + b, c*d)) if (a > 0) else res
        c = 100 if (a > 0) else -10
    # c = blah(1)
    return c


if __name__ == "__main__":
    a = np.array([1, 3, 6, 7, 10])
    b = np.array([1, 3, 6, 7, 10])
    c = pl_add(a, b)
    print(c)
