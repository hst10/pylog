import random
import time

def foo(m, n):
    return m + n

length = 2**20

a = [random.random() for x in range(length)]
b = [random.random() for x in range(length)]

start = time.time()
c = map(lambda x, y: x+y, a, b)
end = time.time()
print("Execution time: %fs." % (end - start))

# c = map(foo, a, b)
