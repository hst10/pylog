# import numpy as np

# data = np.random.rand(10)

data = [23, 43, 23, 5, 65, 23, 23, 43, 23, 5]

# def conv(x):
#     return x[-1] + x[0] + x[1]

# c = hmap(lambda x: x[-1, 0] + x[0, 0] + x[1, 0], data[1:9, :])
# c = hmap(lambda x: x[-1] + x[0] + x[1], data[1:9])
c = hmap(lambda x: x[-1] + x[0] + x[1], data[1:9])
