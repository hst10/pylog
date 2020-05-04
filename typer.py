from nodes import *


pytypes = {"None": None, "bool": bool, "int": int, "float": float, "str": str}


class PLType:
    '''Scalars, arrays, and functions'''
    def __init__(self, ele_type=float, dim=0):
        self.ele_type = ele_type
        self.dim = dim

    def __repr__(self):
        return "PLType(" + self.ele_type + ", " + str(self.dim) + ")"

    def __eq__(self, other):
        if (self.ele_type == other.ele_type) and (self.dim == other.dim):
            return True
        else:
            return False
    def __add__(self, other):
        if isinstance(other, int):
            return PLType(self.ele_type, self.dim+other)
        if self.ele_type != other.ele_type:
            return PLType(float, self.dim+other.dim)
        else:
            return PLType(self.ele_type, self.dim+other.dim)




class PLTyper:
    def __init__(self, args_info):
        self.args_info = args_info

    def iter_fields(self, node):
        """
        Yield a tuple of ``(fieldname, value)`` for each field in ``node._fields``
        that is present on *node*.
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
