from forbiddenfruit import curse
import numpy as np

def cursed(pyclass):
    def cursed_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        curse(pyclass, func.__name__, func)
        return wrapper
    return cursed_decorator

@cursed(range)
def pipeline(self):
    return self

@cursed(range)
def unroll(self, factor=None):
    return self

@cursed(range)
def partition(self, factor=None):
    return self

def pragma(str):
    pass
