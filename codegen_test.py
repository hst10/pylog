#!/usr/bin/python3

import pycgen as c
from utils import *
from nodes import *

import sys
import copy
import ast
import astunparse
import astpretty

def debug_print(*args, **kwargs):
    print(*args, **kwargs)

def gen_for_loop(size, id, loop_body): 
    assert(isinstance(size, int))
    loop = c.For(
        "int %s = 0" % id, 
        "%s < " % id + str(size), 
        "%s++" % id,
        c.Block([ c.Statement(loop_body) ])
    )
    return loop

def inst_lambda(lambda_node, param2arg, id):
    assert(isinstance(lambda_node, ast.Lambda))
    lambda_body_str = astunparse.unparse(lambda_node.body).strip()
    print("lambda_body_str = ", lambda_body_str)
    for param, arg in param2arg.items():
        lambda_body_str = lambda_body_str.replace(param, arg + "[%s]" % id)
    return lambda_body_str

# def get_size(data):
#     if isinstance(data, ast.Subscript):
#         if isinstance(data.slice, ast.Slice):
#             lower = 0 if data.slice.lower == None else data.slice.lower.n
#             upper = 

#             return 
#         elif 
#         return


class ASTEditor(ast.NodeTransformer):
    def visit_Subscript(self, subscript_nd):
        binary_op = ast.BinOp(
            left = ast.copy_location(ast.Name(id='i', ctx=subscript_nd.ctx), subscript_nd),
            op = ast.Add(), 
            right = subscript_nd.value
            )
        return ast.copy_location(ast.Subscript(
            value=binary_op,
            slice=subscript_nd.slice,
            ctx=subscript_nd.ctx
        ), subscript_nd)

class CodegenConfig:
    hmap = False


class LogicPy(ast.NodeVisitor):
    def __init__(self):
        self.logic_ast = c.Block()
        self.array_sizes = {}
        self.funcs = {}

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

    def codegen_hmap(self, assign_nd, config=None):
        target_id = assign_nd.targets[0].id
        assert(isinstance(assign_nd.value, ast.Call))
        call_nd = assign_nd.value
        print('Found hyper map call. ')
        arg_ids = [ call_nd.args[i].id if isinstance(call_nd.args[i], ast.Name) 
                    else call_nd.args[i].value.id for i in range(1, len(call_nd.args))]
        print("arg_ids = ", arg_ids)
        # map_size = self.array_sizes[arg_ids[0]]
        param_ids = []
        hmap_op = call_nd.args[0]
        loop_idx = 'i'

        if isinstance(hmap_op, ast.Lambda):
            param_ids = [ elem.arg for elem in hmap_op.args.args]
            param2arg = dict(zip(param_ids, arg_ids))
            loop_body = target_id + "[%s] = " % loop_idx + inst_lambda(hmap_op, param2arg, loop_idx)

            print("loop_body = ", loop_body)

            hmap_op = ASTEditor().visit(hmap_op)

            new_loop_body = target_id + "[%s] = " % loop_idx + inst_lambda(hmap_op, param2arg, loop_idx)

            print("new_loop_body = ", new_loop_body)

            
        #     loop = gen_for_loop(map_size, loop_idx, loop_body)
        #     self.logic_ast.append(loop)

    def codegen_map(self, assign_nd, config=None):
        target_id = assign_nd.targets[0].id
        assert(isinstance(assign_nd.value, ast.Call))
        call_nd = assign_nd.value
        print('Found map call. ')
        arg_ids = [ call_nd.args[i].id if isinstance(call_nd.args[i], ast.Name) 
                    else call_nd.args[i].value.id for i in range(1, len(call_nd.args))]
        print("arg_ids = ", arg_ids)
        map_size = self.array_sizes[arg_ids[0]]

        param_ids = []
        map_op = call_nd.args[0]

        loop_idx = 'i'

        if isinstance(map_op, ast.Lambda):
            param_ids = [ elem.arg for elem in map_op.args.args]
            param2arg = dict(zip(param_ids, arg_ids))
            loop_body = target_id + "[%s] = " % loop_idx + inst_lambda(map_op, param2arg, loop_idx)
            
            loop = gen_for_loop(map_size, loop_idx, loop_body)
            self.logic_ast.append(loop)

        if isinstance(map_op, ast.Name):
            map_op = self.funcs[map_op.id]
            param_ids = [ elem.arg for elem in map_op.args.args]
            ## TODO: Add support for map with pre-defined functions 


    def visit_FunctionDef(self, node, config=None):
        self.funcs[node.name] = node

    def visit_Assign(self, node, config=None):
        target_id = node.targets[0].id

        print("type of assign node", type(node))

        if isinstance(node.value, ast.List):
            self.array_sizes[target_id] = len(node.value.elts)
            print('Found list: %s, %d' % (target_id, self.array_sizes[target_id]))

        if isinstance(node.value, ast.Call):
            call_nd = node.value
            if call_nd.func.id == "hmap":
                self.codegen_hmap(node)

            if call_nd.func.id == "map": 
                self.codegen_map(node)

    def codegen(self):
        print(self.logic_ast)


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
