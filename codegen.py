import copy
from nodes import *
from cgen.c_ast import *
from cgen.pylog_cast import *
from cgen.c_generator import *
from typer import PLType
import IPanalyzer


def filter_none(lst):
    return list(filter(None, lst))


def is_in_chaining(node):
    if isinstance(node, PLChainingTop):
        return True
    while hasattr(node, 'parent'):
        node = node.parent
        if isinstance(node, PLChainingTop):
            return True
    return False


class CCode:
    def __init__(self, debug=False):
        self.debug = debug
        self.ast = None
        # Global statements, before top function
        self.global_stmt = []

        # Top function
        self.top = []

    def __add__(self, ast):
        self.append(ast)
        return self

    def append_global(self, ext):
        assert (isinstance(ext, (c_ast.Decl, c_ast.Typedef, c_ast.FuncDef)))
        self.global_stmt.append(ext)

    def append(self, ast):
        if isinstance(ast, c_ast.Node):
            self.top.append(ast)
        elif isinstance(ast, list):
            self.top.extend(ast)
        else:
            raise NotImplementedError

    def update(self):
        self.ast = c_ast.FileAST()
        self.ast.ext = self.global_stmt + self.top
        return self.ast

    def show(self):
        self.update()
        self.ast.show(attrnames=True, nodenames=True)

    def cgen(self):
        self.update()
        if self.debug:
            print("C AST: ")
            self.ast.show(attrnames=True, nodenames=True, showcoord=False)
        generator = CGenerator()
        if self.debug:
            print("Start C Code generation.")
        return generator.visit(self.ast)


class PLCodeGenerator:
    def __init__(self, arg_info=None,
                       backend='vhls',
                       board='ultra96',
                       debug=False):
        self.cc = CCode(debug=debug)
        self.arg_info = arg_info
        self.backend = backend # backend flow, e.g. vhls, merlin, etc.
        self.debug = debug
        self.board = board
        self.num_mem_ports = 4
        self.recordip = 0
        self.max_idx = 1
    ##@@ project_path
    def codegen(self, node, project_path, config=None):
        self.project_path = project_path
        self.cc += self.visit(node, config)
        c_code = self.cc.cgen()
        if self.board == 'aws_f1' or self.board.startswith('alveo'):
            c_code = 'extern "C" {\n' + c_code + '\n}\n'

        if self.recordip > 0:
            self.ccode = self.include_code(True) + c_code
        else:
            self.ccode = self.include_code(False) + c_code

        return self.ccode

    def include_code(self, ip_header=False):
        if ip_header:
            header_files = ['ap_int.h', 'ap_fixed.h', 'hls_math.h', 'configured_IPcores.h']
        else:
            header_files = ['ap_int.h', 'ap_fixed.h', 'hls_math.h']
        return ''.join([ f'#include "{f}"\n' for f in header_files]) + '\n'

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
        if self.debug:
            print(f'CODEGEN visiting {node.__class__.__name__}: {node}')
        visit_return = visitor(node, config)
        return visit_return

    def generic_visit(self, node, config=None):
        """Called if no explicit visitor function exists for a node."""
        # visit children
        if isinstance(node, PLNode):
            for field, value in self.iter_fields(node):
                if value != None:
                    self.visit(value, config)
        elif isinstance(node, list):
            for item in node:
                if item != None:
                    self.visit(item, config)

    def visit_int(self, node, config=None):
        return node

    def visit_str(self, node, config=None):
        return node

    def visit_list(self, node, config=None):
        stmt_list = []

        for e in node:
            stmt = self.visit(e, config)
            if isinstance(stmt, list):
                stmt_list += stmt
            else:
                stmt_list.append(stmt)
        return filter_none(stmt_list)

    '''TODO: other constant types'''

    def visit_PLConst(self, node, config=None):
        if isinstance(node.value, int):
            return Constant(type="int", value=str(node.value))
        elif isinstance(node.value, float):
            return Constant(type="float", value=str(node.value))
        elif isinstance(node.value, bool):
            return Constant(type="int", value='1' if node.value else '0')
        elif isinstance(node.value, str):
            return node.value
        else:
            print(f'visit_PLConst: Type: {type(node.value)}')
            raise NotImplementedError

    # def visit_PLArray(self, node, config=None):
    #     pass

    def visit_PLArrayDecl(self, node, config=None):
        dims = [self.visit(e, config) for e in node.dims.elts]
        return array_decl(var_type=node.ele_type,  # string
                          name=self.visit(node.name, config).name,
                          dims=dims)
        # dims=self.visit(node.dims, config))

    def visit_PLVariableDecl(self, node, config=None):
        var = var_decl(var_type=node.ty,
                       name=self.visit(node.name, config).name,
                       init=self.visit(node.init, config))
        return var

    def visit_PLVariable(self, node, config=None):
        if (config is not None) and ('arg_map' in config):
            if node.name in config['arg_map']:
                # return config['arg_map'][node.name]
                return self.visit(config['arg_map'][node.name], config)
        return ID(node.name)

    def visit_PLUnaryOp(self, node, config=None):
        return UnaryOp(op=node.op,
                       expr=self.visit(node.operand, config))

    def get_subscript(self, op_node, iter_prefix='i', \
                      return_plnode=False, config=None):

        assert (isinstance(op_node, (PLSubscript, PLVariable)))

        def VarNode(*args, **kwargs):
            if return_plnode:
                return PLVariable(*args, **kwargs)
            else:
                return ID(*args, **kwargs)

        def const32(*args, **kwargs):
            if return_plnode:
                return PLConst(*args, **kwargs)
            else:
                return int32(*args, **kwargs)

        target_shape = len(op_node.pl_shape)

        if isinstance(op_node, PLSubscript):
            array_name = self.visit(op_node.var, config)
            subs = []
            for i in range(len(op_node.pl_shape)):
                if op_node.pl_shape[i] == 1:
                    if isinstance(op_node.indices[i], PLSlice):
                        idx, _, _ = op_node.indices[i].updated_slice
                        subs.append(const32(idx))
                    else:
                        if return_plnode:
                            subs.append(op_node.indices[i])
                        else:
                            subs.append(self.visit(op_node.indices[i], config))
                else:
                    if isinstance(op_node.indices[i], PLSlice):
                        bounds = op_node.indices[i].updated_slice
                        lower, upper, step = bounds

                        if lower == 0:
                            if step == 1:
                                subs.append(VarNode(f'{iter_prefix}{i}'))
                            else:
                                subs.append(VarNode(
                                    f'({iter_prefix}{i}*({step}))'))
                        else:
                            if step == 1:
                                subs.append(VarNode(
                                    f'({lower}+{iter_prefix}{i})'))
                            else:
                                subs.append(VarNode(
                                    f'({lower}+{iter_prefix}{i}*({step}))'))
                    else:
                        subs.append(VarNode(f'{iter_prefix}{i}'))

            if return_plnode:
                target = PLSubscript(var=op_node.var,
                                     indices=subs)
            else:
                target = subscript(array_name=array_name,
                                   subscripts=subs)

        else:
            array_name = VarNode(op_node.name)

            subs = [VarNode(f'{iter_prefix}{i}') for i in range(target_shape)]
            if return_plnode:
                target = PLSubscript(var=op_node,
                                     indices=subs)
            else:
                target = subscript(array_name=array_name,
                                   subscripts=subs)

        return target

    def visit_PLChainingTop(self, node, config=None):
        stmt = self.visit(node.stmt)
        declaration = None
        if isinstance(stmt, list) and len(stmt) > 1:
            assert (len(stmt) == 2 and isinstance(stmt[0], Decl))
            declaration = stmt[0]
            stmt = [stmt[1]]
        else:
            stmt = [stmt]

        for i in range(len(node.pl_shape) - 1, -1, -1):
            if not any([node.pl_shape[idx] != 1 for idx in range(0, i + 1)]):
                break
                # omitting the indices at the beginning if their bounds
                # are [0,1)
            stmt = [simple_for(iter_var=f'i_chaining_{i}',
                               start=int32(0),
                               op='<',
                               end=int32(node.pl_shape[i]),
                               step=int32(1),
                               stmt_lst=stmt)]
        if declaration is not None:
            return [declaration, stmt[0]]
        else:
            return stmt[0]

    def visit_PLBinOp(self, node, config=None):

        if (not hasattr(node, 'pl_shape')) or (node.pl_shape == ()):
            binop = BinaryOp(op=node.op,
                             left=self.visit(node.left, config),
                             right=self.visit(node.right, config))
            return binop
        elif len(node.pl_shape) > 0 and not is_in_chaining(node):
            # loop body

            target = self.get_subscript(node.assign_target, 'i_bop_', config)
            if node.left.pl_shape != ():
                lvalue = self.get_subscript(node.left, 'i_bop_', config)
            else:
                lvalue = self.visit(node.left, config)

            if node.right.pl_shape != ():
                rvalue = self.get_subscript(node.right, 'i_bop_', config)
            else:
                rvalue = self.visit(node.right, config)

            nd_binop = BinaryOp(op=node.op,
                                left=lvalue,
                                right=rvalue)

            stmt = [Assignment(op=node.assign_op, \
                               lvalue=target, \
                               rvalue=nd_binop)]

            for i in range(len(node.pl_shape) - 1, -1, -1):
                stmt = [simple_for(iter_var=f'i_bop_{i}',
                                   start=int32(0),
                                   op='<',
                                   end=int32(node.pl_shape[i]),
                                   step=int32(1),
                                   stmt_lst=stmt)]

            return stmt[0]
        else:
            raise NotImplementedError

    def visit_PLCall(self, node, config=None):
        el = ExprList(exprs=[self.visit(e, config) for e in node.args])
        if node.is_method:
            return FuncCall(
                name=StructRef(name=self.visit(node.obj, config), type='.', \
                               field=self.visit(node.func, config)), \
                args=el)
        else:
            return FuncCall(name=self.visit(node.func, config), args=el)

    def visit_PLIPcore(self, node, config=None):
        el = ExprList(exprs=[ self.visit(e, config) for e in node.args ])
        IPanalyzer.ip_generator(node, self.project_path, self.recordip)
        self.recordip = self.recordip + 1
        return FuncCall(name=ID(node.name+'_'+str(self.recordip-1)), args=el)

    def visit_PLIfExp(self, node, config=None):
        top = TernaryOp(cond=self.visit(node.test, config),
                        iftrue=self.visit(node.body, config),
                        iffalse=self.visit(node.orelse, config))
        return top

    def visit_PLSubscript(self, node, config=None):

        if isinstance(node.var, PLSubscript):
            array_name = self.visit(node.var.var, config)
            subscripts = []
            for i in range(len(node.indices)):
                # if len(node.var.indices)<=i:
                #     rhs=0
                #     # in case of a subscript to a partial subscript,
                #     # the node.var is at least 1 dimensional array
                #     # (vector) with a few 1 at the beginning of its
                #     # pl_shape but the indices is shorter because the
                #     # non-subscript parts do not need an index.
                #     # In this case, we add a zero for them
                # else:
                #     rhs=node.var.indices[i]
                plbinop = PLBinOp(op='+',
                                  left=node.indices[i],
                                  right=node.var.indices[i])

                binop = self.visit(plbinop, config)
                subscripts.append(binop)

        else:
            array_name = self.visit(node.var, config)
            subscripts = [self.visit(idx, config) for idx in node.indices]

        sub = subscript(array_name=array_name,
                        subscripts=subscripts)
        return sub

        # if hasattr(node, 'is_offset'):
        #     if (config is not None) and ('arg_map' in config):
        #         if node.var.name in config['arg_map']:
        #             # return config['arg_map'][node.name]
        #             actual_var = config['arg_map'][node.var.name]
        #             print(f'1234 actual_var: {actual_var}')
        # else:
        #     sub = subscript(array_name=self.visit(node.var, config),
        #                     subscripts=[ self.visit(idx, config) \
        #                                             for idx in node.indices])
        #     return sub

        # obj = self.visit(node.var, config)
        # for index in node.indices:
        #     obj = ArrayRef(name=obj, subscript=self.visit(index, config))

        # return obj

    '''TODO'''

    def visit_PLSlice(self, node, config=None):
        # assuming slice has been parsed by other module and the final
        # length is equal to 1 (always return the first nubmer)
        if node.lower:
            return self.visit(node.lower, config)
        else:
            return int32(0)

    def visit_PLAssign(self, node, config=None):
        #TODO: the compound assign operator can be transcripted correctly now,
        # such as -=, +=, but we don't know them in the compiler flow. Do we
        # need to break them down to assign with children lhs and binop rhs?
        target_c_obj = self.visit(node.target, config)
        assign_dim = node.target.pl_type.dim
        decl = None

        # generate declaration statement
        if node.is_decl:
            if (assign_dim == 0 and not is_in_chaining(node)) or \
               (is_in_chaining(node) and \
                    not isinstance(node.target, PLSubscript)):
                # in the second situation, though this assign node is in a
                # chaining subtree, the lhs variable is not PLSubscript means
                # it is originally an scalar instead of an array and should
                # follow this branch.
                if isinstance(node.value, (PLMap, PLFor, PLAssign)):
                    decl = var_decl(var_type=node.target.pl_type.ty,
                                    name=target_c_obj.target.name,
                                    init=None)
                    map_expr = self.visit(node.value, config)
                    return [decl, map_expr]
                else:
                    decl = var_decl(var_type=node.target.pl_type.ty,
                                    name=target_c_obj.name,
                                    init=self.visit(node.value, config))
                    return decl

            elif assign_dim > 0 or is_in_chaining(node):
                if is_in_chaining(node):
                    # lhs variable is actually an array but in the guise of
                    # PLSubscript due to chaining goes to get the information
                    # from the var field of the PLSubscript
                    dims = [int32(s) for s in node.target.var.pl_shape]
                    name = target_c_obj.name
                    # target_c_obj.name is ArrayRef and includes name and
                    # subscript
                    while not isinstance(name, str):
                        name = name.name
                    decl = array_decl(var_type=node.target.var.pl_type.ty,
                                      name=name,
                                      dims=dims)
                else:
                    dims = [int32(s) for s in node.target.pl_shape]

                    decl = array_decl(var_type=node.target.pl_type.ty,
                                      name=target_c_obj.name,
                                      dims=dims)

            else:
                raise NotImplementedError

        # generate assignment statement
        if assign_dim == 0:
            asgm = Assignment(op=node.op,
                              lvalue=target_c_obj,
                              rvalue=self.visit(node.value, config))
        elif assign_dim > 0:
            assert (not is_in_chaining(node))
            if isinstance(node.value, (PLConst, PLVariable)):
                if isinstance(node.value, PLVariable):
                    rvalue = self.get_subscript(node.value, 'i_asg_', config)
                else:
                    rvalue = self.visit(node.value, config)

                lvalue = self.get_subscript(node.target, 'i_asg_', config)

                stmt = [Assignment(op=node.op,
                                   lvalue=lvalue,
                                   rvalue=rvalue)]

                for i in range(len(node.pl_shape) - 1, -1, -1):
                    stmt = [simple_for(iter_var=f'i_asg_{i}',
                                       start=int32(0),
                                       op='<',
                                       end=int32(node.pl_shape[i]),
                                       step=int32(1),
                                       stmt_lst=stmt)]

                asgm = stmt[0]

            else:
                if isinstance(node.value, list):
                    for obj in node.value:
                        obj.assign_target = node.target
                        obj.assign_op = node.op
                else:
                    node.value.assign_target = node.target
                    node.value.assign_op = node.op

                asgm = self.visit(node.value, config)
                # not explicitly generate Assignment
        else:
            raise NotImplementedError

        if decl:
            return [decl] + asgm if isinstance(asgm, list) else [decl, asgm]
        else:
            return asgm

    def visit_PLIf(self, node, config=None):
        obj_body = self.visit(node.body, config)
        obj_orelse = self.visit(node.orelse, config)
        if_body = Compound(block_items=obj_body) if obj_body else None
        if_orelse = Compound(block_items=obj_orelse) if obj_orelse else None
        if_stmt = If(cond=self.visit(node.test, config),
                     iftrue=if_body,
                     iffalse=if_orelse)
        return if_stmt

    def visit_PLFor(self, node, config=None):
        pliter_dom = node.iter_dom
        iter_var = self.visit(node.target, config)
        sim_for = simple_for(iter_var=iter_var.name,
                             start=self.visit(pliter_dom.start, config),
                             op=pliter_dom.op,
                             end=self.visit(pliter_dom.end, config),
                             step=self.visit(pliter_dom.step, config),
                             stmt_lst=self.visit(node.body, config))

        if pliter_dom.attr:
            if self.backend == 'vhls':
                insert_pragma(compound_node=sim_for.stmt,
                              pragma=pliter_dom.attr,
                              attr=(self.visit(pliter_dom.attr_args[0], config)
                                    if pliter_dom.attr_args else None))
            elif self.backend == 'merlin':
                merlin_pragma = get_merlin_pragma(
                              pragma=pliter_dom.attr,
                              attr=(self.visit(pliter_dom.attr_args[0], config)
                                    if pliter_dom.attr_args else None))

                sim_for = [merlin_pragma, sim_for]

        return sim_for

    def visit_PLWhile(self, node, config=None):
        while_body = Compound(block_items=self.visit(node.body, config))
        while_stmt = While(cond=self.visit(node.test, config),
                           stmt=while_body)
        # ignoring the orelse branch in PLWhile node. 
        # TODO: support orelse
        return while_stmt

    # TODO: correctly handle nested functions definitions
    def visit_PLFunctionDef(self, node, config=None):

        if not hasattr(node, 'type_infer_done'):
            return

        arg_list = []

        for arg in node.args:
            if hasattr(arg, 'pl_type') and hasattr(arg, 'pl_shape'):
                if arg.pl_shape == (1,):
                    arg_list.append(var_decl(
                        var_type=arg.pl_type.ty,
                        name=self.visit(arg, config).name))
                else:
                    arg_list.append(
                        array_decl(var_type=arg.pl_type.ty,
                                   name=self.visit(arg, config).name,
                                   dims=[int32(e) for e in arg.pl_shape]))

            else:
                arg_list.append(array_decl(var_type="float",
                                           name=self.visit(arg, config).name,
                                           dims=[None] * 2))

        fd = func_def(
            func_name=node.name,
            args=arg_list,
            func_type=node.return_type.ty,
            body=self.visit(node.body, config))

        if node.decorator_list:
            decorator_names = [e.name if isinstance(e, PLVariable) \
                                   else e.func.name \
                               for e in node.decorator_list]
            if "pylog" in decorator_names:
                self.top_func_name = node.name
                self.return_void = (node.return_type.ty == 'void')

                if self.backend == 'vhls':
                    if self.arg_info != None:
                        max_idx = insert_interface_pragmas(
                            compound_node=fd.body,
                            interface_info=self.arg_info,
                            num_mem_ports=self.num_mem_ports)
                        self.max_idx = max_idx
                elif self.backend == 'merlin':
                    merlin_kernel_pragma = c_ast.Pragma('ACCEL kernel')
                    fd = [merlin_kernel_pragma, fd]
                return fd
        else:
            self.cc.append_global(fd)

    def visit_PLPragma(self, node, config=None):
        # print(type(node.pragma))
        return Pragma(self.visit(node.pragma, config))

    '''TODO'''

    def visit_PLLambda(self, node, config=None):
        if hasattr(node, 'arg_map') and hasattr(node, 'target'):
            new_config = copy.deepcopy(config)
            if new_config is None:
                new_config = {'arg_map': node.arg_map,
                              'target': node.target}
            else:
                new_config['arg_map'] = node.arg_map
                new_config['target'] = node.target

        else:
            new_config = config

        assert (isinstance(node.body, PLAssign))
        stmts = self.visit(node.body, new_config)

        if not isinstance(stmts, list):
            stmts = [stmts]
        return stmts

    def visit_PLReturn(self, node, config=None):
        return Return(expr=self.visit(node.value, config))

    '''TODO'''

    def visit_PLMap(self, node, config=None):
        args_subs = []
        for array in node.arrays:
            args_subs.append(self.get_subscript(array, 'i_map_', True, config))

        target_subs = self.get_subscript(node.target, 'i_map_', \
                                         return_plnode=True, config=config)
        lambda_args = [arg.name for arg in node.func.args]

        target_subs.pl_type = PLType(node.pl_type.ty, 0)
        target_subs.pl_shape = (1 for i in node.pl_shape)  # assuming scalar

        node.func.arg_map = dict(zip(lambda_args, args_subs))
        node.func.target = target_subs

        lambda_func_body = node.func.body
        assert (not isinstance(lambda_func_body, PLAssign))
        # create a PLAssign node to assign original expression in lambda
        # function body to the map target

        new_lambda_body = PLAssign(op='=',
                                   target=target_subs,
                                   value=lambda_func_body)

        new_lambda_body.is_decl = False

        node.func.body = new_lambda_body
        stmt = self.visit(node.func, config)

        # for i in range(len(node.pl_shape)-1, -1, -1):
        for i in range(node.pl_type.dim - 1, -1, -1):
            stmt = [simple_for(iter_var=f'i_map_{i}',
                               start=int32(0),
                               op='<',
                               end=int32(node.pl_shape[i]),
                               step=int32(1),
                               stmt_lst=stmt)]

        return stmt[0]

    # '''TODO'''
    # def visit_PLDot(self, node, config=None):

    #     var_decl = PLVariableDecl(ty=node.pl_type.ty,
    #                               name=PLVariable('tmp_dot'),
    #                               init=PLConst(0))

    #     op1_subs = self.get_subscript(node.op1, 'i_dot_', True, config)
    #     op2_subs = self.get_subscript(node.op2, 'i_dot_', True, config)

    #     mult = PLBinOp(op='*',
    #                    left=op1_subs,
    #                    right=op2_subs)

    #     stmt = [ PLAssign(op='+=',
    #                       target=PLVariable('tmp_dot'),
    #                       value=mult) ]

    #     for i in range(len(node.pl_shape)-1, -1, -1):
    #         stmt = [ simple_for(iter_var=f'i_dot_{i}',
    #                             start=int32(0),
    #                             op='<',
    #                             end=int32(node.pl_shape[i]),
    #                             step=int32(1),
    #                             stmt_lst=stmt) ]

    #     return stmt[0]
