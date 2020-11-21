import random
import time
import sys

if len(sys.argv) < 2:
    exit()

order = int(sys.argv[1])
length = 2**order

a = [random.random() for x in range(length)]
b = [random.random() for x in range(length)]

start = time.time()
c = map(lambda x, y: x+y, a, b)
end = time.time()
print("test1, python, %d, %f" % (order, end - start))
