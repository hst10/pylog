#!/usr/bin/python3

import ast
import astpretty
import inspect

def lp_top(func):
    def wrap_func(*args, **kwargs):
        source_func = inspect.getsource(func)
        print(source_func)

        tree = ast.parse(source_func)
        astpretty.pprint(tree)
    return wrap_func


@lp_top
def conv2d(a, b):
    return a + b

conv2d(2, 4)
