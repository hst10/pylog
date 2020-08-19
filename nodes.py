import ast


def iter_fields(node):
    if isinstance(node, list):
        for item in node:
            if isinstance(item, PLNode):
                yield item

    for field in node._fields:
        try:
            yield field, getattr(node, field)
        except AttributeError:
            pass


def iter_child_nodes(node):
    if isinstance(node, list):
        for item in node:
            if isinstance(item, PLNode):
                yield item

    for name, field in iter_fields(node):
        if isinstance(field, PLNode):
            yield field
        elif isinstance(field, list):
            for item in field:
                if isinstance(item, PLNode):
                    yield item


def replace_child(parent, old_child, new_child):
    if isinstance(parent, list):
        for idx in range(len(parent)):
            if parent[idx] == old_child:
                parent[idx] = new_child
        return

    for name, field in iter_fields(parent):
        if isinstance(field, list):
            for idx, child in enumerate(field):
                if child is old_child:
                    getattr(parent, name)[idx] = new_child
                    new_child.parent = parent
                    return
        elif isinstance(field, PLNode):
            if field is old_child:
                setattr(parent, name, new_child)
                new_child.parent = parent
                return


def plnode_walk(node):
    from collections import deque
    if isinstance(node, list):
        todo = deque(node)
    else:
        todo = deque([node])
    while todo:
        node = todo.popleft()
        todo.extend(iter_child_nodes(node))
        yield node


def plnode_link_parent(root):
    for node in plnode_walk(root):
        for child in iter_child_nodes(node):
            child.parent = node


def token(obj):
    type_name = obj.__class__.__name__
    token_map = {
        "And": "&&",
        "Or": "||",
        "Add": "+",
        "Sub": "-",
        "Mult": "*",
        "MatMult": "@",
        "Div": "/",
        "Mod": "%",
        "Pow": "**",
        "LShift": "<<",
        "RShift": ">>",
        "BitOr": "|",
        "BitXor": "^",
        "BitAnd": "&",
        "FloorDiv": "//",
        "Invert": "~",
        "Not": "not",
        "UAdd": "+",
        "USub": "-",
        "Eq": "==",
        "NotEq": "!=",
        "Lt": "<",
        "LtE": "<=",
        "Gt": ">",
        "GtE": ">=",
        "Is": "is",
        "IsNot": "is not",
        "In": "in",
        "NotIn": "not in"
    }
    return token_map.get(type_name, "Invalid token")


class Context:
    def __init__(self, in_lambda=False, map_vars=None, lambda_args_map={}):
        self.in_lambda = in_lambda
        self.map_vars = map_vars
        self.lambda_args_map = lambda_args_map


class PLNode:
    def __init__(self, ast_node=None, config=None):
        self._fields = []
        self.ast_node = ast_node
        self.config = config
        self.codegened = False
        self.type = None  # PLType(None, 0)

    def __repr__(self):
        return f'<{self.__class__.__name__}<{hex(id(self))}>>'

    def set_codegened(self):
        tmp = self.codegened
        self.codegened = True
        return tmp


# class TypeNode(PLNode):
#     def __init__(self, type_val, ast_node=None, config=None):
#         PLNode.__init__(self, ast_node, config)
#         self._fields = ['type_val']
#         self.type = type_val

#     def __repr__(self):
#             if self.type != None:
#                 return "TypeNode(" + self.type.ele_type + ", " + \
#                                                   str(self.type.dim) + ")"
#             else:
#                 return "TypeNode()"

#     def extract(self, ast_node):
#         if ast_node == None:
#             return
#         self.ast_node = ast_node
#         if ast_node.args[0].id in pytypes:
#             self.type = PLType(ast_node.args[0].id, ast_node.args[1].n)


class PLConst(PLNode):
    '''Constant, Num, Str, NameConstant'''

    def __init__(self, value, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['value']
        self.value = value
        self.type = type(self.value)

    def __repr__(self):
        if self.value != None:
            return str(self.value)
        else:
            return "ConstNode: Unknown value"

    # def extract(self, ast_node):
    #     if ast_node == None:
    #         return
    #     self.ast_node = ast_node
    #     if isinstance(self.ast_node, ast.Num):
    #         self.value = self.ast_node.n
    #     elif isinstance(self.ast_node, ast.UnaryOp):
    #         if isinstance(self.ast_node.op, ast.USub):
    #             self.value = -self.ast_node.operand.n
    #         elif isinstance(self.ast_node.op, ast.UAdd):
    #             self.value = self.ast_node.operand.n
    #     else:
    #         raise NotImplementedError


class PLArray(PLNode):
    '''Array in declaration, List, Tuple. '''

    def __init__(self, elts, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['elts']
        self.elts = elts


class PLArrayDecl(PLNode):
    '''Array declaration
       ele_type: string
       dims: PLArray
    '''

    def __init__(self, ele_type, name, dims, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['ele_type', 'name', 'dims']
        self.ele_type = ele_type
        self.name = name
        self.dims = dims


class PLVariableDecl(PLNode):
    '''Declare a variable with optional initial value'''

    def __init__(self, ty, name, init, quals=[], ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['ty', 'name', 'init', 'quals']
        self.ty = ty
        self.name = name
        self.init = init
        self.quals = quals


class PLVariable(PLNode):
    '''ast.Name
        name: string
    '''

    def __init__(self, name, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['name']
        self.name = name


class PLUnaryOp(PLNode):
    '''UnaryOp'''

    def __init__(self, op, operand, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['op', 'operand']
        self.op = op
        self.operand = operand


class PLBinOp(PLNode):
    '''BinOp, BoolOp'''

    def __init__(self, op, left, right, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['op', 'left', 'right']
        self.op = op
        self.left = left
        self.right = right


# class BinOpNode(PLNode):
#     def __init__(self, ast_node=None, config=None):
#         PLNode.__init__(self, ast_node, config)
#         self._fields = []
#         if ast_node != None:
#             self.extract(ast_node)

#     def __repr__(self):
#         if isinstance(self.op, ast.Mult):
#             return str(self.left) + "*" + str(self.right)

#     def extract(self, ast_node):
#         self.left = ast_node.left.pl_data
#         self.right = ast_node.right.pl_data
#         self.op = ast_node.op


## should use PLBinOp instead
# class PLBoolOp(PLNode):
#     '''BoolOp'''
#     def __init__(self, op, values, ast_node=None, config=None):
#         PLNode.__init__(self, ast_node, config)
#         self.op = op
#         self.values = values

## should use PLBinOp instead
# class PLCompare(PLNode):
#     '''Compare'''
#     def __init__(self, ops, values, ast_node=None, config=None):
#         PLNode.__init__(self, ast_node, config)
#         self.ops = ops
#         self.values = values


class PLCall(PLNode):
    '''ast.Call
        func: PLVariable
        args: list of PLNodes
        attr: string
        attr_args: list of PLNodes
        is_method: whether it is a class method with object
        obj: object when it is a class method
    '''

    def __init__(self, func, args, attr=None, attr_args=None, is_method=False, obj=None, \
                 ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['func', 'args', 'attr', 'attr_args']
        self.func = func
        self.args = args
        self.attr = attr  # string
        self.attr_args = attr_args
        self.is_method = is_method
        self.obj = obj


class PLPragma(PLNode):
    '''Call'''

    def __init__(self, pragma, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['pragma']
        self.pragma = pragma


class PLKeyword(PLNode):
    '''keyword'''
    pass


class PLIfExp(PLNode):
    '''if (exp)? a:b'''

    def __init__(self, test, body, orelse, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['test', 'body', 'orelse']
        self.test = test
        self.body = body
        self.orelse = orelse


class PLAttribute(PLNode):
    '''Attribute'''

    def __init__(self, value, attr, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['value', 'attr']
        self.value = value
        self.attr = attr


class PLChainingTop(PLNode):
    '''ChainingTop'''

    def __init__(self, stmt, pl_type, pl_shape, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['stmt']
        self.stmt = stmt
        self.pl_type = pl_type
        self.pl_shape = pl_shape

    def __repr__(self):
        return self.stmt.__repr__()


class PLSubscript(PLNode):
    '''Subscript'''

    def __init__(self, var, indices, ast_node=None, config=None):
        '''
            var: expr for the array name
            indices: Python list of PLSlice/Expr
        '''
        PLNode.__init__(self, ast_node, config)
        self._fields = ['var', 'indices']
        self.var = var
        self.indices = indices

    def __repr__(self):
        return str(self.var) + "[" + \
               ", ".join([str(e) for e in self.indices]) + "]"


class PLSlice(PLNode):
    def __init__(self, lower, upper, step, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['lower', 'upper', 'step']
        self.lower = lower
        self.upper = upper
        self.step = step

    def __repr__(self):
        return str(self.lower) + ":" + str(self.upper) + ":" + str(self.step)

    # def __getitem__(self, i):
    #     return self.slices[i]

    # def __getitem__(self, i, j):
    #     return self.slices[i][j]


class PLAssign(PLNode):
    '''Assign, AugAssign'''

    def __init__(self, op, target, value, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['op', 'target', 'value']
        self.op = op
        self.target = target
        self.value = value
        self.target.parent = self
        self.value.parent = self

    # def extract(self, ast_node):
    #     self.targets = [ t.pl_data for t in ast_node.targets ]


class PLIf(PLNode):
    def __init__(self, test, body, orelse, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['test', 'body', 'orelse']
        self.test = test
        self.body = body
        self.orelse = orelse


class PLIterDom(PLNode):
    '''Represents iteration domain in 'for obj in domain' '''

    def __init__(self, expr=None, start=PLConst(0), op='<', end=PLConst(128),
                 step=PLConst(1), ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['start', 'op', 'end', 'step']
        self.expr = expr
        self.start = start
        self.op = op
        self.end = end
        self.step = step
        self.attr = None
        self.attr_args = None
        self.type = None  # "range" or "expr"
        if expr is not None:
            if isinstance(self.expr, PLCall) and \
                    self.expr.func.name == "range":
                '''coming from visit_Call -> range'''
                self.type = "range"
                num_args = len(self.expr.args)
                if num_args == 1:
                    self.start = PLConst(value=0)
                    self.op = "<"
                    self.end = self.expr.args[0]
                    self.step = PLConst(value=1)
                elif num_args == 2:
                    self.start = self.expr.args[0]
                    self.op = "<"
                    self.end = self.expr.args[1]
                    self.step = PLConst(value=1)
                elif num_args == 3:
                    self.start = self.expr.args[0]
                    self.end = self.expr.args[1]
                    self.step = self.expr.args[2]
                    if isinstance(self.step, PLConst) and self.step.value < 0:
                        self.op = ">"
                    else:
                        self.op = "<"
                        # TODO: need to generate two versions of for,
                        # depending on the value of step in runtime.

                if self.expr.attr != None:
                    self.attr = self.expr.attr
                    self.attr_args = self.expr.attr_args

            else:
                '''Coming from visit_For, iter_dom is a PyLog expression'''
                self.type = "expr"
                pass
                # TODO: need to generate separate ArrayDecl before current stmt


class PLFor(PLNode):
    def __init__(self, target, iter_dom, body, orelse, \
                 ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['target', 'iter_dom', 'body', 'orelse']
        self.target = target
        self.iter_dom = iter_dom
        self.body = body
        self.orelse = orelse


class PLWhile(PLNode):
    def __init__(self, test, body, orelse, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['test', 'body', 'orelse']
        self.test = test
        self.body = body
        self.orelse = orelse


class PLFunctionDef(PLNode):
    '''
        name: string
        args: list of arguments (PLNodes)
        body: list of statements (PLNodes)
        decorator_list: list of PLNodes
    '''

    def __init__(self, name, args, body, decorator_list, pl_top=False,
                 ast_node=None, config=None, annotations={}):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['name', 'args', 'body', 'decorator_list', 'annotations']
        self.name = name
        self.args = args
        self.body = body
        self.decorator_list = decorator_list
        self.iter_vars = []
        self.pl_top = pl_top
        self.annotations = annotations
        # if config != None:
        #     print(">>>>>>>>>>> FuncDef Found CONFIG")
        #     print(config.var_list)

    # def extract(self, ast_node):
    #     self.name = ast_node.name


class PLLambda(PLNode):
    '''
        args: list of PLVariable
        body: a single expression
    '''

    def __init__(self, args, body, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['args', 'body']
        self.args = args
        self.body = body

    # def __repr__(self):
    #     return "LambdaNode"

    # def extract(self, ast_node):
    #     self.args = ast_node.args.pl_data
    #     self.body = ast_node.body.pl_data
    #     self.type = self.body.type
    #     print("LambdaNode assigns type to " + self.name +": "+str(self.type))
    #     print("LambdaNode body type: ", type(self.body))

    # def codegen(self, config, arguments, output_var):
    #     # if self.set_codegened(): return ""
    #     self.src = ""

    #     self.iter_vars = config.iter_vars
    #     param_names = [e.name for e in self.args]
    #     argum_names = [e.name for e in arguments]
    #     self.param2arg = dict(zip(param_names, argum_names))
    #     self.output_var = output_var

    #     curr_context = Context(in_lambda=True,
    #                             lambda_args_map=self.param2arg)

    #     new_config = config
    #     new_config.context = curr_context

    #     self.src += self.body.codegen(new_config)

    #     return self.src


class PLReturn(PLNode):
    def __init__(self, value, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['value']
        self.value = value


'''
    out = map(f, a, b, ...)
    =>
    T out[a.shape(0)];
    for (int i = 0; i < a.shape(0); i++)
    {
        T tmp = f(a[i], b[i], ...);
        out[i] = tmp;
    }


    out = map(lambda x, y, ...: op(x, y, ...), a, b, ...)
    =>
    T out[a.shape(0)];
    for (int i = 0; i < a.shape(0); i++)
    {
        T tmp = op(a[i], b[i], c[i], ...);
        out[i] = tmp;
    }
'''


class PLMap(PLNode):
    ''' plmap
        target: PLNode (PLVariable or PLSubscript)
        func:   PLLambda
        arrays: list of arrays (PLVariable or PLSubscript)
    '''

    def __init__(self, target, func, arrays, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['target', 'func', 'arrays']
        self.target = target
        self.func = func
        self.arrays = arrays


class PLDot(PLNode):
    ''' pldot
    '''

    def __init__(self, target, op1, op2, ast_node=None, config=None):
        PLNode.__init__(self, ast_node, config)
        self._fields = ['target', 'op1', 'op2']
        self.target = target
        self.op1 = op1
        self.op2 = op2

# class PLMap(PLNode):
#     def __init__(self, ast_node=None, config=None):
#         PLNode.__init__(self, ast_node, config)
#         self._fields = []
#         self.iter_vars = []
#         if ast_node != None:
#             self.extract(ast_node)
#         if config != None:
#             print(">>>>>>>>>>> Map Found CONFIG")
#             print(config.var_list)

#     def extract(self, ast_node):
#         arg_lst = [ arg.pl_data for arg in ast_node.args ]
#         self.func = arg_lst[0]
#         self.data = arg_lst[1:]
#         self.target = None
#         print("!!!!!! parent for map: ", ast_node.parent)
#         if isinstance(ast_node.parent, ast.Assign):
#             self.target = ast_node.parent.targets[0].pl_data
#             print("!!! Assign target for map")
#         # elif ast_node.parent.pl_data.type:

#         self.dim = self.data[0].dim

#         if self.func.type:
#             print("############# lambda type: ", self.func.type)

#         self.type = self.func.type + 1
#         print(">>>>>>>>>>>> Map assigns type to " + self.name +": "+\
#                                                             str(self.type))

#     def codegen(self, config):
#         # if self.set_codegened(): return ""
#         self.src = ""
#         dim = self.dim
#         indent_level = config.indent_level
#         indent_str = config.indent_str
#         idx_var_num = config.idx_var_num
#         for dim_i in range(dim):
#             idx_var_num += 1

#             # assuming these are all consts not variables
#             lower_i = self.data[0].slices[dim_i][0]
#             upper_i = self.data[0].slices[dim_i][1]
#             step_i  = self.data[0].slices[dim_i][2]
#             self.src += indent_str*indent_level \
#                + "map_i%d: for (int i%d = %d; i%d < %d; i%d += %d) {\n" %   \
#                (idx_var_num, idx_var_num, lower_i, idx_var_num, upper_i, \
#                 idx_var_num, step_i)
#             self.iter_vars.append("i%d" % idx_var_num)

#             indent_level += 1

#         config.indent_level = indent_level
#         config.idx_var_num = idx_var_num
#         config.iter_vars = self.iter_vars
#         if not hasattr(config, "context"):
#             config.context = Context()
#         # config.context.map_vars = [ VariableNode(name=var.name, index=) \
#                                                        for var in self.data ]

#         self.src += self.func.codegen(config, self.data, self.target)

#         self.src += indent_str*indent_level + str(self.target) + \
#                     "[" + "][".join(self.iter_vars) + "] = " + \
#                                      str(config.context.return_var) + "; \n"

#         for dim_i in range(dim):
#             indent_level -= 1
#             self.src += indent_str*indent_level + "}\n"

#         config.indent_level = indent_level


# class PLHmap(PLNode):
#     def __init__(self, ast_node=None, config=None):
#         PLNode.__init__(self, ast_node, config)
#         self._fields = []
#         self.iter_vars = []
#         if ast_node != None:
#             self.extract(ast_node)
#         if config != None:
#             print(">>>>>>>>>>> Hmap Found CONFIG")
#             print(config.var_list)

#     def extract(self, ast_node):
#         arg_lst = [ arg.pl_data for arg in ast_node.args ]
#         self.func = arg_lst[0]
#         self.data = arg_lst[1:]
#         self.target = ast_node.parent.targets[0].pl_data
#         self.dim = self.data[0].dim

#         print("########### ", type(self.func))

#         if arg_lst[0].type:
#             print("############# lambda type: ", arg_lst[0].type)
#         if arg_lst[1].type:
#             print("############# data: ", arg_lst[1].type)

#         self.type = arg_lst[1].type + arg_lst[0].type
#         print(">>>>>>>>>>>> HmapNode assigns type to " + self.name +": "+\
#                                                              str(self.type))

#         # print("hmap_func   = ", self.func)
#         # print("hmap_data   = ", self.data)
#         # print("hmap_target = ", self.target)

#         # print(self.data.dim)
#         # print(self.data.slices)

#     def codegen(self, config):
#         # if self.set_codegened(): return ""
#         self.src = ""
#         dim = self.dim
#         indent_level = config.indent_level
#         indent_str = config.indent_str
#         idx_var_num = config.idx_var_num
#         for dim_i in range(dim):
#             idx_var_num += 1

#             # assuming these are all consts not variables
#             lower_i = self.data[0].slices[dim_i][0]
#             upper_i = self.data[0].slices[dim_i][1]
#             step_i  = self.data[0].slices[dim_i][2]
#             self.src += indent_str*indent_level \
#                 + "hmap_i%d: for (int i%d = %d; i%d < %d; i%d += %d) {\n" % \
#                 (idx_var_num, idx_var_num, lower_i, idx_var_num, upper_i, \
#                  idx_var_num, step_i)
#             self.iter_vars.append("i%d" % idx_var_num)

#             indent_level += 1

#         config.indent_level = indent_level
#         config.idx_var_num = idx_var_num
#         config.iter_vars = self.iter_vars
#         if not hasattr(config, "context"):
#             config.context = Context()
#         # config.context.map_vars = [ VariableNode(name=var.name, index=)\
#         #                                          for var in self.data ]

#         self.src += self.func.codegen(config, self.data, self.target)

#         self.src += indent_str*indent_level + str(self.target) + \
#                     "[" + "][".join(self.iter_vars) + "] = " + \
#                                     str(config.context.return_var) + "; \n"

#         for dim_i in range(dim):
#             indent_level -= 1
#             self.src += indent_str*indent_level + "}\n"

#         config.indent_level = indent_level

# class PLDot(PLNode):
#     """dot(A, B): returns the dot product of A and B"""
#     """NOTE: This definition is different from NumPy. Will be upated later"""
#     def __init__(self, ast_node=None, config=None):
#         PLNode.__init__(self, ast_node, config)
#         self._fields = []
#         self.iter_vars = []
#         self.operands = []
#         if ast_node != None:
#             self.extract(ast_node)
#         if len(self.operands) == 2:
#             print("DotNode operand types: ", self.operands[0].type)
#             print("DotNode operand types: ", self.operands[1].type)
#             if self.operands[0].type and self.operands[1].type:
#                 self.type = PLType(self.operands[0].type.ele_type, 0)
#                 print("DotNode assigns type to " + self.name +": "+\
#                                                             str(self.type))

#     def extract(self, ast_node):
#         assert(len(ast_node.args) == 2)
#         self.operands = [ e.pl_data for e in ast_node.args ]
#         self.dim = self.operands[0].dim

#     def gen_inner_vars(self, var, config):
#         assert(hasattr(config.context, "lambda_args_map"))
#         if var.name in config.context.lambda_args_map:
#             tmp_src = config.context.lambda_args_map[var.name]
#             tmp_src += "[" + "][".join([ self.iter_vars[i]+"+"+\
#                         config.iter_vars[i]+"+("+str(var.slices[i][0])+")" \
#                         for i in range(len(self.iter_vars)) ]) + "]"
#             return tmp_src
#         else:
#             tmp_src = var.name
#             tmp_src += "[" + "][".join(self.iter_vars) + "]"
#             return tmp_src

#     def codegen(self, config):
#         # if self.set_codegened(): return ""
#         self.src = ""
#         if not hasattr(config.context, "lambda_args_map"): return self.src

#         indent_level = config.indent_level
#         indent_str = config.indent_str
#         idx_var_num = config.idx_var_num

#         idx_var_num += 1
#         accum_var_name = "tmp" + str(idx_var_num)
#         config.context.return_var = VariableNode(name=accum_var_name)

#         self.src += indent_str*indent_level + "int " + accum_var_name+" = 0;\n"

#         for dim_i in range(self.dim):
#             idx_var_num += 1

#             # assuming these are all consts not variables
#             lower_i = self.operands[0].slices[dim_i][0]
#             upper_i = self.operands[0].slices[dim_i][1]
#             step_i  = self.operands[0].slices[dim_i][2]
#             range_i = upper_i - lower_i

#             self.src += indent_str*indent_level \
#                 + "dot_i%d: for (int i%d = 0; i%d < %d; i%d += %d) {\n" %   \
#                 (idx_var_num, idx_var_num, idx_var_num, range_i, \
#                  idx_var_num, step_i)
#             self.iter_vars.append("i%d" % idx_var_num)

#             indent_level += 1


#         # print loop body
#         self.src += indent_str*indent_level + accum_var_name + " += "
#         self.src += self.gen_inner_vars(self.operands[0], config)
#         self.src += " * "
#         self.src += self.gen_inner_vars(self.operands[1], config)
#         self.src += "; \n"

#         config.indent_level = indent_level
#         config.idx_var_num = idx_var_num

#         for dim_i in range(self.dim):
#             indent_level -= 1
#             self.src += indent_str*indent_level + "}\n"

#         config.indent_level = indent_level

#         return self.src
