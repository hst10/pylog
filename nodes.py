import ast

class CodegenConfig:
    def __init__(self, indent_level=0, indent_str=" "*2, idx_var_num=0, context=None):
        self.indent_level = indent_level
        self.indent_str = indent_str
        self.idx_var_num = idx_var_num
        self.context = context

class Context:
    def __init__(self, in_lambda=False, map_vars=None, lambda_args_map={}):
        self.in_lambda = in_lambda
        self.map_vars = map_vars
        self.lambda_args_map = lambda_args_map

class Node:
    def __init__(self, ast_node=None):
        self.ast_node = ast_node
        self.name = "LpNode"
        self.codegened = False
    def __repr__(self):
        return str(self.name)
    def set_codegened(self):
        tmp = self.codegened
        self.codegened = True
        return tmp

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
        self.step  = 1
        if ast_node != None:
            self.extract(ast_node)

    def __repr__(self):
        if self.dim == 1:
            return str(self.lower)+":"+str(self.upper)+":"+str(self.step)
        else: 
            return "ExtSlice Content"

    # def __getitem__(self, i):
    #     return self.slices[i]

    # def __getitem__(self, i, j):
    #     return self.slices[i][j]


    def extract_slice(self, ast_node):
        lower = None
        upper = None
        step  = 1
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
        if hasattr(self, "slices") and self.slices != None:
            return self.name + str(self.slices)
        else:
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
            self.slices = slice_node.slices #TODO: error when = slice_node
        elif isinstance(self.ast_node, ast.Name):
            self.name = self.ast_node.id
            self.offset = None
            self.index = None
        elif isinstance(self.ast_node, ast.arg):
            self.name = self.ast_node.arg
            self.offset = None
            self.index = None
        else:
            raise NotImplementedError

class BinOpNode(Node):
    def __init__(self, ast_node=None):
        Node.__init__(self, ast_node)
        if ast_node != None:
            self.extract(ast_node)

    def __repr__(self):
        if isinstance(self.op, ast.Mult):
            return str(self.left) + "*" + str(self.right)

    def extract(self, ast_node):
        self.left = ast_node.left.lp_data
        self.right = ast_node.right.lp_data
        self.op = ast_node.op

class LambdaNode(Node):
    def __init__(self, ast_node=None):
        Node.__init__(self, ast_node)
        if ast_node != None:
            self.extract(ast_node)
    def __repr__(self):
        return "LambdaNode"

    def extract(self, ast_node):
        self.args = ast_node.args.lp_data
        self.body = ast_node.body.lp_data

    def codegen(self, config, arguments, output_var):
        # if self.set_codegened(): return ""
        self.src = ""
        
        self.iter_vars = config.iter_vars
        param_names = [e.name for e in self.args]
        argum_names = [e.name for e in arguments]
        self.param2arg = dict(zip(param_names, argum_names))
        self.output_var = output_var

        curr_context = Context(in_lambda=True, lambda_args_map=self.param2arg)

        new_config = config
        new_config.context = curr_context

        self.src += self.body.codegen(new_config)

        return self.src

class HmapNode(Node):
    def __init__(self, ast_node=None):
        Node.__init__(self, ast_node)
        self.iter_vars = []
        if ast_node != None:
            self.extract(ast_node)

    def extract(self, ast_node):
        arg_lst = [ arg.lp_data for arg in ast_node.args ]
        self.func = arg_lst[0]
        self.data = arg_lst[1:]
        self.target = ast_node.parent.targets[0].lp_data
        self.dim = self.data[0].dim
        # print("hmap_func   = ", self.func)
        # print("hmap_data   = ", self.data)
        # print("hmap_target = ", self.target)

        # print(self.data.dim)
        # print(self.data.slices)

    def codegen(self, config):
        # if self.set_codegened(): return ""
        self.src = ""
        dim = self.dim
        indent_level = config.indent_level
        indent_str = config.indent_str
        idx_var_num = config.idx_var_num
        for dim_i in range(dim):
            idx_var_num += 1
            
            # assuming these are all consts not variables
            lower_i = self.data[0].slices[dim_i][0]
            upper_i = self.data[0].slices[dim_i][1]
            step_i  = self.data[0].slices[dim_i][2]
            self.src += indent_str*indent_level \
                        + "hmap_i%d: for (int i%d = %d; i%d < %d; i%d += %d) {\n" %   \
                        (idx_var_num, idx_var_num, lower_i, idx_var_num, upper_i, \
                         idx_var_num, step_i)
            self.iter_vars.append("i%d" % idx_var_num)

            indent_level += 1

        config.indent_level = indent_level
        config.idx_var_num = idx_var_num
        config.iter_vars = self.iter_vars
        if not hasattr(config, "context"):
            config.context = Context()
        # config.context.map_vars = [ VariableNode(name=var.name, index=) for var in self.data ]

        self.src += self.func.codegen(config, self.data, self.target)

        self.src += indent_str*indent_level + str(self.target) + \
                    "[" + "][".join(self.iter_vars) + "] = " + str(config.context.return_var) + "; \n"

        for dim_i in range(dim):
            indent_level -= 1
            self.src += indent_str*indent_level + "}\n"

        config.indent_level = indent_level

class DotNode(Node):
    """dot(A, B): returns the dot product of A and B"""
    def __init__(self, ast_node=None):
        Node.__init__(self, ast_node)
        self.iter_vars = []
        if ast_node != None:
            self.extract(ast_node)

    def extract(self, ast_node):
        assert(len(ast_node.args) == 2)
        self.operands = [ e.lp_data for e in ast_node.args ]
        self.dim = self.operands[0].dim

    def gen_inner_vars(self, var, config):
        assert(hasattr(config.context, "lambda_args_map"))
        if var.name in config.context.lambda_args_map:
            tmp_src = config.context.lambda_args_map[var.name]
            tmp_src += "[" + "][".join([ self.iter_vars[i]+"+"+config.iter_vars[i]+"+("+str(var.slices[i][0])+")" \
                                         for i in range(len(self.iter_vars)) ]) + "]"
            return tmp_src
        else:
            tmp_src = var.name
            tmp_src += "[" + "][".join(self.iter_vars) + "]"
            return tmp_src

    def codegen(self, config):
        # if self.set_codegened(): return ""
        self.src = ""
        if not hasattr(config.context, "lambda_args_map"): return self.src

        indent_level = config.indent_level
        indent_str = config.indent_str
        idx_var_num = config.idx_var_num

        idx_var_num += 1
        accum_var_name = "tmp" + str(idx_var_num)
        config.context.return_var = VariableNode(name=accum_var_name)

        self.src += indent_str*indent_level + "int " + accum_var_name + " = 0;\n"

        for dim_i in range(self.dim):
            idx_var_num += 1

            # assuming these are all consts not variables
            lower_i = self.operands[0].slices[dim_i][0]
            upper_i = self.operands[0].slices[dim_i][1]
            step_i  = self.operands[0].slices[dim_i][2]
            range_i = upper_i - lower_i

            self.src += indent_str*indent_level \
                        + "dot_i%d: for (int i%d = 0; i%d < %d; i%d += %d) {\n" %   \
                        (idx_var_num, idx_var_num, idx_var_num, range_i, \
                         idx_var_num, step_i)
            self.iter_vars.append("i%d" % idx_var_num)

            indent_level += 1


        # print loop body
        self.src += indent_str*indent_level + accum_var_name + " += "
        self.src += self.gen_inner_vars(self.operands[0], config)
        self.src += " * "
        self.src += self.gen_inner_vars(self.operands[1], config)
        self.src += "; \n"

        config.indent_level = indent_level
        config.idx_var_num = idx_var_num

        for dim_i in range(self.dim):
            indent_level -= 1
            self.src += indent_str*indent_level + "}\n"
            
        config.indent_level = indent_level

        return self.src


class FuncDefNode(Node):
    def __init__(self, ast_node=None):
        Node.__init__(self, ast_node)
        self.iter_vars = []
        if ast_node != None:
            self.extract(ast_node)

    def extract(self, ast_node):
        self.name = ast_node.name
        
