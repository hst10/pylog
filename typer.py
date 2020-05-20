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
            return PLType('float', self.dim+other.dim)
        else:
            return PLType(self.ty, self.dim+other.dim)

    def __sub__(self, other):
        if isinstance(other, int):
            return PLType(self.ty, self.dim-other)
        if self.ty != other.ty:
            return PLType('float', self.dim-other.dim)
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
        ctx[node.name.name]         = (node.pl_type, node.pl_shape, node)
        # if self.debug:
        #     print(type(node).__name__, node.pl_ctx)

        return node.pl_type, node.pl_shape, node.pl_ctx

    def visit_PLVariableDecl(self, node, ctx={}):
        node.pl_type = PLType(ty=node.ty, dim=0)
        node.pl_shape = ()
        node.pl_ctx   = copy.deepcopy(ctx)
        node.pl_ctx[node.name] = (node.pl_type, node.pl_shape, node)
        ctx[node.name]         = (node.pl_type, node.pl_shape, node)

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

    def get_slice_length(self, lower=None, upper=None, step=None,
                         total_len=None):
        # assuming all are constants (for now)
        if lower is None:
            lower = 0
        if upper is None:
            if total_len is None:
                return None
            else:
                upper = total_len
        if step is None:
            step = 1
        if total_len is None:
            if (lower < 0) or (upper < 0):
                return None

        if lower < 0:
            if lower < -total_len:
                lower = 0
            else:
                lower += total_len
        elif (total_len is not None) and (lower > total_len):
            lower = total_len


        if upper < 0:
            if upper < -total_len:
                upper = 0
            else:
                upper += total_len
        elif (total_len is not None) and (upper > total_len):
            upper = total_len

        if step < 0:
            if lower > upper:
                return (lower - upper + (-step) - 1)  // (-step)
            else:
                return 0
        else:
            if lower < upper:
                return (upper - lower + step - 1) // step
            else:
                return 0

    def visit_PLSlice(self, node, ctx={}):
        if hasattr(node, 'dim_length'):
            dim_length = node.dim_length
        else:
            dim_length = None

        # visit each field first (constant propagation may happen:
        # expression -> PLConst)
        self.visit(node.lower)
        self.visit(node.upper)
        self.visit(node.step)

        for obj in (node.lower, node.upper, node.step):
            if (obj is not None) and (not isinstance(obj, PLConst)):
                print('RETURN!!! ')
                node.pl_type = PLType('slice', 0)
                node.pl_shape = None
                return

        lower = node.lower.value if node.lower else None
        upper = node.upper.value if node.upper else None
        step  = node.step.value  if node.step  else None

        length = self.get_slice_length(lower=lower,
                                       upper=upper,
                                       step=step,
                                       total_len=dim_length)

        node.pl_type = PLType('slice', 0)
        node.pl_shape = (length,)


    def visit_PLAssign(self, node, ctx={}):
        self.visit(node.value, ctx)

        if not hasattr(node.target, 'pl_type'):
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

        if self.debug:
            print(type(node).__name__, node.pl_ctx)

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

    def actual_shape(self, shape):
        # return a new tuple without 1's tuple
        # (1,4,6,1,1,5) -> (4,6,5) represents the actual shape
        return tuple(i for i in shape if i != 1)

    def visit_PLSubscript(self, node, ctx={}):
        array_name = node.var.name

        if array_name in ctx:
            array_dims  = ctx[array_name][0].dim
            array_shape = ctx[array_name][1]
            decl_node = ctx[array_name][2]
            lambda_arg = hasattr(decl_node, 'lambda_node')

            subscript_dim = len(node.indices)

            if not lambda_arg:
                # allow an extra dimension for bit access
                assert(subscript_dim < (array_dims + 1))
            # node.pl_type = ctx[array_name][0] - subscript_dim
            # node.pl_shape = ctx[array_name][1][:-subscript_dim]

            if subscript_dim == (array_dims + 1):
                # bit access
                # for now only allow accesing a scalar's bits
                # TODO: add support for bit access for arrays
                node.pl_type = PLType('bit', 0)
                npde.pl_shape = ()

            else:
                shape = ()
                indices = node.indices
                is_empty = False
                for i in range(len(indices)):
                    indices[i].parent = node
                    # the length along that dimension
                    indices[i].dim_length = array_shape[i]
                    self.visit(indices[i], ctx)
                    idx_shape = indices[i].pl_shape
                    if idx_shape == (0,):
                        is_empty = True
                    elif idx_shape == ():
                        shape += (1,)
                    else:
                        shape += indices[i].pl_shape

                if is_empty:
                    node.pl_type  = PLType(ctx[array_name][0].ty, None)
                    node.pl_shape = None
                else:
                    valid_dims = len(self.actual_shape(shape))
                    node.pl_type  = PLType(ctx[array_name][0].ty, valid_dims)
                    node.pl_shape = shape

        else:
            print(f'{array_name} used before definition!')
            raise NameError

    def visit_PLLambda(self, node, ctx={}):

        node.pl_type  = PLType('pl_lambda', 0)
        node.pl_shape = None

        if all(hasattr(arg, 'pl_type') for arg in node.args):
            local_ctx = copy.deepcopy(ctx)
            for arg in node.args:
                arg.lambda_node = node

                local_ctx[arg.name] = (arg.pl_type, arg.pl_shape, arg)

            self.visit(node.body, local_ctx)
            node.return_type  = node.body.pl_type
            node.return_shape = node.body.pl_shape

    def visit_PLMap(self, node, ctx={}):

        # assuming target is an existing variable

        self.visit(node.target, ctx)
        for array in node.arrays:
            self.visit(array, ctx)

        iter_dom_type  = node.arrays[0].pl_type
        iter_dom_shape = node.arrays[0].pl_shape
        target_type    = node.target.pl_type
        target_shape   = node.target.pl_shape

        if self.debug:
            print(f'iter_dom_shape: {iter_dom_shape}')

        for array in node.arrays:
            if self.debug:
                print(f'array.pl_shape: {array.pl_shape}')
            assert(self.actual_shape(iter_dom_shape) == \
                   self.actual_shape(array.pl_shape))

        # in plmap, the args of lambda function are all scalars
        # since plmap iterates through each element in arrays
        for i in range(len(node.func.args)):
            elem_type = node.arrays[i].pl_type
            node.func.args[i].pl_type  = PLType(elem_type.ty, 0)
            node.func.args[i].pl_shape = ()

        self.visit(node.func)

        map_return_type  = node.func.return_type + \
                                    len(self.actual_shape(iter_dom_shape))
        map_return_shape = node.func.return_shape + iter_dom_shape

        if self.debug:
            print(f'shape: {map_return_shape}')
            print(f'shape: {target_shape}')

            print(f'actual shape: {self.actual_shape(map_return_shape)}')
            print(f'actual shape: {self.actual_shape(target_shape)}')

            print(f'return type: {map_return_type}')
            print(f'target type: {target_type}')

        assert((self.actual_shape(map_return_shape) == \
                self.actual_shape(target_shape)))

        if self.debug:
            print(f'plmap: return type : {map_return_type}')
            print(f'plmap: return shape: {map_return_shape}')

        node.pl_type  = map_return_type
        node.pl_shape = map_return_shape

