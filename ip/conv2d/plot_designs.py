#!/usr/bin/python3

import argparse
import matplotlib.pyplot as plt

# example: 
# 0         1    2     3    4        5        6        7        8    9 10 11  12   13
# solution0,4.00,3.500,0.50,20850362,20850362,20850362,20850362,none,2,5,1600,1870,0
# VC709 resources: BRAM_18K, DSP48E, FF, LUT, URAM
#                  2940,    3600,866400,43320, 0

def parse_record(record):
    lst = [ e.strip() for e in record.split(",") ]
    sol_idx = int(lst[0][8:])
    clk     = float(lst[2])
    latency = int(lst[4])
    area_rt = float(lst[9])/2940 + float(lst[10])/3600 + float(lst[11])/866400 + float(lst[12])/433200
    return (sol_idx, clk, latency, area_rt)

parser = argparse.ArgumentParser(description='Plot synthesis results of designs')
parser.add_argument("log_file", action="store", help="Synthesis results in csv format")

args = parser.parse_args()

log_fp = open(args.log_file)
designs = [ parse_record(e) for e in log_fp.readlines() ]

latency = [ e[2] for e in designs ]
clk     = [ e[1] for e in designs ]
area_rt = [ 5000*e[3] for e in designs ]


plt.figure()
plt.scatter(x=latency, y=clk, s=area_rt, alpha=0.3)

# create legend
l1 = plt.scatter([],[], s=50, c='C0', alpha=0.5)
l2 = plt.scatter([],[], s=250, c='C0', alpha=0.5)
l3 = plt.scatter([],[], s=500, c='C0', alpha=0.5)
labels = ["1%", "5%", "10%"]
leg = plt.legend([l1, l2, l3], labels, frameon=True, title='Area', labelspacing=1.5, borderpad=0.8)

plt.show()
