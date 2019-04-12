
import numpy as np

a = [[1, 3], [2, 4]]
b = [[1, 3], [2, 4]]

c = map(lambda x, y: x + y, a, b)

print(c)

np_a = np.array(a)
np_b = np.array(b)

np_c = map(lambda x, y: x + y, np_a, np_b)
print(np_c)
