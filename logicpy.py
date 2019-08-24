#!/usr/bin/python3

import pycgen as c
from utils import *
from nodes import *
import visitors

import sys
import copy
import ast
import astunparse
import astpretty

class ast_visitor_test(ast.NodeVisitor):
    def visit(self, node, config=None):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, config)

    def generic_visit(self, node, config=None):
        """Called if no explicit visitor function exists for a node."""
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item, config)
            elif isinstance(value, ast.AST):
                self.visit(value, config)

    def visit_Name(self, node, config=None):
        print("found Name node: ", node.id)
        print("Type: ", type(node))
        if config != None:
            print("MESSAGE = ", config)
        print("Parent = ", node.parent)
        return node.id
    def visit_BinOp(self, node, config=None):
        print("BinOp, type: ", type(node))
        ret = self.visit(node.left, "Hello!!! ")

def make_parent(root):
    for node in ast.walk(root):
        for child in ast.iter_child_nodes(node):
            child.parent = node

if __name__ == "__main__":
    if len(sys.argv) < 2: 
        print("Usage: %s test.py" % __file__ )
        # src_file = open("./tests/test2.py")
        src_file = open("./tests/test_conv_2d.py")
    else:
        src_file = open(sys.argv[1])
    src = src_file.read()
    src_file.close()

    ast_py = ast.parse(src)
    astpretty.pprint(ast_py)

    make_parent(ast_py)

    print(type(ast_py))

    # gen_inst = LogicPy()
    # gen_inst.visit(ast_py)

    # print("Input code: ")
    # print(src)
    # print("Output code: ")
    # gen_inst.codegen()

    print("Testing AST visitor: ")

    ast_visitor_test_inst = ast_visitor_test()
    ast_visitor_test_inst.visit(ast_py)
