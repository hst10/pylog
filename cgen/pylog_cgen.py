
from __future__ import print_function
import sys

# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
sys.path.extend(['.'])

import c_ast
import c_generator
from pylog_cast import *

class CCode:
    def __init__(self):
        self.ast = None
        # Global statements, before top function
        self.global_stmt = []

        # Top function
        self.top = []

    def __add__(self, ast):
        self.append(ast)
        return self

    def append_global(self, ext):
        assert(isinstance(ext, (c_ast.Decl, c_ast.Typedef, c_ast.FuncDef)))
        self.global_stmt.append(ext)

    def append(self, ast):
        assert(isinstance(ast, c_ast.Node))
        self.top.append(ast)

    def update(self):
        self.ast = c_ast.FileAST()
        self.ast.ext = self.global_stmt + self.top

        # # Construct top function
        # self.top = func_def(func_name="pylog_top", 
        #                     args=[], 
        #                     func_type="int", 
        #                     body=[])
        return self.ast

    def show(self):
        self.update()
        self.ast.show(attrnames=True, nodenames=True)

    def cgen(self):
        self.update()
        generator = c_generator.CGenerator()
        return generator.visit(self.ast)



if __name__ == '__main__':
    cc = CCode()
    cc.append_global(var_decl("unit32", "asdfasd", "2454"))
    cc.append_global(array_decl("float16", "boom", [int32(4), int32(2), int32(4)]))

    # arg_1 = var_decl("int", "foo")
    # arg_2 = var_decl("float", "bar")
    # cc.append(func_def("foo", [arg_1, arg_2], "float", body=[arg_1, arg_2]))
    test_asgnm = assignment("+=", var("result"), binop("+", var("accum"), int32("2")))
    sim_for = simple_for("i", int32(0), "<", int32(10), int32(1), stmt_lst=[test_asgnm])
    top = func_def(func_name="pylog_top", 
                   args=[], 
                   func_type="int", 
                   body=[sim_for])
    # cc.append(top)
    cc += top
    cc.show()
    print(cc.cgen())
