import sys
sys.path.extend(['/home/xilinx/pylog/'])

import numpy as np
from pylog import *

'''
The inputs to the PyLog function should be simply regular NumPy arrays. 
PyLog should be able to get the element data type and array dimensions 
from the input NumPy arrays. 
'''

@pylog(synthesis=False, deploy=True)
def pylog_add(a, b, c):

    for i in range(1024).pipeline():
        c[i] = a[i] + b[i]

    return 0

if __name__ == "__main__":
    length = 1024
    a = np.random.rand(length).astype(np.float32)
    b = np.random.rand(length).astype(np.float32)
    c = np.random.rand(length).astype(np.float32)

    print("original arrays: ")
    print(a)
    print(b)
    print(c)

    pylog_add(a, b, c)
    print("result arrays: ")
    print(a)
    print(b)
    print(c)
