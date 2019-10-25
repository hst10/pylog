
@test
#@top
@hello
def top_func(w, data):
    c = hmap(lambda x: dot(x[-1:2, -1:2], w), data[1:360, 1:240])
    return c


# w = [1, 1, 1]
# data = [1, 1, 1]

# c = top_func(w, data)
