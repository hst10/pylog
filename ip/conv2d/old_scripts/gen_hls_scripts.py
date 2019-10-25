#!/usr/bin/python3

import jinja2
import itertools
from operator import add

def gen_directives_tcl(top_func, interface_lst, loop_lst, loop_directive_lst):
    interface_dir = "set_directive_interface -mode m_axi -offset slave " + top_func + " "
    src = "\n".join([ interface_dir+e for e in interface_lst ])
    space = list(itertools.product(loop_directive_lst, repeat=len(loop_lst)))
    loop_directives = [ list(map(add, tp, loop_lst)) for tp in space ]

    num_designs = len(loop_directives)
    
    for i in range(len(loop_directives)):
        dir_src = src + "\n\n" + "\n".join(loop_directives[i])
        dtcl_fp = open("directives_"+str(i)+".tcl", "w")
        dtcl_fp.write(dir_src)
        dtcl_fp.close()

    return num_designs

def gen_hls_tcl(top_func, num_designs):
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "run_hls.tcl.jinja"
    template = templateEnv.get_template(TEMPLATE_FILE)
    outputText = template.render(top_func=top_func, num_designs=num_designs)  # this is where to put args to the template renderer

    print(outputText, file=open("run_hls.tcl", "w"))

top_func = "conv2d"
interface_lst = ['data', 'w', 'c']
loop_lst = ['conv2d/hmap_i1', 'conv2d/hmap_i2', 'conv2d/dot_i4', 'conv2d/dot_i5']
loop_directive_lst = ['set_directive_pipeline ', 'set_directive_unroll ']

num_designs = gen_directives_tcl(top_func, interface_lst, loop_lst, loop_directive_lst)
gen_hls_tcl(top_func, num_designs)
print("Number of design points: ", num_designs)