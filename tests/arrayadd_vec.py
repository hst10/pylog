from env import *

import numpy as np
from pylog import *

'''
The inputs to the PyLog function should be simply regular NumPy arrays. 
PyLog should be able to get the element data type and array dimensions 
from the input NumPy arrays. 
'''

@pylog(mode='debug')
def pl_arrayadd21(a, b, c):
    c=a+b

@pylog(mode='debug')
def pl_arrayadd22(a, b, c):
    c[:,:] = a + b

@pylog(mode='debug')
def pl_arrayadd23(a, b, c):
    for idx in range(len(a)):
        c[idx,:]=a[idx,:]+b[idx,:]

@pylog(mode='debug')
def pl_arrayadd_ultimate(a,b,c):
    def dummy_linear_transform(val):
        return val+0.5
    a = c*a + (a+b) * c
    d = 2.5*a*b + b + 1
    #d=dummy_linear_transform(a+b)*dummy_linear_transform(a*b)+1

#@pylog(mode='debug, viz')
#def pl_arrayadd3(a, b, c):
#    c=plmap(lambda x:x+x,b)

if __name__ == "__main__":
    length = 1024
    a = np.random.rand(length,length//2)
    b = np.random.rand(length,length//2)
    c = np.random.rand(length,length//2)

    pl_arrayadd21(a, b, c)
    pl_arrayadd22(a, b, c)
    pl_arrayadd23(a,b,c)
    pl_arrayadd_ultimate(a, b, c)
