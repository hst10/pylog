def foo(m, n):
    return m + n
a = [321, 123, 32]
b = [1, 3, 4]
c = map(lambda x, y: x+y, a, b)
# c = map(foo, a, b)
