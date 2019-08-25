import ast

class Node:
    def __init__(self, ast_node=None):
        self.ast_node = ast_node
        self.name = "LpNode"
    def __repr__(self):
        return str(self.name)

class ConstNode(Node):
    def __init__(self, ast_node=None):
        Node.__init__(self, ast_node)
        self.value = None
        if ast_node != None:
            self.extract(ast_node)

    def __repr__(self):
        if self.value != None:
            return str(self.value)
        else:
            return "ConstNode: Unknown value"

    def extract(self, ast_node):
        if ast_node == None:
            return
        self.ast_node = ast_node
        if isinstance(self.ast_node, ast.Num):
            self.value = self.ast_node.n
        elif isinstance(self.ast_node, ast.UnaryOp):
            if isinstance(self.ast_node.op, ast.USub):
                self.value = -self.ast_node.operand.n
            elif isinstance(self.ast_node.op, ast.UAdd):
                self.value = self.ast_node.operand.n
        else:
            raise NotImplementedError


class SliceNode(Node):
    def __init__(self, ast_node=None):
        Node.__init__(self, ast_node)
        self.slices = []
        self.dim = None
        self.lower = None
        self.upper = None
        self.step  = None
        if ast_node != None:
            self.extract(ast_node)

    def __repr__(self):
        if self.dim == 1:
            return str(self.lower)+":"+str(self.upper)+":"+str(self.step)
        else: 
            return "ExtSlice Content"

    def extract_slice(self, ast_node):
        print(type(ast_node))
        lower = None
        upper = None
        step  = None
        if hasattr(ast_node.lower, "lp_data"):
            lower = ast_node.lower.lp_data.value
        if hasattr(ast_node.upper, "lp_data"):
            upper = ast_node.upper.lp_data.value
        if hasattr(ast_node.step, "lp_data"):
            step = ast_node.step.lp_data.value
        return (lower, upper, step)

    def extract(self, ast_node):
        if ast_node == None:
            return
        self.ast_node = ast_node
        if isinstance(self.ast_node, ast.Slice):
            self.dim = 1
            (self.lower, self.upper, self.step) = self.extract_slice(ast_node)
            self.slices = [(self.lower, self.upper, self.step)]

        elif isinstance(self.ast_node, ast.ExtSlice):
            self.dim = len(self.ast_node.dims)
            self.lower = None
            self.upper = None
            for s in self.ast_node.dims:
                print("type of elem in extslice: ", type(s))
            self.slices = [self.extract_slice(s) for s in self.ast_node.dims]

        else:
            raise NotImplementedError


class VariableNode(Node):
    def __init__(self, ast_node=None, name=None, offset=None, index=None):
        Node.__init__(self, ast_node)
        self.name = name
        self.offset = offset
        self.index = index
        if ast_node != None:
            self.extract(ast_node)

    def __repr__(self):
        return self.name

    def set_name(self, name):
        self.name = name
    def set_offset(self, offset):
        self.offset = offset
    def set_index(self, index):
        self.index = index
    def extract(self, ast_node):
        if ast_node == None:
            return
        self.ast_node = ast_node
        if isinstance(self.ast_node, ast.Subscript):
            self.name = self.ast_node.value.id
            assert(hasattr(self.ast_node.slice, "lp_data")) # has been traversed
            slice_node = self.ast_node.slice.lp_data
            self.dim = slice_node.dim
            self.upper = slice_node.upper
            self.lower = slice_node.lower
            self.slices = slice_node.slices

        elif isinstance(self.ast_node, ast.Name):
            self.name = self.ast_node.id
            self.offset = None
            self.index = None
        else:
            raise NotImplementedError


class LambdaNode(Node):
    def __init__(self, ast_node=None):
        Node.__init__(self, ast_node)
        self.params = []


class HmapNode(Node):
    def __init__(self, asNode=None, lambda_node=None, op_lst=None):
        Node.__init__(self, ast_node)
        self.lambda_node = lambda_node
        self.op_lst = op_lst
