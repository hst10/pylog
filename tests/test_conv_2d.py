
# w = [[0.5, 0, -0.5], [0, 0.5, 0], [1.5, -0.5, 0]] 

c = hmap(lambda x: dot(x[-2:3:2, -2:3:2, -1:2], w), data[1:360:2, 1:240:2, 0:3])
# TODO: support 2D conv with channels: 
# c = hmap(lambda x: dot(x[-2:3:2, -2:3:2, 0:3], w), data[1:360:2, 1:240:2, 0])

# TODO: single dot call
# c = dot(x[-2:3:2, -2:3:2, -1:2], w)
