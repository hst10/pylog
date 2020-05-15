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


class PLTyper:
    def __init__(self, args_info):
        self.args_info = args_info

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



    def visit(self, node, config=None):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        visit_return = visitor(node, config)
        if config == "DEBUG":
            print(node.__class__.__name__+": ", node)
        return visit_return

    def generic_visit(self, node, config=None):
        """Called if no explicit visitor function exists for a node."""
        # visit children
        if isinstance(node, PLNode):
            for field, value in self.iter_fields(node):
                self.visit(value, config)
        elif isinstance(node, list):
            for item in node:
                self.visit(item, config)

    ### TODO: visit body, add return_type
    def visit_PLFunctionDef(self, node, config=None):
        if node.decorator_list:
            decorator_names = [e.name if isinstance(e, PLVariable) \
                               else e.func.name for e in node.decorator_list]
            if "pylog" in decorator_names:
                for arg in node.args:
                    type_name, shape = self.args_info[arg.name]
                    arg.pl_type  = PLType(ty=np_pl_type_map(type_name),
                                          dim=len(shape))
                    arg.pl_shape = shape

    def visit_PLConst(self, node, config=None):
        node.pl_type  = PLType(ty=type(node.value).__name__, dim=0)
        node.pl_shape = (0,)
        node.pl_ctx   = {} # no need to maintain context

        return node.pl_type, node.pl_shape, node.pl_ctx

    def visit_PLArray(self, node, config=None):
        pass

    def visit_PLArrayDecl(self, node, config=None):
        node.pl_type  = PLType(ty=node.ele_type, dim=len(node.dims))
        node.pl_shape = tuple(node.dims)

        node.pl_ctx   = copy.deepcopy(config['context']) \
                                 if ((config is not None) and \
                                     ('context' in config)) else {}
        node.pl_ctx[f'{node.name}'] = (node.pl_type, node.pl_shape)

        return node.pl_type, node.pl_shape, node.pl_ctx

    def visit_PLVariable(self, node, config=None):
        pass
