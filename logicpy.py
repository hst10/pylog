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
import inspect

class LpPostorderVisitor(ast.NodeVisitor):
    def visit(self, node, config=None):
        """Visit a node."""
        if node == None:
            return None
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
        if node == None:
            return None
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, config)

    def generic_visit(self, node, config=None):
        """Called if no explicit visitor function exists for a node."""
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        return self.visit(item, config)
            elif isinstance(value, ast.AST):
                return self.visit(value, config)

class LpTester(LpPostorderVisitor):
    pass
    # def visit_Assign(self, node, config=None):
    #     print(type(node))
    # def visit_stmt(self, node, config=None):
    #     print(type(node))

class LpAnalyzer(LpPreorderVisitor):

    def __init__(self):
        LpPreorderVisitor.__init__(self)
        self.args = {}

    def isLambdaArg(self, node):
        assert(isinstance(node, ast.Subscript))
        """Check if Subscript node is lambda argument, which represents delta/offset. """
        is_lambda_arg = False
        p_node = node.parent
        while (not isinstance(p_node, ast.Module)):
            if isinstance(p_node, ast.Lambda):
                arg_lst = [elem.arg for elem in p_node.args.args]

                if node.value.id in arg_lst:
                    is_lambda_arg = True
                    break
            p_node = p_node.parent
        return is_lambda_arg

    def visit_NoneType(self, node, config=None):
        pass

    def visit_Num(self, node, config=None):
        node.lp_data = ConstNode(node, config)

    def visit_Name(self, node, config=None):
        node.lp_data = VariableNode(node, config)

    def visit_UnaryOp(self, node, config=None):
        self.visit(node.operand, config)
        node.lp_data = ConstNode(node, config)

    def visit_Slice(self, node, config=None):
        if node.lower:
            self.visit(node.lower, config)
        if node.upper:
            self.visit(node.upper, config)
        if node.step:
            self.visit(node.step, config)
        node.lp_data = SliceNode(node, config)

    def visit_ExtSlice(self, node, config=None):
        for slc in node.dims:
            self.visit(slc)
        node.lp_data = SliceNode(node, config)

    def visit_Subscript(self, node, config=None):
        self.visit(node.value, config)
        self.visit(node.slice, config)

        # # not used
        # if self.isLambdaArg(node):
        #     node.is_delta_node = True
        node.lp_data = VariableNode(node, config)

    def visit_BinOp(self, node, config=None):
        self.visit(node.left, config)
        self.visit(node.right, config)
        node.lp_data = BinOpNode(node, config)

    def visit_arg(self, node, config=None):
        if node.annotation != None:
            self.visit(node.annotation, config)
        node.lp_data = VariableNode(node, config)

    def visit_arguments(self, node, config=None):
        for arg in node.args:
            self.visit(arg, config)
        node.lp_data = [ arg.lp_data for arg in node.args ]

    def visit_Lambda(self, node, config=None):
        self.visit(node.args, config)
        self.visit(node.body, config)
        node.lp_data = LambdaNode(node, config)

    def visit_Call(self, node, config=None):
        self.visit(node.func, config)
        for arg in node.args:
            self.visit(arg, config)

        if node.func.id in {"hmap", "map"}:
            node.lp_data = HmapNode(node, config)
        elif node.func.id == "dot":
            node.lp_data = DotNode(node, config)
        elif node.func.id == "LpType" and len(node.args) == 2 \
            and isinstance(node.args[0], ast.Name) \
            and isinstance(node.args[1], ast.Num):
            node.lp_data = TypeNode(node, config)
            return node.lp_data.type

    def visit_Assign(self, node, config=None):
        for target in node.targets:
            self.visit(target, config)
        self.visit(node.value, config)

    def parse_func_args(self, arg_lst):
        return { arg.arg:self.visit(arg.annotation) for arg in arg_lst }

    def visit_FunctionDef(self, node, config=None):
        self.visit(node.args, config)

        if node.decorator_list:
            decorator_names = [e.id for e in node.decorator_list]
            print(decorator_names)
            if "lp_top" in decorator_names:
                self.top_func = node.name
                if node.args.args:
                    self.args.update(self.parse_func_args(node.args.args))
                    print(self.args)

        if config == None:
            config = LpConfig()
        config.var_list = self.args

        if isinstance(node.body, list):
            for item in node.body:
                if isinstance(item, ast.AST):
                    self.visit(item, config)
        elif isinstance(node.body, ast.AST):
            self.visit(node.body, config)

    def visit_Module(self, node, config=None):
        for stmt in node.body:
            self.visit(stmt)

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
                self.codegen(value, config)
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

    def codegen_Call(self, node, config=None):
        if node.func.id not in {"LpType"}:
            lc = LpConfig(indent_level=3, indent_str="  ", idx_var_num=4)
            lc = LpConfig()
            node.lp_data.codegen(lc)
            print(node.lp_data.src)

def make_parent(root):
    for node in ast.walk(root):
        for child in ast.iter_child_nodes(node):
            child.parent = node

# class lp_top:
#     def __init__(func):
#         self.func = func
#     def __call__(*args, **kwargs):
#         source_func = inspect.getsource(func)
#         print(source_func)
#         logicpy_compile(source_func)

def lp_top(func):
    def wrap_func(*args, **kwargs):
        source_func = inspect.getsource(func)
        print(source_func)
        logicpy_compile(source_func)
    return wrap_func

def logicpy_compile(src):
    ast_py = ast.parse(src)
    astpretty.pprint(ast_py)

    # add an extra attribute pointing to parent for each node
    make_parent(ast_py) # need to be called before analyzer

    # instantiate passes
    analyzer = LpAnalyzer()
    tester   = LpTester()
    codegen  = LpCodeGenerator()

    # execute passes
    analyzer.visit(ast_py)
    tester.visit(ast_py)
    codegen.codegen(ast_py)


if __name__ == "__main__":
    if len(sys.argv) < 2: 
        print("Usage: %s test.py" % __file__ )
        # src_file = open("./tests/test2.py")
        # src_file = open("./tests/test_conv_2d.py")
        src_file = open("./tests/func.py")
    else:
        src_file = open(sys.argv[1])
    src = src_file.read()
    src_file.close()

    logicpy_compile(src)

