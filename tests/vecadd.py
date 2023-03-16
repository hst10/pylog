import numpy as np
from pylog import *

'''
The inputs to the PyLog function should be simply regular NumPy arrays. 
PyLog should be able to get the element data type and array dimensions 
from the input NumPy arrays. 
'''


@pylog(mode='debug, viz', board='pynq-z2')
def pl_vecadd(a, b, c):
    for i in range(1024).pipeline():
        c[i] = a[i] + b[i]


if __name__ == "__main__":
    length = 1024
    # a = np.random.rand(length).astype(pl_fixed(16, 6))
    # b = np.random.rand(length).astype(pl_fixed(8, 3))
    # c = np.random.rand(length).astype(pl_fixed(8, 4))
    a = np.random.rand(length).astype(np.float32)
    b = np.random.rand(length).astype(np.float32)
    c = np.random.rand(length).astype(np.float32)

    # print("original arrays: ")
    # print(a)
    # print(b)
    # print(c)

    pl_vecadd(a, b, c)
    # print("result arrays: ")
    # print(a)
    # print(b)
    # print(c)
