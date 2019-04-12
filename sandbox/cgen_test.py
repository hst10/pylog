
import pycgen as c

import sys
import copy
import ast
import astunparse
import astpretty

# def gen_loop(idx, )

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



source_code_0 = """
def my_kernel(A, n):
    for i in range(n):
        for j in range(n):
            A[i,j] = i + j
"""

source_code = """
def add_one(x):
    return x + 1

map(lambda x, y: x+y, [9, 1, 4])
map(add_one, [9, 1, 4])
"""

source = source_code_0
tree = ast.parse(source)

astpretty.pprint(tree)
# print(ast.dump(tree))

