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

class pylog:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.num_calls = 0

    def __call__(self, *args, **kwargs):
        self.num_calls += 1

        source_func = textwrap.dedent(inspect.getsource(self.func))
        print(source_func)
        arg_names = inspect.getfullargspec(self.func).args

        for arg in args:
            assert(isinstance(arg, (np.ndarray, np.generic)))

        arg_info = { arg_names[i]:(args[i].dtype.name, args[i].shape)  for i in range(len(args)) }
        print(arg_info)

        # TODO: the data type and dimension info should also be passed to
        # PyLog compiler. Here we discard them for now.
        # if self.synthesis:
        self.compile(source_func, arg_info)


    def compile(self, src, arg_info):
        self.ast_py = ast.parse(src)
        astpretty.pprint(self.ast_py)

        # add an extra attribute pointing to parent for each node
        make_parent(self.ast_py) # need to be called before analyzer

        # instantiate passes
        tester   = PLTester()
        analyzer = PLAnalyzer()
        typer    = PLTyper(arg_info)
        codegen  = PLCodeGenerator()

        # execute passes
        tester.visit(self.ast_py)
        pylog_ir = analyzer.visit(self.ast_py)
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

    # # pylog.py can also compile a *.py file that contains
    # # only top function (kernel file)
    # pl = pylog()
    # filename = "./tests/conv.py"
    # if len(sys.argv) < 2: 
    #     print("Usage: %s test.py" % __file__ )
    # else:
    #     filename = sys.argv[1]

    # with open(filename) as src_file:
    #     src = src_file.read()
    #     # assuming src only contains top function and no host code
    #     pl.compile(src)
