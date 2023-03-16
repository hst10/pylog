import numpy as np
from pylog import *

@pylog(mode='cgen,debug')
def pl_map(w, data):

    # c = w + 12
    # c = data + 1
    # c = plmap(lambda x: x + 1, data)

    # c = plmap(lambda x, y: x[1,-2,-2,1]+y[0,-2,-3], w[5,3,2,2], data[5,5,100])
    # c = plmap(lambda x, y: x[1,-2,-2,1]+y[0,-2,-3], w[1:5,3,2,2], data[1:5,5,100])
    # c = plmap(lambda x, y: dot(x[-1:5:2,-2,-2,1], y[-2:4:2,-2,-3]), w[1:5,3,2,2], data[1:5,5,100])

    # c = plmap(lambda x: dot(x[-1:2, -1:2, 0:16], w[:,:,:,1]), data[1:360:2, 1:240:2, 0])
    # c = plmap(lambda x: dot(x[-1:2, -1:2, 0:16], w[:,:,:,1]), data[1:360:2, 1:240:2, 0])
    # c = data + 1
    c = plmap(lambda x: dot(x[-1:2, -1:2, 0:16], w[:,:,:,1]), data[1:360:2, 1:240:2, 0])
    # c = plmap(lambda x: dot(x[-1:2, -1:2, 0:16], w[:,:,:,1]), data[1:360:2, 1:240:2, 0])
    # c = plmap(lambda x: dot(x[-1:2, -1:2, 0:16], w[:,:,:,1]), data[1:360:2, 1:240:2, 0])
    # c = plmap(lambda x: dot(x[-1:2, -1:2, 0:16], w), data[1:360, 1:240, 0])

if __name__ == "__main__":
    w    = np.random.uniform(size=(3, 3, 16, 32))
    data = np.random.uniform(size=(360, 240, 16))
    pl_map(w, data)
