open_project -reset hls_conv2d
set_top conv2d
add_files conv2d.cpp


open_solution -reset "solution0"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_0.tcl"
csynth_design

open_solution -reset "solution1"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_1.tcl"
csynth_design

open_solution -reset "solution2"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_2.tcl"
csynth_design

open_solution -reset "solution3"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_3.tcl"
csynth_design

open_solution -reset "solution4"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_4.tcl"
csynth_design

open_solution -reset "solution5"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_5.tcl"
csynth_design

open_solution -reset "solution6"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_6.tcl"
csynth_design

open_solution -reset "solution7"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_7.tcl"
csynth_design

open_solution -reset "solution8"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_8.tcl"
csynth_design

open_solution -reset "solution9"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_9.tcl"
csynth_design

open_solution -reset "solution10"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_10.tcl"
csynth_design

open_solution -reset "solution11"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_11.tcl"
csynth_design

open_solution -reset "solution12"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_12.tcl"
csynth_design

open_solution -reset "solution13"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_13.tcl"
csynth_design

open_solution -reset "solution14"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_14.tcl"
csynth_design

open_solution -reset "solution15"
set_part {xc7vx690tffg1761-2} -tool vivado
create_clock -period 4
source "./directives_15.tcl"
csynth_design


exit
