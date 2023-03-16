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




@pylog(mode='cgen,debug')
def tryip():

    #c = [12.1,1,1]
  #  n = np.empty((2,), int)
  #  v = np.empty((3,), int)

  #  np.testip(n,c)
  #  np.testip(v,c)

    x = np.empty((8,), int)
    y = np.empty((8,1), int)    
    z = np.empty((8,), int)
    a = np.empty((8,), int)    
    b = np.empty((8,16), int)
    c = np.empty((16,1), int)

    for i in range(8):
        x[i] = np.argmax(a)
        a[i] = 0
    np.matmul(b,c,y)
    z = x+y

if __name__ == "__main__":
    z = np.empty((8,), int)
    tryip()