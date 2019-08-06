import random
import time
import sys

def foo(x, y, z):
    return x + y * z

def bar(x, y, z):
    return x * y * z

if len(sys.argv) < 2:
    exit()

order = int(sys.argv[1])
length = 2**order

a = [random.random() for x in range(length)]
b = [random.random() for x in range(length)]
c = [random.random() for x in range(length)]

start = time.time()
d = map(lambda x, y, z: foo(x, y, z) / bar(x, y, z), a, b, c)
end = time.time()
print("test3, python, %d, %f" % (order, end - start))
