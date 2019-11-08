import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/newhdd/logicpy/')

from logicpy import *

@lp_top
def top_func(w, data):
    c = hmap(lambda x: dot(x[-1:2, -1:2, 0:16], w), data[1:360, 1:240, 0])
    return c

top_func(0, 0)
