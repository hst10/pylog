from env import *

import numpy as np
from pylog import *

'''
The inputs to the PyLog function should be simply regular NumPy arrays. 
PyLog should be able to get the element data type and array dimensions 
from the input NumPy arrays. 
'''


@pylog(mode='debug')
def pl_vecadd(a, b, c):
    for idx in range(len(a)):
        c[idx] = a[idx] + b[idx]


@pylog(mode='debug')
def pl_vecadd2(a, b, c):
    c = a + b
    d = a + c


# @pylog(mode='debug, viz')
# def pl_vecadd3(a, b, c):
#    c=map(lambda x:x,b)

@pylog(mode='debug')
def pl_vecadd4(a, b, c):
    c[:15] = a[:15] + b[15:30]


if __name__ == "__main__":
    length = 1024
    a = np.random.rand(length).astype(pl_fixed(16, 6))
    b = np.random.rand(length).astype(pl_fixed(8, 3))
    c = np.random.rand(length).astype(pl_fixed(8, 4))
    # a = np.random.rand(length).astype(np.float32)
    # b = np.random.rand(length).astype(np.float32)
    # c = np.random.rand(length).astype(np.float32)

    # print("original arrays: ")
    # print(a)
    # print(b)
    # print(c)

    # pl_vecadd(a, b, c)
    # pl_vecadd2(a, b, c)
    pl_vecadd(a, b, c)
    pl_vecadd2(a, b, c)
    pl_vecadd4(a, b, c)
    # print("result arrays: ")
    # print(a)
    # print(b)
    # print(c)
