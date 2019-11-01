from logicpy import *

@lp_top
def top_func(w, data):
    c = hmap(lambda x: dot(x[-1:2, -1:2], w), data[1:360, 1:240])
    return c

top_func(0, 0)
