#!/usr/bin/python3

import os
import sys
import ast
import astpretty
import inspect
import textwrap
import functools

from visitors import *
from analyzer import *
from typer    import *
from codegen  import *
from sysgen   import *

import numpy as np

def pylog(func=None, *, synthesis=True, path='./', board='zedboard'):
    if func is None:
        return functools.partial(pylog, synthesis=synthesis, path=path, board=board)

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

        if synthesis:
            config = {
                'project_name': top_func,
                'project_path': project_path,
                'freq':         125.00,
                'top_name':     top_func,
                'num_bundles':  max_idx,
            }
            plsysgen = PLSysGen(board=board)
            plsysgen.generate_system(config)

    return wrapper


def pylog_compile(src, arg_info, path='./'):
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

    project_path = f'{path}/{analyzer.top_func}/'

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
