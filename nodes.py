import ast

class Node:
    def __init__(self, ast_node=None):
        self.ast_node = ast_node
    def __repr__(self):
        return str(self.name)

class ConstNode(Node):
    def __init__(self, ast_node=None):
        Node.__init__(self, ast_node)
        self.value = None
        if ast_node != None:
            self.config(self, ast_node)

    def config(self, ast_node):
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


class VariableNode(Node):
    def __init__(self, ast_node=None, name=None, offset=None, index=None):
        Node.__init__(self, ast_node)
        self.name = name
        self.offset = offset
        self.index = index

    def set_name(self, name):
        self.name = name
    def set_offset(self, offset):
        self.offset = offset
    def set_index(self, index):
        self.index = index
    def config(self, ast_node):
        self.ast_node = ast_node
        if isinstance(self.ast_node, ast.Subscript):
            self.name = self.ast_node.value.id
        elif isinstance(self.ast_node, ast.Name):
            print("A")
        elif isinstance(self.ast_node, ast.Num):
            print("A")
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