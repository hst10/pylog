import ast

pytypes = {"None": None, "bool": bool, "int": int, "float": float, "str": str}

class LpType:
    def __init__(self, ele_type="float", dim=0):
        self.ele_type = ele_type
        self.dim = dim

    def __repr__(self):
        return "LpType(" + self.ele_type + ", " + str(self.dim) + ")"

    def __eq__(self, other):
        if (self.ele_type == other.ele_type) and (self.dim == other.dim):
            return True
        else:
            return False
    def __add__(self, other):
        if isinstance(other, int):
            return LpType(self.ele_type, self.dim+other)
        if self.ele_type != other.ele_type:
            return LpType("float", self.dim+other.dim)
        else:
            return LpType(self.ele_type, self.dim+other.dim)

class LpConfig:
    def __init__(self, indent_level=0, indent_str=" "*2, idx_var_num=0, \
                 context=None, var_list={}, targets=None, node=None):
        self.indent_level = indent_level
        self.indent_str = indent_str
        self.idx_var_num = idx_var_num
        self.context = context
        self.var_list = var_list
        self.tarets = targets
        self.curr_node = node

class Context:
    def __init__(self, in_lambda=False, map_vars=None, lambda_args_map={}):
        self.in_lambda = in_lambda
        self.map_vars = map_vars
        self.lambda_args_map = lambda_args_map

class Node:
    def __init__(self, ast_node=None, config=None):
        self.ast_node = ast_node
        self.config = config
        self.name = "LpNode"
        self.codegened = False
        self.type = None # LpType("None", 0)
    def __repr__(self):
        return str(self.name)
    def set_codegened(self):
        tmp = self.codegened
        self.codegened = True
        return tmp

class TypeNode(Node):
    def __init__(self, ast_node=None, config=None):
        Node.__init__(self, ast_node, config)
        if ast_node != None:
            self.extract(ast_node)
    def __repr__(self):
            if self.type != None:
                return "TypeNode(" + self.type.ele_type + ", " + str(self.type.dim) + ")"
            else:
                return "TypeNode()"
    def extract(self, ast_node):
        if ast_node == None:
            return
        self.ast_node = ast_node
        if ast_node.args[0].id in pytypes:
            self.type = LpType(ast_node.args[0].id, ast_node.args[1].n)


class ConstNode(Node):
    def __init__(self, ast_node=None, config=None):
        Node.__init__(self, ast_node, config)
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
    def __init__(self, ast_node=None, config=None):
        Node.__init__(self, ast_node, config)
        self.slices = []
        self.index = None
        self.dim   = None
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
        if isinstance(ast_node, ast.Index):
            if hasattr(ast_node.value, "lp_data"):
                return ast_node.value.lp_data
            else:
                return ast_node.value.n
        lower = None
        upper = None
        step  = 1

        # TODO: assuming all values are consts, expr support to add
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
    """ast.Subscript, ast.Name"""
    def __init__(self, ast_node=None, config=None, name=None, offset=None, index=None):
        Node.__init__(self, ast_node, config)
        self.name = name
        self.offset = offset
        self.index = index
        if ast_node != None:
            self.extract(ast_node)

        if config != None:
            if self.name in config.var_list:
                self.type = config.var_list[self.name]
                print("VariableNode assigns type to " + self.name +": "+str(self.type))

        if hasattr(self, "slices") and self.slices != None:
            self.type = LpType("float", len(self.slices))

    def __repr__(self):
        if hasattr(self, "slices") and self.slices != None:
            return self.name + str(self.slices)
        elif self.index != None:
            return self.name + "[" + str(self.index) + "]"
        else:
            return self.name

    def set_name(self, name):
        self.name = name
    def set_offset(self, offset):
        self.offset = offset
    def set_index(self, index):
        self.index = index

    def get_child_variable(self, index):
        """x[i][j] -> x[i][j][k]"""
        pass

    def extract(self, ast_node):
        if ast_node == None:
            return
        self.ast_node = ast_node
        if isinstance(self.ast_node, ast.Subscript):
            self.name = self.ast_node.value.id # TODO: add supports for expr[slice]
            assert(hasattr(self.ast_node.slice, "lp_data")) # has been traversed
            slice_node = self.ast_node.slice.lp_data

            if isinstance(slice_node, SliceNode):
                self.dim = slice_node.dim
                self.upper = slice_node.upper
                self.lower = slice_node.lower
                self.slices = slice_node.slices #TODO: error when = slice_node
            else:
                # list, ConstNode, VariableNode, etc. 
                self.index = slice_node

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
    def __init__(self, ast_node=None, config=None):
        Node.__init__(self, ast_node, config)
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
    def __init__(self, ast_node=None, config=None):
        Node.__init__(self, ast_node, config)
        if ast_node != None:
            self.extract(ast_node)

    def __repr__(self):
        return "LambdaNode"

    def extract(self, ast_node):
        self.args = ast_node.args.lp_data
        self.body = ast_node.body.lp_data
        self.type = self.body.type
        print("LambdaNode assigns type to " + self.name +": "+str(self.type))
        print("LambdaNode body type: ", type(self.body))

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

class MapNode(Node):
    def __init__(self, ast_node=None, config=None):
        Node.__init__(self, ast_node, config)
        self.iter_vars = []
        if ast_node != None:
            self.extract(ast_node)
        if config != None:
            print(">>>>>>>>>>> Map Found CONFIG")
            print(config.var_list)

    def extract(self, ast_node):
        arg_lst = [ arg.lp_data for arg in ast_node.args ]
        self.func = arg_lst[0]
        self.data = arg_lst[1:]
        self.target = None
        print("!!!!!! parent for map: ", ast_node.parent)
        if isinstance(ast_node.parent, ast.Assign):
            self.target = ast_node.parent.targets[0].lp_data
            print("!!! Assign target for map")
        # elif ast_node.parent.lp_data.type:
            
        self.dim = self.data[0].dim

        if self.func.type:
            print("############# lambda type: ", self.func.type)

        self.type = self.func.type + 1
        print(">>>>>>>>>>>> Map assigns type to " + self.name +": "+str(self.type))

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
                        + "map_i%d: for (int i%d = %d; i%d < %d; i%d += %d) {\n" %   \
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


class HmapNode(Node):
    def __init__(self, ast_node=None, config=None):
        Node.__init__(self, ast_node, config)
        self.iter_vars = []
        if ast_node != None:
            self.extract(ast_node)
        if config != None:
            print(">>>>>>>>>>> Hmap Found CONFIG")
            print(config.var_list)

    def extract(self, ast_node):
        arg_lst = [ arg.lp_data for arg in ast_node.args ]
        self.func = arg_lst[0]
        self.data = arg_lst[1:]
        self.target = ast_node.parent.targets[0].lp_data
        self.dim = self.data[0].dim

        print("########### ", type(self.func))

        if arg_lst[0].type:
            print("############# lambda type: ", arg_lst[0].type)
        if arg_lst[1].type:
            print("############# data: ", arg_lst[1].type)

        self.type = arg_lst[1].type + arg_lst[0].type
        print(">>>>>>>>>>>> HmapNode assigns type to " + self.name +": "+str(self.type))

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
    """NOTE: This definition is different from NumPy. Will be upated later"""
    def __init__(self, ast_node=None, config=None):
        Node.__init__(self, ast_node, config)
        self.iter_vars = []
        self.operands = []
        if ast_node != None:
            self.extract(ast_node)
        if len(self.operands) == 2:
            print("DotNode operand types: ", self.operands[0].type)
            print("DotNode operand types: ", self.operands[1].type)
            if self.operands[0].type and self.operands[1].type: 
                self.type = LpType(self.operands[0].type.ele_type, 0)
                print("DotNode assigns type to " + self.name +": "+str(self.type))

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
    def __init__(self, ast_node=None, config=None):
        Node.__init__(self, ast_node, config)
        self.iter_vars = []
        if ast_node != None:
            self.extract(ast_node)
        if config != None:
            print(">>>>>>>>>>> FuncDef Found CONFIG")
            print(config.var_list)

    def extract(self, ast_node):
        self.name = ast_node.name
        
class AssignNode(Node):
    def __init__(self, ast_node=None, config=None):
        Node.__init__(self, ast_node, config)
        self.node = "AssignNode"
        if ast_node != None:
            self.extract(ast_node)

    def extract(self, ast_node):
        self.targets = [ t.lp_data for t in ast_node.targets ]

