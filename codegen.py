
from nodes import *
from cgen.c_ast import *
from cgen.pylog_cast import *
from cgen.c_generator import *

def filter_none(lst):
    return list(filter(None, lst))

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
        assert(isinstance(ext, (c_ast.Decl, c_ast.Typedef, c_ast.FuncDef)))
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
    def __init__(self, arg_info=None, debug=False):
        self.cc = CCode(debug=debug)
        self.arg_info = arg_info

    def codegen(self, node, config=None):
        self.cc += self.visit(node, config)
        self.ccode = self.include_code() + self.cc.cgen()
        return self.ccode

    def include_code(self):
        header_files = ['ap_int.h', 'ap_fixed.h']
        return ''.join([ f'#include "{f}"\n' for f in header_files])

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
            stmt = self.visit(e)
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
            raise NotImplementedError

    # def visit_PLArray(self, node, config=None):
    #     pass

    def visit_PLArrayDecl(self, node, config=None):
        dims = [ self.visit(e) for e in node.dims.elts ]
        return array_decl(var_type=node.ele_type, # string
                          name=self.visit(node.name).name,
                          dims=dims)
                          # dims=self.visit(node.dims))

    def visit_PLVariableDecl(self, node, config=None):
        var = var_decl(var_type=node.ty,
                       name=self.visit(node.name).name,
                       init=self.visit(node.init))
        return var

    def visit_PLVariable(self, node, config=None):
        return ID(node.name)

    def visit_PLUnaryOp(self, node, config=None):
        return UnaryOp(op=node.op,
                       expr=self.visit(node.operand))

    def visit_PLBinOp(self, node, config=None):

        def get_subscript(op_node):

            target_shape = len(op_node.pl_shape)

            if isinstance(op_node, PLSubscript):
                array_name = self.visit(op_node.var)
                subs       = []
                for i in range(len(op_node.pl_shape)):
                    if op_node.pl_shape[i] == 1:
                        if isinstance(op_node.indices[i], PLSlice):
                            idx, _, _ = op_node.indices[i].updated_slice
                            subs.append(int32(idx))
                        else:
                            subs.append(self.visit(op_node.indices[i]))
                    else:
                        if isinstance(op_node.indices[i], PLSlice):
                            bounds = op_node.indices[i].updated_slice
                            lower, upper, step = bounds
                            subs.append(ID(f'({lower}+i_bop_{i}*({step}))'))
                        else:
                            subs.append(ID(f'i_bop_{i}'))

                target = subscript(array_name=array_name,
                                   subscripts=subs[::-1])

            else:
                array_name = ID(op_node.name)
                subs = [ ID(f'i_bop_{i}') for i in range(target_shape) ]
                target = subscript(array_name=array_name,
                                   subscripts=subs[::-1])

            return target

        if (not hasattr(node, 'pl_shape')) or (node.pl_shape == ()):
            binop = BinaryOp(op=node.op,
                             left=self.visit(node.left),
                             right=self.visit(node.right))
            return binop
        elif len(node.pl_shape) > 0:
            # loop body

            target = get_subscript(node.assign_target)
            if node.left.pl_shape != ():
                lvalue = get_subscript(node.left)
            else:
                lvalue = self.visit(node.left)

            if node.right.pl_shape != ():
                rvalue = get_subscript(node.right)
            else:
                rvalue = self.visit(node.right)

            nd_binop = BinaryOp(op=node.op,
                                left=lvalue,
                                right=rvalue)

            stmt = [ Assignment(op=node.assign_op, \
                                lvalue=target,     \
                                rvalue=nd_binop) ]

            for i in range(len(node.pl_shape)-1, -1, -1):
                stmt = [ simple_for(iter_var=f'i_bop_{i}',
                                    start=int32(0),
                                    op='<',
                                    end=int32(node.pl_shape[i]),
                                    step=int32(1),
                                    stmt_lst=stmt) ]

            return stmt[0]
        else:
            raise NotImplementedError


    def visit_PLCall(self, node, config=None):
        el = ExprList(exprs=[ self.visit(e) for e in node.args ])
        return FuncCall(name=self.visit(node.func), args=el)


    def visit_PLIfExp(self, node, config=None):
        top = TernaryOp(cond=self.visit(node.test),
                        iftrue=self.visit(node.body),
                        iffalse=self.visit(node.orelse))
        return top

    def visit_PLSubscript(self, node, config=None):
        sub = subscript(array_name=self.visit(node.var),
                        subscripts=[ self.visit(idx) for idx in node.indices ])
        return sub
        # obj = self.visit(node.var)
        # for index in node.indices:
        #     obj = ArrayRef(name=obj, subscript=self.visit(index))

        # return obj

    '''TODO'''
    def visit_PLSlice(self, node, config=None):
        pass

    def visit_PLAssign(self, node, config=None):

        target_c_obj = self.visit(node.target)
        assign_dim = node.target.pl_type.dim
        decl = None

        if node.is_decl:
            if assign_dim == 0:
                decl = var_decl(var_type=node.target.pl_type.ty,
                                name=target_c_obj.name,
                                init=self.visit(node.value))
                return decl

            elif assign_dim > 0:
                dims = [ int32(s) for s in node.target.pl_shape ]

                decl = array_decl(var_type=node.target.pl_type.ty,
                                  name=target_c_obj.name,
                                  dims=dims)

            else:
                raise NotImplementedError

        if assign_dim == 0:
            asgm = Assignment(op=node.op,
                              lvalue=target_c_obj,
                              rvalue=self.visit(node.value))
        elif assign_dim > 0:
            node.value.assign_target = node.target
            node.value.assign_op     = node.op
            asgm = self.visit(node.value)

        else:
            raise NotImplementedError

        if decl:
            return [decl, asgm]
        else:
            return asgm

    def visit_PLIf(self, node, config=None):
        obj_body = self.visit(node.body)
        obj_orelse = self.visit(node.orelse)
        if_body   = Compound(block_items=obj_body)   if obj_body else None
        if_orelse = Compound(block_items=obj_orelse) if obj_orelse else None
        if_stmt = If(cond=self.visit(node.test),
                     iftrue=if_body,
                     iffalse=if_orelse)
        return if_stmt


    def visit_PLFor(self, node, config=None):
        pliter_dom = node.iter_dom
        iter_var = self.visit(node.target)
        sim_for = simple_for(iter_var=iter_var.name,
                             start=self.visit(pliter_dom.start),
                             op=pliter_dom.op,
                             end=self.visit(pliter_dom.end),
                             step=self.visit(pliter_dom.step),
                             stmt_lst=self.visit(node.body))

        if pliter_dom.attr:
            insert_pragma(compound_node=sim_for.stmt, 
                          pragma=pliter_dom.attr, 
                          attr=(self.visit(pliter_dom.attr_args[0])
                                    if pliter_dom.attr_args else None))

        return sim_for

    def visit_PLWhile(self, node, config=None):
        while_body = Compound(block_items=self.visit(node.body))
        while_stmt = While(cond=self.visit(node.test),
                           stmt=while_body)
        # ignoring the orelse branch in PLWhile node. 
        # TODO: support orelse
        return while_stmt


    # TODO: correctly handle nested functions definitions
    def visit_PLFunctionDef(self, node, config=None):

        arg_list = []

        for arg in node.args:
            if hasattr(arg, 'pl_type') and hasattr(arg, 'pl_shape'):
                if arg.pl_shape == (1,):
                    arg_list.append(var_decl(var_type=arg.pl_type.ty,
                                             name=self.visit(arg).name))
                else:
                    arg_list.append(
                        array_decl(var_type=arg.pl_type.ty,
                                   name=self.visit(arg).name,
                                   dims=[ int32(e) for e in arg.pl_shape]))

            else:
                arg_list.append(array_decl(var_type="float",
                                           name=self.visit(arg).name,
                                           dims=[None]*2))


        # arg_list = [var_decl(var_type="float**", name=self.visit(arg).name) \
        #                                               for arg in node.args  ]
        # arg_list = [array_decl(var_type="float", name=self.visit(arg).name, \
        #                                dims=[None]*2) for arg in node.args  ]

        fd = func_def(
                func_name=node.name,
                args=arg_list,
                func_type="int",
                body=self.visit(node.body))

        if node.decorator_list:
            decorator_names = [e.name if isinstance(e, PLVariable) \
                                      else e.func.name \
                                            for e in node.decorator_list]
            if "pylog" in decorator_names:
                self.top_func_name = node.name

                if self.arg_info != None:
                    max_idx = insert_interface_pragmas(fd.body, self.arg_info)
                    self.max_idx = max_idx
                return fd
        else:
            self.cc.append_global(fd)

    def visit_PLPragma(self, node, config=None):
        # print(type(node.pragma))
        return Pragma(self.visit(node.pragma))

    '''TODO'''
    def visit_PLLambda(self, node, config=None):
        pass

    def visit_PLReturn(self, node, config=None):
        return Return(expr=self.visit(node.value))


    '''TODO'''
    def visit_PLMap(self, node, config=None):
        pass


    '''TODO'''
    def visit_PLHmap(self, node, config=None):
        pass

    '''TODO'''
    def visit_PLDot(self, node, config=None):
        pass

