open_project -reset hls_conv2d
set_top conv2d
add_files conv2d.cpp
# add_files -tb tb_sdnn.cpp

open_solution -reset "solution1"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_1.tcl"
# csim_design
csynth_design
# export_design -format ip_catalog -version "0.042"

open_solution -reset "solution2"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_2.tcl"
# csim_design
csynth_design
# export_design -format ip_catalog -version "0.042"

open_solution -reset "solution3"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_3.tcl"
# csim_design
csynth_design
# export_design -format ip_catalog -version "0.042"

exit

