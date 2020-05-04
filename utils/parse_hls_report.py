#!/usr/bin/python
import sys
from os import path
import argparse

parser = argparse.ArgumentParser(description='HLS report processor')
parser.add_argument("directory", action="store", help="HLS synthesis output directory")
parser.add_argument("top_function", nargs='?', action="store", help="HLS top function name")
parser.add_argument("--csv", action="store_true", help="Print a line of comma separated values")

args = parser.parse_args()
print_csv = args.csv
hls_syn_dir = args.directory
top_func_name = args.top_function

if path.exists(hls_syn_dir + "/solution1/syn/report/" + top_func_name + "_csynth.rpt"):
    report_file = hls_syn_dir + "/solution1/syn/report/" + top_func_name + "_csynth.rpt"
elif path.exists(hls_syn_dir + "/syn/report/" + top_func_name + "_csynth.rpt"):
    report_file = hls_syn_dir + "/syn/report/" + top_func_name + "_csynth.rpt"

report_fp = open(report_file)
lines = report_fp.readlines()

report_fp.close()

screen_print = ""
csv_print = ""

for i in range(len(lines)):
    if lines[i].split(":")[0] == "* Solution":
        screen_print += lines[i]
        csv_print += lines[i].split(":")[1].strip() + ","
    if lines[i].split(":")[0] == "* Target device":
        screen_print += lines[i]
        # csv_print += lines[i].split(":")[1].strip() + ","
    if lines[i].strip() == "+ Timing (ns):":
        screen_print += "".join(lines[i:i+7])
        csv_print += ",".join([ e.strip() for e in lines[i+5].split("|")[2:5] ]) + ","
    if lines[i].strip() == "+ Latency (clock cycles):":
        screen_print += "".join(lines[i:i+8])
        csv_print += ",".join([ e.strip() for e in lines[i+6].split("|")[1:6] ]) + ","
    if lines[i].strip() == "== Utilization Estimates":
        screen_print += "".join(lines[i-1:i+21])
        csv_print += ",".join([ e.strip() for e in lines[i+14].split("|")[2:7] ])

if print_csv:
    print(csv_print)
else:
    print(screen_print)
