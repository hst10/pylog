import random
import time
import sys

if len(sys.argv) < 2:
    exit()

order = int(sys.argv[1])
length = 2**order

a = [random.random() for x in range(length)]
b = [random.random() for x in range(length)]
c = [random.random() for x in range(length)]
d = [random.random() for x in range(length)]

start = time.time()
e = map(lambda x, y, z, m: x+y*z/m, a, b, c, d)
end = time.time()
print("test2, python, %d, %f" % (order, end - start))
