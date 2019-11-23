import sys
from typing import List
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/newhdd/logicpy/')

from logicpy import *

LpArray4D = List[List[List[List[float]]]]
def LpType(ele_type, dim):
    if dim == 0:
        return ele_type
    elif dim == 1:
        return List[ele_type]
    else:
        return List[LpType(ele_type, dim - 1)]


@lp_top
def top_func(w: LpType(float, 4), data: LpType(float, 3)) -> LpType(float, 3):
#    c = hmap(lambda x: dot(x[-1:2, -1:2], w), data[1:360, 1:240]) 
    c = map(lambda wi: 
              hmap(lambda x: 
                dot(x[0:16, -1:2, -1:2], wi), data[0, 1:240, 1:360]),
            w)
    return c

@lp_top
def test(c):
    # c[3]
    c[3, 5, 2:4]
    return 1

top_func(0, 0)
# test(24)

# import numpy as np
# w = np.random.rand(2,3,4)

# data = np.random.rand(2,3,4)

# print(data)
# print(list(map(lambda x: x+1, data[:,:,:])))

# print("original: ", data)

# data1 = [1, 3, 4]
# print("new: ", list(map(lambda x: x+1, data1)))

# # c = [ map(wi, data) for wi in w ]
# c = map(lambda wi: list(map(lambda x: x + wi, data)), w)
# print("new new: ", list(c))
