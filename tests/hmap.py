import sys
sys.path.extend(['/home/shuang91/pylog/'])

import numpy as np
from pylog import *

@pylog
def top_func(w, data):
    c = hmap(lambda x: dot(x[-1:2, -1:2, 0:16], w), data[1:360, 1:240, 0])
    return c

if __name__ == "__main__":
    w    = np.random.uniform(size=(32, 16, 3, 3))
    data = np.random.uniform(size=(16, 240, 360))
    c = top_func(w, data)
    print(c)
