import random
import time
import sys

if len(sys.argv) < 2:
    exit()

order = int(sys.argv[1])
length = 2**order

a = [random.random() for x in range(length)]
w = [random.random() for x in range(3)]

start = time.time()
b = [a[i-1]*w[0] + a[i]*w[1] + a[i+1]*w[2] for i in range(1, len(a)-1)]
end = time.time()
print("test4, python, %d, %f" % (order, end - start))
