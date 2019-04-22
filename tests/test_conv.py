import numpy as np

data = np.random.rand(10)

def conv(x):
    return x[-1] + x[0] + x[1]

c = hmap(lambda x: x[-1] + x[0] + x[1], data[1:9])

