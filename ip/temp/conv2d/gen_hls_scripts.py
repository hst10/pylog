#!/usr/bin/python3

import itertools
import os, sys, time
from subprocess import Popen

def gen_hls_tcl(top_func, interface_lst, loop_lst, loop_directive_lst):
    src  = "open_project hls_" + top_func + "\n"
    src += "set_top " + top_func + "\n"
    src += "add_files " + top_func + ".cpp\n"

    space = list(itertools.product(loop_directive_lst, repeat=len(loop_lst)))
    loop_directives = [ list(map(lambda a, b: a+b if a != "" else "", tp, loop_lst)) for tp in space ]

    num_designs = len(loop_directives)

    if not os.path.exists("./tcl_scripts"):
        os.makedirs("tcl_scripts")
    
    for i in range(len(loop_directives)):
        local_src = src + "\n\nopen_solution -reset \"solution" + str(i) + "\"\n"
        local_src += "set_part {xc7vx690tffg1761-2} -tool vivado\n"
        local_src += "create_clock -period 4\n\n"

        interface_dir = "set_directive_interface -mode m_axi -offset slave " + top_func + " "
        local_src += "\n".join([ interface_dir+e for e in interface_lst ])

        local_src += "\n\n" + "\n".join(loop_directives[i])

        local_src += "\ncsynth_design\n"
        local_src += "exit\n"

        dtcl_fp = open("./tcl_scripts/run_hls_"+str(i)+".tcl", "w")
        dtcl_fp.write(local_src)
        dtcl_fp.close()

    return num_designs


def cpu_count():
    ''' Returns the number of CPUs in the system
    '''
    num = 1
    if sys.platform == 'win32':
        try:
            num = int(os.environ['NUMBER_OF_PROCESSORS'])
        except (ValueError, KeyError):
            pass
    elif sys.platform == 'darwin':
        try:
            num = int(os.popen('sysctl -n hw.ncpu').read())
        except ValueError:
            pass
    else:
        try:
            num = os.sysconf('SC_NPROCESSORS_ONLN')
        except (ValueError, OSError, AttributeError):
            pass

    return num

def exec_commands(cmds, max_task=8):
    ''' Exec commands in parallel in multiple process 
    (as much as we have CPU)
    '''
    if not cmds: return # empty list

    def done(p):
        return p.poll() is not None
    def success(p):
        return p.returncode == 0
    def fail():
        sys.exit(1)

    processes = []
    while True:
        while cmds and len(processes) < max_task:
            task = cmds.pop()
            print(task)
            # print(list2cmdline(task))
            processes.append(Popen(task, shell=True))

        for p in processes:
            if done(p):
                if success(p):
                    processes.remove(p)
                else:
                    fail()

        if not processes and not cmds:
            break
        else:
            time.sleep(0.05)


top_func = "conv2d"
interface_lst = ['data', 'w', 'c']
loop_lst = ['conv2d/hmap_i1', 'conv2d/hmap_i2', 'conv2d/dot_i4', 'conv2d/dot_i5']
loop_directive_lst = ['', 'set_directive_pipeline ', 'set_directive_unroll -factor 4 ']

num_designs = gen_hls_tcl(top_func, interface_lst, loop_lst, loop_directive_lst)
print("Number of design points: ", num_designs)

syn_cmds = [ "vivado_hls -f ./tcl_scripts/run_hls_"+str(i)+".tcl" for i in range(num_designs) ]
exec_commands(syn_cmds, cpu_count()-2)
