#!/usr/bin/python

import sys

if len(sys.argv) < 2:
    exit()

fin = open(sys.argv[1])
fout = open("processed_" + sys.argv[1], "w")
lines = fin.readlines()

test_name = ""
total_time = 0.0

for line in lines:
    lst = line.strip().split(",")
    name = ",".join(lst[0:3])

    if (name != test_name) and (test_name != ""):
        time = total_time / 5
        fout.write(test_name + ", " + str(time) + "\n")
        total_time = float(lst[3])
        test_name = name
    else:
        total_time += float(lst[3])
        test_name = name

time = total_time / 5
fout.write(test_name + ", " + str(time) + "\n")