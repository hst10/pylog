def matmul(a, b, c):
    for i in range(32):
        for j in range(32).unroll(4):
            tmp = 0.
            for k in range(32).pipeline():
                tmp += a[i][k] * b[k][j]
            c[i][j] = tmp
