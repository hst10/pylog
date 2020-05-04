def plmap(func, *argv):
    res = []
    length = len(argv[0])
    for i in range(length):
        res.append(func(argv))
