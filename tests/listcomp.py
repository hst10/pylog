import sys
sys.path.extend(['/home/shuang91/pylog/'])

import numpy as np
from pylog import *

@pylog
def listcomp(list_a, list_b):
    c = [a**2 for a in list_a if a+1 for b in list_b if a == b]
    return c

if __name__ == "__main__":
    a = np.array([1, 3, 6, 7, 10])
    b = np.array([1, 3, 6, 7, 10])
    c = listcomp(a, b)
    print(c)
