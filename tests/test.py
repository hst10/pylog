import numpy as np
from pylog import *

@pylog(mode='cgen,debug')
def kernel2(a, b, c):

    c = plmap(lambda x, y: x + y, a, b)


@pylog(mode='cgen,debug')
def pl_test(a, b, c):

    c = plmap(lambda x, y: x + y, a, b)

    # def add_one(a, b):
    #     b = a + 1

    # res = 1 + 3
    # res = np.empty([3,5,7], int)

    # # add_one(a, res)
    # d = 1 + 3
    # d = (a + 3.5) * b

   # a = np.empty([3,5,7], int)
   # c = np.empty([3,5,7,9], float)

   # b = 10 + a

   # x = a * b

   # b[:,:,:] = a
  #  c[:,:,:,3] = b

   # a[:,:,:] = 10

   # a = 10

if __name__ == "__main__":
    # a = np.empty([3,5,7,9], float)
    # b = np.empty([3,5,7,9], float)
    # c = np.empty([3,5,7,9], float)

    # a = np.random.uniform(size=(1024, 512))
    # b = np.random.uniform(size=(1024, 512))
    # c = np.random.uniform(size=(1024, 512))
    # pl_test(a, b, c)

    print(PYLOG_KERNELS)
