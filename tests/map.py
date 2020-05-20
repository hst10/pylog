from env import *

import numpy as np
from pylog import *

@pylog
def pl_map(w, data):
    c = plmap(lambda x: dot(x[-1:2, -1:2, 0:16], w), data[1:360, 1:240, 0])
    return c

if __name__ == "__main__":
    w    = np.random.uniform(size=(32, 16, 3, 3))
    data = np.random.uniform(size=(16, 240, 360))
    c = pl_map(w, data)
    print(c)
