#!/usr/bin/python3

import pycgen as c

import sys
import copy
import ast
import astunparse
import astpretty

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
    for param, arg in param2arg.items():
        lambda_body_str = lambda_body_str.replace(param, arg + "[%s]" % id)
    return lambda_body_str

class LogicPy(ast.NodeVisitor):
    def __init__(self):
        self.logic_ast = c.Block()
        self.array_sizes = {}
        self.funcs = {}

    def visit_FunctionDef(self, node):
        self.funcs[node.name] = node

    def visit_Assign(self, node):
        target_id = node.targets[0].id

        if isinstance(node.value, ast.List):
            self.array_sizes[target_id] = len(node.value.elts)
            print('Found list: %s, %d' % (target_id, self.array_sizes[target_id]))

        if isinstance(node.value, ast.Call):
            call_nd = node.value
            if call_nd.func.id == "map": 
                print('Found function call: ', call_nd.func.id)
                arg_ids = [call_nd.args[i].id for i in range(1, len(call_nd.args))]

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

    def codegen(self):
        print(self.logic_ast)

if __name__ == "__main__":
    if len(sys.argv) < 2: 
        print("Usage: %s test.py" % __file__ )
    src_file = open(sys.argv[1])
    src = src_file.read()
    src_file.close()

    ast_py = ast.parse(src)
    astpretty.pprint(ast_py)

    gen_inst = LogicPy()
    gen_inst.visit(ast_py)

    print("Input code: ")
    print(src)
    print("Output code: ")
    gen_inst.codegen()
