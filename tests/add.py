'''
The inputs to the PyLog function should be simply regular NumPy arrays. 
PyLog should be able to get the element data type and array dimensions 
from the input NumPy arrays. 
'''
import sys
import numpy as np

sys.path.insert(1, '/newhdd/logicpy/')
from logicpy import *

@pylog_build
def pl_add(a, b):
    return a + b


if __name__ == "__main__":
    a = np.asarray([1, 3, 6, 7, 10])
    b = np.asarray([1, 3, 6, 7, 10])

    pl_add(a, b)
