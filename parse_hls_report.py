#!/usr/bin/python
import sys
from os import path

if len(sys.argv) < 2:
    print("USAGE: parse_hls_report.py {HLS_SYN_DIR}")
    exit(1)

HLS_SYN_DIR = sys.argv[1]

if len(sys.argv) > 2:
    top_func_name = sys.argv[2]
else:
    top_func_name = "sparse_dnn"


if path.exists(HLS_SYN_DIR + "/solution1/syn/report/" + top_func_name + "_csynth.rpt"):
    report_file = HLS_SYN_DIR + "/solution1/syn/report/" + top_func_name + "_csynth.rpt"
elif path.exists(HLS_SYN_DIR + "/syn/report/" + top_func_name + "_csynth.rpt"):
    report_file = HLS_SYN_DIR + "/syn/report/" + top_func_name + "_csynth.rpt"

report_fp = open(report_file)
lines = report_fp.readlines()

report_fp.close()

to_print = ""

for i in range(len(lines)):
    if lines[i].strip() == "+ Timing (ns):":
        to_print += "".join(lines[i:i+7])
    if lines[i].strip() == "+ Latency (clock cycles):":
        to_print += "".join(lines[i:i+8])
    if lines[i].strip() == "== Utilization Estimates":
        to_print += "".join(lines[i-1:i+21])

print(to_print)
