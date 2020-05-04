a = [6, 8, 0, 6, 1, 2, 8, 5, 4, 5]
b = [1, 3, 4, 6, 8, 0, 6, 1, 2, 5]
c = [2, 3, 4, 6, 8, 0, 6, 1, 2, 8]
d = [3, 3, 4, 6, 8, 0, 6, 1, 2, 8]

def foo(x):
    return x + 1

def bar(x):
    return x*2

test = map(lambda x: foo(x) + bar(x), a)
print(test)

# result = map(lambda x, y, z, m: x + y * z / m, a, b, c, d)
