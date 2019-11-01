#!/bin/bash
for ((i=0; i<81; i=i+1))
do
    ../../parse_hls_report.py ./hls_conv2d/solution$i conv2d --csv >> synth_rpts.log
done
