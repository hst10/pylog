#!/usr/bin/python3

import os
import sys
import ast
import astpretty
import re
import inspect
import textwrap
import functools
import subprocess

from visitors import *
from analyzer import *
from typer    import *
from codegen  import *
from sysgen   import *
from runtime  import *

import numpy as np

HOST_ADDR   = 'shuang91@192.168.0.108'
HOST_BASE   = '/home/shuang91/vivado_projects/pylog_projects'
TARGET_ADDR = 'xilinx@192.168.0.118'
TARGET_BASE = '/home/xilinx/pylog_projects'
WORKSPACE   = HOST_BASE

def pylog(func=None, *, mode='cgen', path=WORKSPACE, board='ultra96'):
    if func is None:
        return functools.partial(pylog, mode=mode, path=path, board=board)

    code_gen   = ('cgen' or 'codegen') in mode
    hwgen      = 'hwgen' in mode
    pysim_only = 'pysim' in mode
    deploy     = ('deploy' or 'run' or 'acc') in mode
    debug      = 'debug' in mode
    timing     = 'timing' in mode
    viz        = 'viz' in mode

    if pysim_only:
        return func

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        source_func = textwrap.dedent(inspect.getsource(func))
        if debug: print(source_func)
        arg_names = inspect.getfullargspec(func).args

        for arg in args:
            assert(isinstance(arg, (np.ndarray, np.generic)))

        arg_info = {}

        for i in range(len(args)):
            if args[i].dtype.fields is not None:
                key_fields = ''.join(args[i].dtype.fields.keys())
                m1 = re.search('total([0-9]*)bits', key_fields)
                m2 = re.search('dec([0-9]*)bits', key_fields)
                type_name = f'ap_fixed<{m1.group(1)}, {m2.group(1)}>'
            else:
                type_name = args[i].dtype.name

            arg_info[arg_names[i]] = (type_name, args[i].shape)


        # arg_info = { arg_names[i]:(args[i].dtype.name, args[i].shape) \
        #                                           for i in range(len(args)) }

        num_array_inputs = sum(len(val[1])!=1 for val in arg_info.values())

        project_path, top_func, max_idx = pylog_compile(source_func, arg_info,
                                                        path=path, debug=debug,
                                                        viz=viz)

        config = {
            'workspace_base': WORKSPACE,
            'project_name': top_func,
            'project_path': project_path,
            'freq':         125.00,
            'top_name':     top_func,
            'num_bundles':  max_idx,
            'timing':       timing,
            'board':        board
        }

        if hwgen:
            print("generating hardware ...")

            plsysgen = PLSysGen(board=board)
            plsysgen.generate_system(config)

        if deploy:
            process = subprocess.call(f"mkdir -p {TARGET_BASE}/{top_func}/", \
                                      shell=True)

            bit_file = f'{top_func}/{top_func}_{board}.bit'
            hwh_file = f'{top_func}/{top_func}_{board}.hwh'

            if not os.path.exists(f'{TARGET_BASE}/{bit_file}'):
                process = subprocess.call(f"scp -r {HOST_ADDR}:{HOST_BASE}/"+\
                                          f"{bit_file} " + \
                                          f"{TARGET_BASE}/{top_func}/", \
                                          shell=True)
            if not os.path.exists(f'{TARGET_BASE}/{hwh_file}'):
                process = subprocess.call(f"scp -r {HOST_ADDR}:{HOST_BASE}/"+\
                                          f"{hwh_file} " + \
                                          f"{TARGET_BASE}/{top_func}/",
                                          shell=True)

            plrt = PLRuntime(config)
            plrt.call(args)

    return wrapper


def pylog_compile(src, arg_info, path=HOST_BASE, debug=False, viz=False):
    ast_py = ast.parse(src)
    if debug: astpretty.pprint(ast_py)

    # add an extra attribute pointing to parent for each node
    make_parent(ast_py) # need to be called before analyzer

    # instantiate passes
    tester   = PLTester()
    analyzer = PLAnalyzer(debug=debug)
    typer    = PLTyper(arg_info, debug=debug)
    codegen  = PLCodeGenerator(arg_info, debug=debug)

    # execute passes
    if debug:
        tester.visit(ast_py)

    pylog_ir = analyzer.visit(ast_py)

    if debug:
        print(pylog_ir)

    typer.visit(pylog_ir)

    hls_c = codegen.codegen(pylog_ir)

    if debug:
        print("Generated C Code:")
        print(hls_c)

    project_path = f'{path}/{analyzer.top_func}'

    if not os.path.exists(project_path):
        os.makedirs(project_path)
    # else:
    #     print(f"Directory {project_path} exists! Overwriting... ")

    output_file = f'{project_path}/{analyzer.top_func}.cpp'
    with open(output_file, 'w') as fout:
        fout.write(hls_c)
        print(f"HLS C code written to {output_file}")

    if viz:
        import pylogviz
        pylogviz.show(src, pylog_ir)


    return project_path, analyzer.top_func, codegen.max_idx

if __name__ == "__main__":

    a = np.array([1, 3, 5])
    b = np.array([2, 4, 6])

    @pylog
    def test(a, b):
        return a + b

    test(a, b)

def pl_fixed(total_bits, dec_bits):
    return np.dtype([(f'total{total_bits}bits', np.int32), \
                     (f'dec{dec_bits}bits', np.int32)])
