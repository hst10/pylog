from env import *

import numpy as np
from pylog import *

@pylog# (mode='debug, viz')
def pl_type_infer(a, b):

    f = lambda x: x + 1

    list_a = np.empty((10,20,40), pl_fixed(8,3))
    list_b = np.empty((10,20,40,10), float32)

    # out1 = np.empty((10,20,40,), int)
    out1 = plmap(lambda x, y: x + y, list_a, list_b[:,:,:,2])

    # out2 = np.empty((5,3,6,), int)
    out2 = plmap(lambda x, y: x + y, list_a[:5][ :3, :6], \
                                    list_b[::2, ::7, 3:9, 2])

    out1[::2, ::7, 3:9] = plmap(lambda x, y: x + y, list_a[:5][ :3, :6], \
                                                    list_b[::2, ::7, 3:9, 2])

    def vecadd(lst_a, lst_b, lst_c):
        for i in range(1024):
            lst_c[i] = lst_a[i] + lst_a[i]

        return [1,3,4,4]

    c = a + b

    d = vecadd(a, b, c)

    # a = np.empty([3,5,7], float)

    return d

if __name__ == "__main__":
    a = np.array([1, 3, 6, 7, 10])
    b = np.array([1, 3, 6, 7, 10, 13])
    c = pl_type_infer(a, b)
    print(c)
