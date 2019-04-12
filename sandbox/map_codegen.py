
import pycgen as c

import sys
import copy
import ast
import astunparse
import astpretty

func = c.FunctionBody(
    c.FunctionDeclaration(c.Const(c.Pointer(c.Value("char", "greet"))), []),
    c.Block([
        c.Statement('return "hello world"')
        ])
    )

loop = c.For(
    "int i = 0", 
    "i < 100", 
    "i++",
    c.Block([
        c.Statement('return "hello world"')
        ])
    )

print(func)
print(loop)

def foo(f, array):
    return [f(x) for x in array]

result = foo(lambda x: x**2, [1, 2, 3, 4])
print(result)



source_code_1 = """
def my_kernel(A, n):
    for i in range(n):
        for j in range(n):
            A[i,j] = i + j
"""

source_code_2 = """
# def add_one(x):
#     return x + 1

map(lambda x, y: x+y, [9, 1, 4])
# map(add_one, [9, 1, 4])
"""

source_code_3 = """
a = [321, 123, 32]
b = [[1, 1], [1, 0]]
map(lambda x: x[-1] + x[0] + x[1], a)
"""

source_code_4 = """
def foo(m, n):
    return m + n
a = [321, 123, 32]
b = [1, 3, 4]
c = map(lambda x, y: x+y, a, b)
# c = map(foo, a, b)
"""

# ast_1 = ast.parse(source_code_1)
# ast_2 = ast.parse(source_code_2)
ast_3 = ast.parse(source_code_4)

# astpretty.pprint(ast_1)
# astpretty.pprint(ast_2)
astpretty.pprint(ast_3)

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
    lambda_body_str = astunparse.unparse(lambda_node.body)
    for param, arg in param2arg.items():
        lambda_body_str = lambda_body_str.replace(param, arg + "[%s]" % id)
    return lambda_body_str

class LogicGen(ast.NodeVisitor):
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

a = LogicGen()
a.visit(ast_3)

print(source_code_4)
a.codegen()
