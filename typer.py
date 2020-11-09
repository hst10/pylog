import re
import copy

from utils import *
from nodes import *
import IPinforms


class PLTyper:
    def __init__(self, args_info, debug=False):
        self.args_info = args_info
        self.debug = debug

    def visit(self, node, ctx={}, is_statement=False):
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
            for field, value in iter_fields(node):
                self.visit(value, ctx)
        elif isinstance(node, list):
            for item in node:  # item is a complete statement
                self.visit(item, ctx)

    def visit_PLFunctionDef(self, node, ctx={}):

        if hasattr(node, 'type_infer_done'):  # TODO: what is this for?
            return  # node.pl_type, node.pl_shape, node.pl_ctx

        node.pl_type = PLType('pl_func', 0)
        node.pl_shape = ()
        ctx[node.name] = (node.pl_type, node.pl_shape, node)

        local_ctx = copy.copy(ctx)

        if node.pl_top:
            # breakpoint()
            buf_decls = []
            buf_copies = ([], [])
            for arg in node.args:
                type_name, shape = self.args_info[arg.name]
                arg.pl_type = PLType(ty=np_pl_type_map(type_name),
                                     dim=len(shape))
                arg.pl_shape = shape

                # copy input array to buffer when annotation=buffer
                # specifically, create a new node named var, which will be used
                # as a buffer for top function's input
                # change the name of top function's input to _var
                annotation = node.annotations[arg.name]
                if annotation is not None and 'buffer' in annotation.value:
                    #breakpoint()
                    elts = [ PLConst(e) for e in shape ]
                    buf_decl = PLArrayDecl(ele_type=arg.pl_type.ty,
                                           name=PLVariable(arg.name),
                                           dims=PLArray(elts=elts))
                    buf_decls.append(buf_decl)

                    if 'in' in annotation.value:
                        buf_copy = PLAssign(op='=',
                                            target=PLVariable(arg.name),
                                            value=PLVariable('_'+arg.name))
                        buf_copies[0].append(buf_copy)
                    elif 'out' in annotation.value:
                        buf_copy = PLAssign(op='=',
                                            target=PLVariable('_'+arg.name),
                                            value=PLVariable(arg.name))
                        buf_copies[1].append(buf_copy)

                    local_ctx[arg.name] = (arg.pl_type, arg.pl_shape, arg)
                    arg.name = '_' + arg.name
            node.body.insert(0, buf_copies[0])
            node.body.insert(0, buf_decls)
            node.body.insert(len(node.body), buf_copies[1])
        node.return_type  = PLType('void', 0)
        node.return_shape = ()

        if all(hasattr(arg, 'pl_type') for arg in node.args):
            for arg in node.args:
                local_ctx[arg.name] = (arg.pl_type, arg.pl_shape, arg)
            for stmt in node.body:
                self.visit(stmt, local_ctx,
                           is_statement=True)  
                if isinstance(stmt, PLReturn):
                    node.return_type = stmt.pl_type
                    node.return_shape = stmt.pl_shape

            node.type_infer_done = True

        # return node.pl_type, node.pl_shape, node.pl_ctx

    def visit_PLConst(self, node, ctx={}):
        node.pl_type = PLType(ty=type(node.value).__name__, dim=0)
        node.pl_shape = ()
        # node.pl_ctx   = {} # no need to maintain context

        # return node.pl_type, node.pl_shape, node.pl_ctx

    def visit_PLArray(self, node, ctx={}):
        dim = len(node.elts)
        if dim == 0:
            node.pl_type = PLType('None', 0)
            node.pl_shape = ()
        else:
            self.visit(node.elts[0], ctx)
            node.pl_type = node.elts[0].pl_type + 1  # assuming 1D list
            node.pl_shape = (dim,)

    def visit_PLArrayDecl(self, node, ctx={}):
        dims = ()
        for e in node.dims.elts:
            dims += (e.value,)

        node.pl_type = PLType(ty=node.ele_type, dim=len(dims))
        node.pl_shape = dims

        # node.pl_ctx   = copy.copy(ctx)
        # breakpoint()
        # node.name is a PLVariable object
        # node.pl_ctx[node.name.name] = (node.pl_type, node.pl_shape, node)
        ctx[node.name.name] = (node.pl_type, node.pl_shape, node)
        # if self.debug:
        #     print(type(node).__name__, node.pl_ctx)

        # return node.pl_type, node.pl_shape, node.pl_ctx

    def visit_PLVariableDecl(self, node, ctx={}):
        node.pl_type = PLType(ty=node.ty, dim=0)
        node.pl_shape = ()
        # node.pl_ctx   = copy.copy(ctx)
        # node.pl_ctx[node.name] = (node.pl_type, node.pl_shape, node)
        ctx[node.name.name] = (node.pl_type, node.pl_shape, node)

        # if self.debug:
        #     print(type(node).__name__, node.pl_ctx)

        # return node.pl_type, node.pl_shape, node.pl_ctx

    def visit_PLVariable(self, node, ctx={}):

        if not hasattr(node, 'pl_type'):  # TODO: What is this for?
            if node.name in ctx:
                node.pl_type = ctx[node.name][0]
                node.pl_shape = ctx[node.name][1]
                # node.pl_ctx   = {}
            else:
                print(node.name)
                # breakpoint()
                raise NameError

        # return node.pl_type, node.pl_shape, node.pl_ctx

    def visit_PLUnaryOp(self, node, ctx={}):
        self.visit(node.operand, ctx)  
        node.pl_type = node.operand.pl_type
        node.pl_shape = node.operand.pl_shape
        # node.pl_ctx   = node.operand.pl_ctx

        # if self.debug:
        #     print(type(node).__name__, node.pl_ctx)

        # return node.pl_type, node.pl_shape, node.pl_ctx

    def visit_PLBinOp(self, node, ctx={}):

        self.visit(node.op, ctx)  # TODO: What is this for?
        self.visit(node.left, ctx)  
        self.visit(node.right, ctx)  

        left_shape = self.actual_shape(node.left.pl_shape)
        right_shape = self.actual_shape(node.right.pl_shape)

        if self.debug:
            print(f'original left_shape = {node.left.pl_shape}')
            print(f'original right_shape = {node.right.pl_shape}')
            print(f'left_shape = {left_shape}')
            print(f'right_shape = {right_shape}')

        if (left_shape != ()) and (right_shape != ()):
            assert (left_shape == right_shape)
            node.pl_type = PLType(node.left.pl_type.ty, len(left_shape))
            node.pl_shape = left_shape
        else:
            if left_shape != ():
                node.pl_type = PLType(node.left.pl_type.ty, len(left_shape))
                node.pl_shape = left_shape
            else:
                node.pl_type = PLType(node.right.pl_type.ty, len(right_shape))
                node.pl_shape = right_shape

    def get_slice_length(self, lower=None, upper=None, step=None,
                         total_len=None):
        # assuming all are constants (for now)
        if step is None:
            step = 1

        if lower is None:
            lower = 0
        if upper is None:
            if step > 0:
                if total_len is None:
                    return None, None
                else:
                    upper = total_len
            else:
                upper = 0

        if total_len is None:
            if (lower < 0) or (upper < 0):
                return None, None

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

        updated_slice = (lower, upper, step)

        if step < 0:
            if lower > upper:
                return (lower - upper + (-step) - 1) // (-step), updated_slice
            else:
                return 0, updated_slice
        else:
            if lower < upper:
                return (upper - lower + step - 1) // step, updated_slice
            else:
                return 0, updated_slice

    def visit_PLSlice(self, node, ctx={}):

        # visit each field first (constant propagation may happen:
        # expression -> PLConst)
        self.visit(node.lower, ctx)  # not dealing with chaining propagation here (array as subscription)
        self.visit(node.upper, ctx)  # not dealing with chaining propagation here (array as subscription)
        self.visit(node.step, ctx)  # not dealing with chaining propagation here (array as subscription)

        lower = node.lower.value if node.lower else None
        upper = node.upper.value if node.upper else None
        step = node.step.value if node.step else None

        if hasattr(node, 'is_offset'):
            if step is None: step = 1
            length = (upper - lower + step - 1) // step
            node.updated_slice = (lower, upper, step)
            node.pl_type = PLType('slice', 0)
            node.pl_shape = (length,)
            return

        if hasattr(node, 'dim_length'):
            dim_length = node.dim_length
        else:
            dim_length = None

        for obj in (node.lower, node.upper, node.step):
            if (obj is not None) and (not isinstance(obj, PLConst)):
                node.pl_type = PLType('slice', 0)
                node.pl_shape = ()
                return

        length, updated_slice = self.get_slice_length(
            lower=lower,
            upper=upper,
            step=step,
            total_len=dim_length)

        node.updated_slice = updated_slice

        node.pl_type = PLType('slice', 0)
        node.pl_shape = (length,)

    def visit_PLAssign(self, node, ctx={}):
        self.visit(node.value, ctx)  # not dealing with chaining propagation here (array as subscription)

        node.is_decl = True
        if isinstance(node.target, PLSubscript):
            node.is_decl = False
        elif len(node.op)>=2:#compound assignment operator like += implies the value is already defined
            node.is_decl= False
        else:
            if node.target.name in ctx:
                ctx_type, ctx_shape, ctx_decl = ctx[node.target.name]
                if isinstance(ctx_decl, PLVariableDecl):
                    node.is_decl = False
                if ctx_shape == node.value.pl_shape:
                    # allow types to be different (implicit type cast)
                    node.is_decl = False

        if node.is_decl:
            node.target.pl_shape = self.actual_shape(node.value.pl_shape)
            node.target.pl_type = PLType(ty=node.value.pl_type.ty, \
                                         dim=len(node.target.pl_shape))

            ctx[node.target.name] = (node.target.pl_type, \
                                     node.target.pl_shape, \
                                     node)
        else:
            self.visit(node.target, ctx)  
            target_type = node.target.pl_type
            target_shape = node.target.pl_shape

            if node.value.pl_shape != ():
                assert ((self.actual_shape(node.value.pl_shape) == \
                         self.actual_shape(target_shape)))

        if node.is_decl:
            node.pl_type = node.value.pl_type
            node.pl_shape = node.value.pl_shape
        else:
            node.pl_type = node.target.pl_type
            node.pl_shape = node.target.pl_shape

    def visit_PLReturn(self, node, ctx={}):
        self.visit(node.value, ctx)  
        if node.value:
            node.pl_type = node.value.pl_type
            node.pl_shape = node.value.pl_shape
        else:
            node.pl_type = PLType('void', 0)
            node.pl_shape = ()

        if self.debug:
            print(type(node).__name__, ctx)

        # return node.pl_type, node.pl_shape, node.pl_ctx

    def visit_PLFor(self, node, ctx={}):
        node.target.pl_type = PLType('int', 0)
        node.target.pl_shape = ()

        ctx[node.target.name] = (node.target.pl_type, node.target.pl_shape, \
                                 node.target)
        self.visit(node.iter_dom, ctx)
        for stmt in node.body:
            self.visit(stmt, ctx)  

        # node.pl_ctx = copy.copy(ctx)

    def visit_PLIterDom(self, node, ctx):
        self.visit(node.end, ctx)
        self.visit(node.expr, ctx)
        self.visit(node.start, ctx)
        self.visit(node.step, ctx)

    def visit_PLWhile(self, node, ctx={}):
        for stmt in node.body:
            self.visit(stmt, ctx)  

        # node.pl_ctx = copy.copy(ctx)

    def visit_PLIf(self, node, ctx={}):
        for stmt in node.body:
            self.visit(stmt, ctx)  

        for stmt in node.orelse:
            self.visit(stmt, ctx)  

    def visit_PLIfExp(self, node, ctx={}):
        #This is to deal with single-line (a if condition else b) expression
        self.visit(node.body, ctx)
        self.visit(node.orelse, ctx)  
        #right now only support node.body shape and type equals those of node.orelse
        assert(node.body.pl_shape==node.orelse.pl_shape)
        assert(node.body.pl_type==node.orelse.pl_type)
        node.pl_shape=node.body.pl_shape
        node.pl_type=node.body.pl_type

    def visit_PLCall(self, node, ctx={}):
        # breakpoint()
        func_name = node.func.name
        if func_name in ctx:
            func_def_node = ctx[func_name][2]
            node.func_def_node = func_def_node  # register the def node in nodes so that chaining rewriter can read it without passing ctx objects
            for i in range(len(node.args)):
                self.visit(node.args[i],
                           ctx)  
                # breakpoint()
                func_def_node.args[i].pl_type = node.args[i].pl_type
                func_def_node.args[i].pl_shape = node.args[i].pl_shape

            self.visit(func_def_node, ctx)  # Add the for loop inside the func_def, don't need to propagate up.

            node.pl_type = func_def_node.return_type
            node.pl_shape = func_def_node.return_shape

        elif func_name == 'len':
            if len(node.args) != 1:
                print(f'Function {func_name} should only have one parameter!')
                raise TypeError

            if isinstance(node.args[0], PLVariable):
                var_name = node.args[0].name
                num_indice = 0
            elif isinstance(node.args[0], PLSubscript):
                var_name = node.args[0].var.name
                num_indice = len(node.args[0].indices)
            else:
                print(f'Object of type {node.args[0]} has no len()!')
                raise TypeError

            if ctx[var_name][1] == ():
                print(f'Object of type {ctx[var_name][0]} has no len()')
                raise TypeError

            length = PLConst(ctx[var_name][1][num_indice])
            length.pl_type = PLType('int')
            length.pl_shape = ()
            replace_child(node.parent, node, length)
        elif func_name == 'range':
            return
        else:
            print(f'Function {func_name} called before definition!')
            raise NameError

    def check_ip_inputs(self, node):
        global_ip = IPinforms.Global_IP_args[node.name]

        if len(node.dims) != len(global_ip['dim']):
            # check if the number of the inputs is correct
            print(f'The input number of IP {node.name} is incorrect!')
            raise NameError

        for i in range(len(node.dims)):
            # check if the dimensions of the inputs are correct
            if global_ip['dim'][i] != node.dims[i]:
                input_name = node.args[i].name
                global_dim = global_ip['dim'][i]
                current_dim = node.dims[i]
                print("Note that dimension =0 indicates scalar and >1 indicates array")
                print(f'The dimension of input {input_name} should be {global_dim} instead of {current_dim}!')
                raise NameError
        
        # check types
        for i in range(len(node.dims)):
            if global_ip['type'][i] in node.func_configs:
                # check if the data types are consistent    
                global_ty = node.func_configs[global_ip['type'][i]]
                current_ty = node.types[i]
                input_name = node.args[i].name
                if(current_ty != global_ty):
                    print(f'The type of input {input_name} should be {global_ty} instead of {current_ty}!')
                    raise NameError
            else:
                if (global_ip['type'][i][0]=='d'):
                    # if begin with "d", the type should be configured
                    node.func_configs[global_ip['type'][i]] = node.types[i]
                else:
                    # deal with fixed types like int, void ...
                    global_ty = global_ip['type'][i]
                    current_ty = node.types[i]
                    input_name = node.args[i].name

                    if ( global_ty != current_ty):
                        print(f'The type of input {input_name} should be {global_ty} instead of {current_ty}!')
                        raise NameError
        
        # check shapes
        for i in range(len(node.dims)):
            if self.debug:
                if (node.dims[i]==0):
                    print("input is a scalar, nothing to do")
            
            # input is a one-dimensional array
            if (node.dims[i]==1):
                if global_ip['shape'][i] in node.func_configs:
                    # check if the data shape are consistent    
                    global_sp = node.func_configs[global_ip['shape'][i]]
                    current_sp = node.shapes[i][0]
                    input_name = node.args[i].name
                    if(current_sp != global_sp):
                        print(f'The shape of input {input_name} should be {global_sp} instead of {current_sp}!')
                        raise NameError
                else:
                    if (global_ip['shape'][i][0]=='s') :
                        # if begin with "s", the shape should be configured
                        node.func_configs[global_ip['shape'][i]] = node.shapes[i][0]
            
            # the input dimension is >1
            if (node.dims[i]>1):
                for j in range(node.dims[i]):
                    if global_ip['shape'][i][j] in node.func_configs:
                        # print("enter")
                        # check if the data shape are consistent    
                        global_sp = node.func_configs[global_ip['shape'][i][j]]
                        current_sp = node.shapes[i][j]
                        input_name = node.args[i].name
                        if self.debug:
                            print(input_name)
                            print(global_sp)
                            print(current_sp)
                        if(current_sp != global_sp):
                            print(f'The size of dimension {j} of input {input_name} should be {global_sp} instead of {current_sp}!')
                            raise NameError
                    else:
                        if (global_ip['shape'][i][j][0]=='s') :
                            # if begin with "s", the shape should be configured
                            node.func_configs[global_ip['shape'][i][j]] = node.shapes[i][j]
        if self.debug:
            print(node.func_configs)


    def calculate_ip_return(self, node):
        global_ip_ret = IPinforms.Global_IP_args[node.name]['ret']
        if (global_ip_ret[0]=='d'):
            return PLType( node.func_configs[global_ip_ret[0]],0), () 
        if (global_ip_ret =='void'):
            return PLType('void', 0) , ()
        else :
            return PLType( global_ip_ret, 0) , ()     

    ## have not consider the situation that argmax(1, a+2), a is not defined
    ## have not consider the input is constant such as np.testip(m,m,m,m,5)
    ## have not consider IP shape is fixed
    def visit_PLIPcore(self, node, ctx={}):
        if self.debug:
            print("\n ctx")
            print(ctx)
            print("\n args")
            print(node.args)

        node.types = []
        node.shapes = []
        node.dims = []

        for a in node.args:
            self.visit(a, ctx)
            if(isinstance(a, PLVariable)):
                if a.name not in ctx:
                    print(f'Input argument {a.name} of IP {node.name} called before definition!')
                    raise NameError
            node.types.append(a.pl_type.ty)
            node.shapes.append(a.pl_shape)
            node.dims.append(a.pl_type.dim)

        if self.debug:
            print(node.types)
            print(node.shapes)
            print(node.dims)
            print(type(node.shapes[0]))
        
        self.check_ip_inputs(node)
        node.pl_type, node.pl_shape  = self.calculate_ip_return(node)


    def actual_shape(self, shape):
        # return a new tuple without 1's tuple
        # (1,4,6,1,1,5) -> (4,6,5) represents the actual shape
        return tuple(i for i in shape if i != 1)

    # Indices could be an array
    def visit_PLSubscript(self, node, ctx={}):
        array_name = node.var.name
        if array_name in ctx:
            array_dims = ctx[array_name][0].dim
            array_shape = ctx[array_name][1]
            decl_node = ctx[array_name][2]

            if array_dims == 0:
                node.is_offset = True
                node.var.is_offset = True

            lambda_arg = hasattr(decl_node, 'lambda_node')

            subscript_dim = len(node.indices)

            if self.debug:
                # print(f'Type: >>>>>>>>>>>> {type(node.indices[0])}')
                print(f'Type: >>>>>>>>>>>> {type(node.indices)}')
                print(f'Type: >>>>>>>>>>>> {len(node.indices)}')

            if not lambda_arg:
                # allow an extra dimension for bit access
                if 'fixed' in ctx[array_name][0].ty:
                    assert (subscript_dim < (array_dims + 2))
                else:
                    assert (subscript_dim < (array_dims + 1))
            # node.pl_type = ctx[array_name][0] - subscript_dim
            # node.pl_shape = ctx[array_name][1][:-subscript_dim]

            if subscript_dim == (array_dims + 1):
                # bit-wise range access
                # last index (extra dimension) used as range function
                # implemented as function call, which replaces original object
                # in the node tree
                print(">>>>>>>>>>>>>>>>BIT ACCESS")
                indices = node.indices
                parent = node.parent
                range_arg = indices.pop()
                range_fn = PLCall(func=PLVariable('range'),
                                  args=[range_arg.lower, range_arg.upper],
                                  is_method=True,
                                  obj=node)

                replace_child(node.parent, node, range_fn)
                node = range_fn

                self.visit(node.obj, ctx)  # not dealing with chaining propagation here
                for i in range(len(node.args)):
                    self.visit(node.args[i], ctx)  # not dealing with chaining propagation here (array as subscription)

                node.pl_type = PLType('bit', 0)
                node.pl_shape = ()

            else:
                shape = ()
                indices = node.indices
                is_empty = False
                if self.debug:
                    print(">>>>>>>>>>>>>>>>")
                for i in range(len(indices)):
                    # indices[i].parent = node
                    # the length along that dimension
                    if hasattr(node, 'is_offset'):
                        indices[i].is_offset = True
                    else:
                        indices[i].dim_length = array_shape[i]
                    if self.debug:
                        print('VISITING INDICS')
                        print(f'{type(indices[i])}')
                    self.visit(indices[i], ctx)  # not dealing with chaining propagation here
                    idx_shape = indices[i].pl_shape
                    if idx_shape == (0,):
                        is_empty = True
                    elif idx_shape == ():
                        shape += (1,)
                    else:
                        shape += indices[i].pl_shape
                if self.debug:
                    print("<<<<<<<<<<<<<<<<<<<")
                if is_empty:
                    node.pl_type = PLType(ctx[array_name][0].ty, None)
                    node.pl_shape = None
                else:
                    valid_dims = len(self.actual_shape(shape))
                    node.pl_type = PLType(ctx[array_name][0].ty, valid_dims)
                    node.pl_shape = shape

        else:
            print(f'{array_name} used before definition!')
            raise NameError

    def visit_PLLambda(self, node, ctx={}):

        node.pl_type = PLType('pl_lambda', 0)
        node.pl_shape = ()

        if all(hasattr(arg, 'pl_type') for arg in node.args):
            local_ctx = copy.copy(ctx)
            for arg in node.args:
                arg.lambda_node = node

                local_ctx[arg.name] = (arg.pl_type, arg.pl_shape, arg)

            self.visit(node.body,
                       local_ctx)  
            node.return_type = node.body.pl_type
            node.return_shape = node.body.pl_shape

    def visit_PLMap(self, node, ctx={}):

        for array in node.arrays:
            self.visit(array, ctx)

        iter_dom_type = node.arrays[0].pl_type
        iter_dom_shape = node.arrays[0].pl_shape

        if self.debug:
            print(f'iter_dom_shape: {iter_dom_shape}')

        for array in node.arrays:
            if self.debug:
                print(f'array.pl_shape: {array.pl_shape}')
            assert (self.actual_shape(iter_dom_shape) == \
                    self.actual_shape(array.pl_shape))

        # in plmap, the args of lambda function are all scalars
        # since plmap iterates through each element in arrays
        for i in range(len(node.func.args)):
            elem_type = node.arrays[i].pl_type
            node.func.args[i].pl_type = PLType(elem_type.ty, 0)
            node.func.args[i].pl_shape = ()

        self.visit(node.func, ctx)

        map_return_type = node.func.return_type + \
                          len(self.actual_shape(iter_dom_shape))
        map_return_shape = node.func.return_shape + iter_dom_shape

        if self.debug:
            print(f'plmap: return type : {map_return_type}')
            print(f'plmap: return shape: {map_return_shape}')

        node.pl_type = map_return_type
        node.pl_shape = map_return_shape

    def visit_PLDot(self, node, ctx={}):
        self.visit(node.op1, ctx)
        self.visit(node.op2, ctx)

        op1_actual_shape = self.actual_shape(node.op1.pl_shape)
        op2_actual_shape = self.actual_shape(node.op2.pl_shape)

        assert (op1_actual_shape == op2_actual_shape)

        node.op_type = PLType(ty=node.op1.pl_type.ty,
                              dim=op1_actual_shape)
        node.op_shape = op1_actual_shape

        node.pl_type = PLType(node.op1.pl_type.ty, 0)
        node.pl_shape = ()

        node.return_type = PLType(node.op1.pl_type.ty, 0)
        node.return_shape = ()

    # def visit_PLAttribute(self, node, ctx={}):

    #     if node.attr = 'shape':
    #         node.
