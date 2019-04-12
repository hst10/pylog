from functools import *

val = [1, 2, 3, 4, 5, 6]
print list(map(lambda x: x * 2, val))
print map(lambda x: x * 2, val)

def power(base, exp):
    return base ** exp
cube = partial(power, exp=3)

print map(cube, val)
# print cube(5)  # returns 125

def dotprod(A, B):
    

def map():


def conv(filter, fmap):
    map(partial(dotprod, B=filter), fmap[:, :, 0])
    return fmap_out


def matmul(A, B):
    
    return C


