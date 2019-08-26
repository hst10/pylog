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

class LpPostorderVisitor(ast.NodeVisitor):
    def visit(self, node, config=None):
        """Visit a node."""
        # visit children first
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item, config)
            elif isinstance(value, ast.AST):
                self.visit(value, config)
        # visit current node after visiting children (postorder)
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        visit_return = visitor(node, config)
        if config == "DEBUG" and hasattr(node, "lp_data"):
            print(node.__class__.__name__+": ", node.lp_data)
        return visit_return

    def generic_visit(self, node, config=None):
        """Called if no explicit visitor function exists for a node."""
        pass

class LpPreorderVisitor(ast.NodeVisitor):
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

class LpTester(LpPostorderVisitor):
    # pass
    def visit_Assign(self, node, config=None):
        print(type(node))
    def visit_stmt(self, node, config=None):
        print(type(node))

class LpAnalyzer(LpPostorderVisitor):

    def visit_NoneType(self, node, config=None):
        pass

    def visit_Num(self, node, config=None):
        node.lp_data = ConstNode(node)

    def visit_Name(self, node, config=None):
        node.lp_data = VariableNode(node)

    def visit_UnaryOp(self, node, config=None):
        node.lp_data = ConstNode(node)

    def visit_Slice(self, node, config=None):
        node.lp_data = SliceNode(node)

    def visit_ExtSlice(self, node, config=None):
        node.lp_data = SliceNode(node)

    def visit_Subscript(self, node, config=None):
        node.lp_data = VariableNode(node)

    def visit_BinOp(self, node, config=None):
        node.lp_data = BinOpNode(node)

    def visit_arg(self, node, config=None):
        node.lp_data = VariableNode(node)

    def visit_arguments(self, node, config=None):
        node.lp_data = [ e.lp_data for e in node.args ]

    def visit_Lambda(self, node, config=None):
        node.lp_data = LambdaNode(node)

    def visit_Call(self, node, config=None):
        if node.func.id == "hmap":
            node.lp_data = HmapNode(node)


class LpCodeGenerator(ast.NodeVisitor):
    def codegen(self, node, config=None):
        """Visit a node."""
        # visit children first
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.codegen(item, config)
            elif isinstance(value, ast.AST):
                self.visit(value, config)
        # visit current node after visiting children (postorder)
        method = 'codegen_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_codegen)
        visit_return = visitor(node, config)
        if config == "DEBUG" and hasattr(node, "lp_data"):
            print(node.__class__.__name__+": ", node.lp_data)
        return visit_return

    def generic_codegen(self, node, config=None):
        """Called if no explicit visitor function exists for a node."""
        pass

#    def codegen_

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

    print("Top module type: ", type(ast_py))

    analyzer = LpAnalyzer()
    tester   = LpTester()

    analyzer.visit(ast_py)
    tester.visit(ast_py)

    print("Input code: ")
    print(src)
