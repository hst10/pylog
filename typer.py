import re
import copy

from utils import *
from nodes import *


class PLType:
    '''Scalars, arrays, and functions'''
    def __init__(self, ty="float", dim=0):
        self.ty = ty
        self.dim = dim

    def __repr__(self):
        return "PLType(" + self.ty + ", " + str(self.dim) + ")"

    def __eq__(self, other):
        if (self.ty == other.ty) and (self.dim == other.dim):
            return True
        else:
            return False
    def __add__(self, other):
        if isinstance(other, int):
            return PLType(self.ty, self.dim+other)
        if self.ty != other.ty:
            return PLType(float, self.dim+other.dim)
        else:
            return PLType(self.ty, self.dim+other.dim)

    def __sub__(self, other):
        if isinstance(other, int):
            return PLType(self.ty, self.dim-other)
        if self.ty != other.ty:
            return PLType(float, self.dim-other.dim)
        else:
            return PLType(self.ty, self.dim-other.dim)

class PLTyper:
    def __init__(self, args_info, debug=False):
        self.args_info = args_info
        self.debug = debug

    def iter_fields(self, node):
        """
        Yield a tuple of ``(fieldname, value)`` for each field in
        ``node._fields`` that is present on *node*.
        """
        for field in node._fields:
            try:
                yield field, getattr(node, field)
            except AttributeError:
                pass

    def visit(self, node, ctx={}):
        """Visit a node."""

        if self.debug:
            print(f'Visiting {node.__class__.__name__}, {node}')

        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        visit_return = visitor(node, ctx)

        return visit_return

    def generic_visit(self, node, ctx={}):
        """Called if no explicit visitor function exists for a node."""
        # visit children
        if isinstance(node, PLNode):
            for field, value in self.iter_fields(node):
                self.visit(value, ctx)
        elif isinstance(node, list):
            for item in node:
                self.visit(item, ctx)

    def visit_PLFunctionDef(self, node, ctx={}):

        node.pl_type  = PLType('pl_func', 0)
        node.pl_shape = None
        ctx[node.name] = (node.pl_type, node.pl_shape, node)
        node.pl_ctx   = copy.deepcopy(ctx)

        local_ctx = copy.deepcopy(ctx)

        if node.pl_top:
            for arg in node.args:
                type_name, shape = self.args_info[arg.name]
                arg.pl_type  = PLType(ty=np_pl_type_map(type_name),
                                      dim=len(shape))
                arg.pl_shape = shape

        node.return_type  = PLType('void', 0)
        node.return_shape = ()

        if all(hasattr(arg, 'pl_type') for arg in node.args):
            for arg in node.args:
                local_ctx[arg.name] = (arg.pl_type, arg.pl_shape, arg)
            for stmt in node.body:
                self.visit(stmt, local_ctx)
                if isinstance(stmt, PLReturn):
                    node.return_type  = stmt.pl_type
                    node.return_shape = stmt.pl_shape

        return node.pl_type, node.pl_shape, node.pl_ctx

    def visit_PLConst(self, node, ctx={}):
        node.pl_type  = PLType(ty=type(node.value).__name__, dim=0)
        node.pl_shape = ()
        node.pl_ctx   = {} # no need to maintain context

        return node.pl_type, node.pl_shape, node.pl_ctx

    def visit_PLArray(self, node, ctx={}):
        dim = len(node.elts)
        if dim == 0:
            node.pl_type  = PLType('None', 0)
            node.pl_shape = ()
        else:
            self.visit(node.elts[0])
            node.pl_type  = node.elts[0].pl_type + 1 # assuming 1D list
            node.pl_shape = (dim,)

    def visit_PLArrayDecl(self, node, ctx={}):
        dims = ()
        for e in node.dims.elts:
            dims += (e.value,)

        node.pl_type  = PLType(ty=node.ele_type, dim=len(dims))
        node.pl_shape = dims

        node.pl_ctx   = copy.deepcopy(ctx)

        # node.name is a PLVariable object
        node.pl_ctx[node.name.name] = (node.pl_type, node.pl_shape, node)
        # if self.debug:
        #     print(type(node).__name__, node.pl_ctx)

        return node.pl_type, node.pl_shape, node.pl_ctx

    def visit_PLVariableDecl(self, node, ctx={}):
        node.pl_type = PLType(ty=node.ty, dim=0)
        node.pl_shape = ()
        node.pl_ctx   = copy.deepcopy(ctx)
        node.pl_ctx[node.name] = (node.pl_type, node.pl_shape, node)

        if self.debug:
            print(type(node).__name__, node.pl_ctx)

        return node.pl_type, node.pl_shape, node.pl_ctx

    def visit_PLVariable(self, node, ctx={}):

        if not hasattr(node, 'pl_type'):
            if node.name in ctx:
                node.pl_type  = ctx[node.name][0]
                node.pl_shape = ctx[node.name][1]
                node.pl_ctx   = {}
            else:
                print(node.name)
                raise NameError

        return node.pl_type, node.pl_shape, node.pl_ctx

    def visit_PLUnaryOp(self, node, ctx={}):
        self.visit(node.operand, ctx)
        node.pl_type  = node.operand.pl_type
        node.pl_shape = node.operand.pl_shape
        node.pl_ctx   = node.operand.pl_ctx

        if self.debug:
            print(type(node).__name__, node.pl_ctx)

        return node.pl_type, node.pl_shape, node.pl_ctx

    def visit_PLBinOp(self, node, ctx={}):
        self.visit(node.op, ctx)
        self.visit(node.left, ctx)
        self.visit(node.right, ctx)

        node.pl_type  = node.left.pl_type
        node.pl_shape = node.left.pl_shape

    def visit_PLAssign(self, node, ctx={}):
        self.visit(node.value, ctx)

        self.is_decl = True

        if not isinstance(node.target, PLSubscript):
            if node.target.name in ctx:
                ctx_type, ctx_shape, _ = ctx[node.target.name]
                if ctx_type  == node.value.pl_type and \
                   ctx_shape == node.value.pl_shape:
                    self.is_decl = False
        else:
            self.is_decl = False

        node.target.pl_type  = node.value.pl_type
        node.target.pl_shape = node.value.pl_shape

        node.pl_type  = node.value.pl_type
        node.pl_shape = node.value.pl_shape

        if self.is_decl:
            ctx[node.target.name] = (node.target.pl_type, \
                                     node.target.pl_shape,\
                                     node)

    def visit_PLReturn(self, node, ctx={}):
        self.visit(node.value, ctx)
        node.pl_type  = node.value.pl_type
        node.pl_shape = node.value.pl_shape
        node.pl_ctx   = ctx

        # if self.debug:
        #     print(type(node).__name__, node.pl_ctx)

        return node.pl_type, node.pl_shape, node.pl_ctx

    def visit_PLFor(self, node, ctx={}):
        node.target.pl_type  = PLType('int', 0)
        node.target.pl_shape = ()

        ctx[node.target.name] = (node.target.pl_type, node.target.pl_shape,\
                                node.target)
        for stmt in node.body:
            self.visit(stmt, ctx)

        node.pl_ctx = copy.deepcopy(ctx)

    def visit_PLWhile(self, node, ctx={}):
        for stmt in node.body:
            self.visit(stmt, ctx)

        node.pl_ctx = copy.deepcopy(ctx)

    def visit_PLIf(self, node, ctx={}):
        for stmt in node.body:
            self.visit(stmt, ctx)

        for stmt in node.orelse:
            self.visit(stmt, ctx)

    def visit_PLIfExp(self, node, ctx={}):
        for stmt in node.body:
            self.visit(stmt, ctx)

        for stmt in node.orelse:
            self.visit(stmt, ctx)

    def visit_PLCall(self, node, ctx={}):
        func_name = node.func.name
        if func_name in ctx:
            func_def_node = ctx[func_name][2]

        else:
            print(f'Function {func_name} called before definition!')
            raise NameError

        for i in range(len(node.args)):
            self.visit(node.args[i], ctx)
            func_def_node.args[i].pl_type  = node.args[i].pl_type
            func_def_node.args[i].pl_shape = node.args[i].pl_shape

        self.visit(func_def_node)

        node.pl_type  = func_def_node.return_type
        node.pl_shape = func_def_node.return_shape

    def visit_PLSubscript(self, node, ctx={}):
        array_name = node.var.name
        subscript_dim = len(node.indices)
        if array_name in ctx:
            dims = ctx[array_name][0].dim
            node.pl_type = ctx[array_name][0] - subscript_dim
            node.pl_shape = ctx[array_name][1][:-subscript_dim]
        else:
            print(f'{array_name} used before definition!')
            raise NameError

    def visit_PLLambda(self, node, ctx={}):
        node.pl_type  = PLType('pl_lambda', 0)
        node.pl_shape = None

        if all(hasattr(arg, 'pl_type') for arg in node.args):
            local_ctx = copy.deepcopy(ctx)
            for arg in node.args:
                local_ctx[arg.name] = (arg.pl_type, arg.pl_shape, arg)
                self.visit(node.body, local_ctx)

