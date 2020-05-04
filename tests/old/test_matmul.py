from numpy import dot
from numpy import matmul
import numpy as np

a = [[1, 3, 5], [1, 3, 5], [1, 3, 5]]
b = [[2, 4, 6], [2, 4, 6], [2, 4, 6]]
c = dot(a, b)
print(c)

c = np.asarray(a) * np.asarray(b)
print(c)

d = matmul(a, b)
print(d)

d = matmul(a, np.matrix.transpose(np.asarray(b)))
print(d)

e = [ [ dot(a_row, b_row) for b_row in b ] for a_row in a ]
print(e)

