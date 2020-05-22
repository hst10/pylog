from env import *

import numpy as np
from pylog import *

@pylog
def top_func(w: LpType(float, 4), data: LpType(float, 3)) -> LpType(float, 3):
#    c = hmap(lambda x: dot(x[-1:2, -1:2], w), data[1:360, 1:240]) 
    c = map(lambda wi: 
              hmap(lambda x: 
                dot(x[0:16, -1:2, -1:2], wi), data[0, 1:240, 1:360]),
            w)
    return c

@pylog
def new_conv_for(c, w, data):
    for i in range(w.shape[0]):
        c[i] = plmap(lambda x:dot(x[0:16, -1:2, -1:2], w[i]), data[0, 1:240, 1:360])

'''
// map: iterate through w
for (int i0 = 0; i0 < w.dim[0]; i0++)
{
    float ***wi = w[i0]; 

    // hmap: iterate through data, 2D
    for (int i1 = 1; i1 < 240; i1++)
    {
        for (int i2 = 1; i2 < 360; i2++)
        {
            float ***x = data; 
            // dot
            float tmp = 0.0; 
            for (int i3 = 0; i3 < w.dim[1]; i3++)
            {
                for (int i4 = 0; i4 < 3; i4++)
                {
                    for (int i5 = 0; i5 < 3; i5++)
                    {
                        tmp += data[i3][i1+(-1)+i4][i2+(-1)+i5] * w[i0][i3][i4][i4]; 
                    }
                }
            }
            c[i0][i1-1][i2-1] = tmp; 
        }
    }
}
'''

@pylog
def add(a, b):
    c = map(lambda x, y: x+y, a, b)
    return c


@pylog
def test(c):
    # c[3]
    c[3, 5, 2:4]
    return 1


w    = np.random.uniform(size=(32, 16, 3, 3))
data = np.random.uniform(size=(16, 240, 360))

# top_func(w, data)
a = np.random.uniform(size=(32))
b = np.random.uniform(size=(32))
# add(a, b)


# test(24)
