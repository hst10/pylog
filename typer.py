import re

from nodes import *

# pytypes = {"None": None, "bool": bool, "int": int, "float": float, "str": str}
pytypes = ["None", "bool", "int", "float", "str"]


class PLType:
    '''Scalars, arrays, and functions'''
    def __init__(self, ele_type="float", dim=0):
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

    def np_pl_type_map(self, type_name):
        m = re.match('(u?int)([0-9]*)', type_name)
        if m:
            if m.group(2) == '':
                return m.group(1)
            else:
                return f'ap_{m.group(1)}<{m.group(2)}>'

        if type_name.startswith(('int', 'uint')):
            return type_name
        for pltype in pytypes:
            if type_name.startswith(pltype):
                return pltype
        return type_name

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

    def visit_PLFunctionDef(self, node, config=None):
        if node.decorator_list:
            decorator_names = [e.name if isinstance(e, PLVariable) else e.func.name \
                                                     for e in node.decorator_list]
            if "pylog" in decorator_names:
                for arg in node.args:
                    type_name, shape = self.args_info[arg.name]
                    arg.pl_type  = PLType(ele_type=self.np_pl_type_map(type_name), dim=len(shape))
                    arg.pl_shape = shape
