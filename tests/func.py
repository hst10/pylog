
@test
#@top
@hello
@xixi
def top(w, data):
    c = hmap(lambda x: dot(x[-1:2, -1:2], w), data[1:360, 1:240])
    return c
