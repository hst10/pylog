#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import numpy as np
import hashlib
import inspect

DESIGN_LIB = "/home/shuang91/vivado_projects/pylog_designs/"

class LogicInstance:
    def __init__(self, key=None):
        self.key = key


def load_design_keys(filename="design_keys"):
    fin = open(DESIGN_LIB+filename)
    keys = fin.read().strip().splitlines()
    fin.close()
    return keys

def pylog_go(func):

    def wrap_func(*args, **kwargs):
        source_func = inspect.getsource(func)
        for arg in args:
            assert(isinstance(arg, (np.ndarray, np.generic)))
            print(arg, type(arg))
        design_key = hashlib.md5(source_func.encode("UTF-8"))
        existing_keys = load_design_keys()
        if design_key in existing_keys:

        else:
            Print("Design doesn't exist. Need to run synthesis first. ")

    return wrap_func


@pylog_go
def pl_add(a, b):
    return a + b

if __name__ == "__main__":
    a = np.asarray([1, 3, 6, 7, 10])
    b = np.asarray([1, 3, 6, 7, 10])

    key = pl_add(a, b)
    print(key.hexdigest())
