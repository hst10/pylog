#!/usr/bin/python3

import os
import sys
import ast
import astpretty
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
WORKSPACE   = TARGET_BASE

def pylog(func=None, *, synthesis=False, pysim_only=False, deploy=False, path=WORKSPACE, board='ultra96'):
    if func is None:
        return functools.partial(pylog, synthesis=synthesis, pysim_only=pysim_only, deploy=deploy, path=path, board=board)

    if pysim_only:
        return func

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        source_func = textwrap.dedent(inspect.getsource(func))
        print(source_func)
        arg_names = inspect.getfullargspec(func).args

        for arg in args:
            assert(isinstance(arg, (np.ndarray, np.generic)))

        arg_info = { arg_names[i]:(args[i].dtype.name, args[i].shape) for i in range(len(args)) }

        num_array_inputs = sum(len(val[1])!=1 for val in arg_info.values())

        project_path, top_func, max_idx = pylog_compile(source_func, arg_info, path)

        config = {
            'workspace_base': WORKSPACE,
            'project_name': top_func,
            'project_path': project_path,
            'freq':         125.00,
            'top_name':     top_func,
            'num_bundles':  max_idx,
        }

        if synthesis:
            print("generating hardware ...")

            plsysgen = PLSysGen(board=board)
            plsysgen.generate_system(config)

        if deploy:
            process = subprocess.call(f"mkdir -p {TARGET_BASE}/{top_func}/", shell=True)

            if not os.path.exists(f'{TARGET_BASE}/{top_func}/{top_func}.bit'):
                process = subprocess.call(f"scp -r {HOST_ADDR}:{HOST_BASE}/{top_func}/{top_func}.bit \
                                           {TARGET_BASE}/{top_func}/", shell=True)
            if not os.path.exists(f'{TARGET_BASE}/{top_func}/{top_func}.hwh'):
                process = subprocess.call(f"scp -r {HOST_ADDR}:{HOST_BASE}/{top_func}/{top_func}.hwh \
                                           {TARGET_BASE}/{top_func}/", shell=True)

            plrt = PLRuntime(config)
            plrt.call(args)

    return wrapper


def pylog_compile(src, arg_info, path=HOST_BASE):
    ast_py = ast.parse(src)
    astpretty.pprint(ast_py)

    # add an extra attribute pointing to parent for each node
    make_parent(ast_py) # need to be called before analyzer

    # instantiate passes
    tester   = PLTester()
    analyzer = PLAnalyzer()
    typer    = PLTyper(arg_info)
    codegen  = PLCodeGenerator(arg_info)

    # execute passes
    tester.visit(ast_py)
    pylog_ir = analyzer.visit(ast_py)
    print(pylog_ir)

    typer.visit(pylog_ir)

    print("Code generation...")
    hls_c = codegen.codegen(pylog_ir)
    # codegen.codegen(self.ast_py)
    print("Generated C Code:")
    print(hls_c)

    project_path = f'{path}/{analyzer.top_func}'

    if not os.path.exists(project_path):
        os.makedirs(project_path)
    else:
        print(f"Directory {project_path} exists! Exiting... ")

    output_file = f'{project_path}/{analyzer.top_func}.cpp'
    with open(output_file, 'w') as fout:
        fout.write(hls_c)
        print(f"HLS C code written to {output_file}")

    return project_path, analyzer.top_func, codegen.max_idx

if __name__ == "__main__":

    a = np.array([1, 3, 5])
    b = np.array([2, 4, 6])

    @pylog
    def test(a, b):
        return a + b

    test(a, b)
