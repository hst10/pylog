#!/usr/bin/python3

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

import numpy as np

def pylog(func=None, *, synthesis=True):
    if func is None:
        return functools.partial(pylog, synthesis=synthesis)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        source_func = textwrap.dedent(inspect.getsource(func))
        print(source_func)
        arg_names = inspect.getfullargspec(func).args

        for arg in args:
            assert(isinstance(arg, (np.ndarray, np.generic)))

        arg_info = { arg_names[i]:(args[i].dtype.name, args[i].shape)  for i in range(len(args)) }
        print(arg_info)

        # TODO: the data type and dimension info should also be passed to
        # PyLog compiler. Here we discard them for now.
        if synthesis:
            pylog_compile(source_func, arg_info)
    return wrapper


def pylog_compile(src, arg_info):
    ast_py = ast.parse(src)
    astpretty.pprint(ast_py)

    # add an extra attribute pointing to parent for each node
    make_parent(ast_py) # need to be called before analyzer

    # instantiate passes
    tester   = PLTester()
    analyzer = PLAnalyzer()
    typer    = PLTyper(arg_info)
    codegen  = PLCodeGenerator()

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
    output_file = '/home/shuang91/pylog/output_pylog.c'
    with open(output_file, 'w') as fout:
        fout.write(hls_c)
        print(f"HLS C code written to {output_file}")

if __name__ == "__main__":

    a = np.array([1, 3, 5])
    b = np.array([2, 4, 6])

    @pylog
    def test(a, b):
        return a + b

    test(a, b)
