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
from typer import *
from optimizer import *
from codegen   import *
from sysgen    import *
from runtime   import *
import IPinforms
from chaining_rewriter import *

import numpy as np

HOST_ADDR = 'ubuntu@localhost'
HOST_BASE = '/home/ubuntu/vivado_projects/pylog_projects'
TARGET_ADDR = 'ubuntu@localhost'
TARGET_BASE = '/home/ubuntu/vivado_projects/pylog_projects'
WORKSPACE = HOST_BASE


def pylog(func=None, *, mode='cgen', path=WORKSPACE, backend='vhls', \
          board='ultra96', freq=None):
    if func is None:
        return functools.partial(pylog, mode=mode, path=path, \
                                 backend=backend, board=board, freq=freq)

    hwgen = 'hwgen' in mode # hwgen = cgen, hls, syn

    # individual steps
    gen_hlsc = hwgen or ('cgen' in mode) or ('codegen' in mode) # HLS C gen
    run_hls  = hwgen or ('hls' in mode) # run HLS
    run_syn  = hwgen or ('syn' in mode) # run FPGA synthesis

    pysim_only = 'pysim' in mode
    deploy = ('deploy' in mode) or ('run' in mode) or ('acc' in mode)
    debug = 'debug' in mode
    timing = 'timing' in mode
    viz = 'viz' in mode

    if freq is None:
        if (board == 'aws_f1' or board.startswith('alveo')):
            freq = 200.0
        else:
            freq = 100.0

    if pysim_only:
        return func

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        # builtins = open('builtin.py').read()
        source_func = textwrap.dedent(inspect.getsource(func))
        if debug: print(source_func)
        arg_names = inspect.getfullargspec(func).args

        for arg in args:
            assert (isinstance(arg, (np.ndarray, np.generic)))

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

        # num_array_inputs = sum(len(val[1]) != 1 for val in arg_info.values())

        project_path, top_func, max_idx, return_void = pylog_compile(
            src=source_func,
            arg_info=arg_info,
            backend=backend,
            board=board,
            path=path,
            gen_hlsc=gen_hlsc,
            debug=debug,
            viz=viz)

        config = {
            'workspace_base': WORKSPACE,
            'project_name': top_func,
            'project_path': project_path,
            'freq': freq,
            'top_name': top_func,
            'num_bundles': max_idx,
            'timing': timing,
            'board': board,
            'return_void': return_void
        }

        if run_hls or run_syn or hwgen:
            print("generating hardware ...")

            plsysgen = PLSysGen(backend=backend, board=board)
            plsysgen.generate_system(config, run_hls, run_syn)

        if deploy:
            subprocess.call(f"mkdir -p {TARGET_BASE}/{top_func}/", \
                                      shell=True)

            if board == 'aws_f1' or board.startswith('alveo'):

                ext = 'awsxclbin' if (board == 'aws_f1') else 'xclbin'

                xclbin = f'{top_func}/{top_func}_{board}.{ext}'

                if not os.path.exists(f'{TARGET_BASE}/{xclbin}'):
                    subprocess.call(
                        f"scp -r {HOST_ADDR}:{HOST_BASE}/{xclbin} " + \
                        f"{TARGET_BASE}/{top_func}/", shell=True)

            else:

                bit_file = f'{top_func}/{top_func}_{board}.bit'
                hwh_file = f'{top_func}/{top_func}_{board}.hwh'

                if not os.path.exists(f'{TARGET_BASE}/{bit_file}'):
                    subprocess.call(
                        f"scp -r {HOST_ADDR}:{HOST_BASE}/{bit_file} " + \
                        f"{TARGET_BASE}/{top_func}/", shell=True)

                if not os.path.exists(f'{TARGET_BASE}/{hwh_file}'):
                    subprocess.call(
                        f"scp -r {HOST_ADDR}:{HOST_BASE}/{hwh_file} " + \
                        f"{TARGET_BASE}/{top_func}/", shell=True)

            plrt = PLRuntime(config)
            return plrt.call(args)

    return wrapper


def pylog_compile(src, arg_info, backend, board, path,
                  gen_hlsc=True, debug=False, viz=False):
    print("Compiling PyLog code ...")
    ast_py = ast.parse(src)
    if debug: astpretty.pprint(ast_py)

    # add an extra attribute pointing to parent for each node
    ast_link_parent(ast_py)  # need to be called before analyzer

    # instantiate passes
    tester = PLTester()
    analyzer = PLAnalyzer(debug=debug)
    typer = PLTyper(arg_info, debug=debug)
    chaining_rewriter = PLChainingRewriter(debug=debug)
    optimizer = PLOptimizer(backend=backend, debug=debug)
    codegen = PLCodeGenerator(arg_info,
                              backend=backend,
                              board=board,
                              debug=debug)

    # execute passes
    if debug:
        tester.visit(ast_py)

    pylog_ir = analyzer.visit(ast_py)
    plnode_link_parent(pylog_ir)

    if debug:
        print('\n')
        print("pylog IR after analyzer")
        print(pylog_ir)
        print('\n')

    typer.visit(pylog_ir)

    if debug:
        print('\n')
        print("pylog IR after typer")
        print(pylog_ir) 
        print('\n')   
    chaining_rewriter.visit(pylog_ir)

    # transform loop transformation and insert pragmas
    optimizer.opt(pylog_ir)

    if debug:
        print('\n')
        print("pylog IR after optimizer")
        print(pylog_ir) 
        print('\n')  



    project_path = f'{path}/{analyzer.top_func}'

    if not os.path.exists(project_path):
        os.makedirs(project_path)
    # else:
    #     print(f"Directory {project_path} exists! Overwriting... ")


    hls_c = codegen.codegen(pylog_ir, project_path )

    if debug:
        print("Generated C Code:")
        print(hls_c)

    if gen_hlsc:
        output_file = f'{project_path}/{analyzer.top_func}.cpp'
        with open(output_file, 'w') as fout:
            fout.write(hls_c)
            print(f"HLS C code written to {output_file}")

    if viz:
        import pylogviz
        pylogviz.show(src, pylog_ir)

    return project_path, analyzer.top_func, \
           codegen.max_idx, codegen.return_void


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
