import numpy as np
from pylog import *

# @pylog(mode='debug')
# def pl_fixed_types(lst_a, lst_b):

#     # a = pl_fixed(16, 3)

#     # b = pl_int8(25)

#     c = np.empty((3,), float)

#     # d = np.empty((3,), pl_fixed(8, 3))

#     # e = np.empty((3,), pl_int8)


# if __name__ == "__main__":
#     a = np.array([1, 3, 6, 7, 10])
#     b = np.array([1, 3, 6, 7, 10])
#     pl_fixed_types(a, b)
#     print(c)




@pylog(mode='debug')
def pl_fixed_types():

    c = [12.1,1,1]
    n = np.empty((2,), int)
    v = np.empty((3,), int)

    np.testip(n,c)
    np.testip(v,c)

if __name__ == "__main__":
    pl_fixed_types()