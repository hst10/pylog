from __future__ import print_function
import sys
sys.path.extend(['/home/shuang91/pylog/cgen'])

from nodes import *
from c_ast import *
from pylog_cast import *
import c_generator

def filter_none(lst):
    return list(filter(None, lst))

class CCode:
    def __init__(self):
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
        print(">>>>>>>>>> Start to show C AST...")
        self.ast.show(attrnames=True, nodenames=True, showcoord=False)
        generator = c_generator.CGenerator()
        print(">>>>>>>>>> Start to generate C Code...")
        return generator.visit(self.ast)


class PLCodeGenerator:
    def __init__(self):
        self.cc = CCode()

    def codegen(self, node, config=None):
        self.cc += self.visit(node, config)
        self.ccode = self.cc.cgen()
        return self.ccode

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
        return filter_none([ self.visit(e) for e in node ])

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
        return array_decl(var_type=self.visit(node.ele_type).name,
                          name=self.visit(node.name).name,
                          dims=dims)
                          # dims=self.visit(node.dims))

    def visit_PLVariable(self, node, config=None):
        return ID(node.name)

    def visit_PLUnaryOp(self, node, config=None):
        return UnaryOp(op=node.op,
                       expr=self.visit(node.operand))

    def visit_PLBinOp(self, node, config=None):
        binop = BinaryOp(op=node.op,
                         left=self.visit(node.left),
                         right=self.visit(node.right))
        return binop

    def visit_PLCall(self, node, config=None):
        el = ExprList(exprs=[ self.visit(e) for e in node.args ])
        return FuncCall(name=self.visit(node.func), args=el)


    def visit_PLIfExp(self, node, config=None):
        top = TernaryOp(cond=self.visit(node.test),
                        iftrue=self.visit(node.body),
                        iffalse=self.visit(node.orelse))
        return top

    def visit_PLSubscript(self, node, config=None):
        obj = self.visit(node.var)
        for index in node.indices:
            obj = ArrayRef(name=obj, subscript=self.visit(index))

        return obj

    '''TODO'''
    def visit_PLSlice(self, node, config=None):
        pass

    def visit_PLAssign(self, node, config=None):
        asgm = Assignment(op=node.op, 
                          lvalue=self.visit(node.target),
                          rvalue=self.visit(node.value))
        return asgm

    def visit_PLIf(self, node, config=None):
        if_body   = Compound(block_items=self.visit(node.body))
        if_orelse = Compound(block_items=self.visit(node.orelse))
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
                             stmt_lst=[ self.visit(s) for s in node.body ])

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

        # arg_list = [ var_decl(var_type="float**", name=self.visit(arg).name) for arg in node.args  ]
        arg_list = [ array_decl(var_type="float", name=self.visit(arg).name, dims=[None]*2) for arg in node.args  ]

        fd = func_def(func_name=node.name, 
                      args=arg_list,
                      func_type="int",
                      body=filter_none([ self.visit(stmt) for stmt in node.body ]))

        if node.decorator_list:
            decorator_names = [e.name if isinstance(e, PLVariable) else e.func.name \
                                                     for e in node.decorator_list]
            if "pylog" in decorator_names:
                self.top_func_name = node.name
                return fd
        else:
            self.cc.append_global(fd)

    def visit_PLPragma(self, node, config=None):
        print(type(node.pragma))
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

