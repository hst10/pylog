
from . import c_ast
from . import c_generator

# Constants

def const(const_type, value):
    return c_ast.Constant(type=const_type, value=str(value))

def _create_const_class(const_type):
    def tmp_func(value):
        return c_ast.Constant(type=const_type, value=str(value))
    return tmp_func

int16   = _create_const_class("int16")
int32   = _create_const_class("int")
float16 = _create_const_class("float16")
float32 = _create_const_class("float")


# def var(var_name):
#     '''
#         var_name: string
#     '''
#     return c_ast.ID(name=var_name)


def var_decl(var_type, name, init=None):
    '''
        var_type: string
        name:     string
        init:     AST Node
    '''
    type_decl = c_ast.TypeDecl(declname=name,
                               type=c_ast.IdentifierType(names=[var_type]))
    if init == None:
        decl = c_ast.Decl(name=name, type=type_decl)
    else:
        # decl = c_ast.Decl(name=name, type=type_decl,\
        #                   init=c_ast.Constant(type=var_type, value=init))
        decl = c_ast.Decl(name=name, type=type_decl, init=init)

    return decl

def array_decl(var_type, name, dims=[]):
    '''
        var_type: string; 
        name:     string; 
        dims:     list of AST nodes, outermost to innermost
    '''
    type_decl = c_ast.TypeDecl(declname=name,
                               type=c_ast.IdentifierType(names=[var_type]))
    for i in range(len(dims)-1, -1, -1):
        type_decl = c_ast.ArrayDecl(type=type_decl, dim=dims[i], dim_quals=[])

    decl = c_ast.Decl(name=name, type=type_decl)

    return decl

def subscript(array_name, subscripts):
    obj = array_name
    for index in subscripts:
        obj = c_ast.ArrayRef(name=obj, subscript=index)
    return obj

# def unaryop(op, expr):
#     '''
#         op:   string
#         expr: AST node
#     '''
#     return c_ast.UnaryOp(op=op, expr=expr)

# def binop(op, lvalue, rvalue):
#     '''
#         op:     string
#         lvalue: AST node
#         rvalue: AST node
#     '''
#     return c_ast.BinaryOp(op=op, left=lvalue, right=rvalue)

# def assignment(op, lvalue, rvalue):
#     '''
#         op:     string
#         lvalue: AST node
#         rvalue: AST node
#     '''
#     return c_ast.Assignment(op=op, lvalue=lvalue, rvalue=rvalue)

# def ifelse(cond, iftrue, iffalse):
#     '''
#         cond:   AST node
#         lvalue: AST node
#         rvalue: AST node
#     '''
#     return c_ast.If(cond=cond, iftrue=iftrue, iffalse=iffalse)

def simple_for(iter_var, start, op, end, step, stmt_lst):
    '''
        iter_var: string
        start:    AST node
        op:       string
        end:      AST node
        step:     AST node
        stmt_lst: list of AST nodes
    '''
    iter_decl = c_ast.Decl(
                    name=iter_var, 
                    quals=[], 
                    storage=[], 
                    funcspec=[],
                    type=c_ast.TypeDecl(
                        declname=iter_var, 
                        quals=[], 
                        type=c_ast.IdentifierType(names=['int'])
                    ), # assuming iter var is an int
                    init=start)
    for_init = c_ast.DeclList([iter_decl])
    for_cond = c_ast.BinaryOp(op=op, left=c_ast.ID(iter_var), right=end)
    for_next = c_ast.Assignment(op='+=',
                                lvalue=c_ast.ID(iter_var),
                                rvalue=step)
    return c_ast.For(init=for_init, cond=for_cond, next=for_next,
                     stmt=c_ast.Compound(block_items=stmt_lst))

def insert_pragma(compound_node, pragma=None, attr=None, pragma_str=None):
    assert(isinstance(compound_node, c_ast.Compound))
    if pragma_str != None:
        if isinstance(pragma_str, str):
            pragmas = [ c_ast.Pragma('HLS ' + pragma_str) ]
        elif isinstance(pragma_str, list):
            pragmas = [ c_ast.Pragma('HLS ' + s) for s in pragma_str ]
    else:
        pragmas = [ c_ast.Pragma(f'HLS {pragma}' + (f' factor={attr.value}' \
                                                           if attr else '')) ]
    compound_node.block_items = pragmas + compound_node.block_items

def insert_interface_pragmas(compound_node, interface_info, num_mem_ports=4):
    pragma_strs = []
    data_bundle_idx = -1
    max_bundle_idx  = -1
    for key, val in interface_info.items():
        type_name, shape = val
        if shape in {(1,), ()}:
            pragma_strs.append(f'INTERFACE s_axilite register port={key} '+\
                               f'bundle=CTRL')
        else:
            data_bundle_idx = (data_bundle_idx + 1) % num_mem_ports
            max_bundle_idx = max(max_bundle_idx, data_bundle_idx)
            pragma_strs.append(f'INTERFACE m_axi port={key} offset=slave '+\
                               f'bundle=DATA_{data_bundle_idx}')

    pragma_strs.append(f'INTERFACE s_axilite register port=return bundle=CTRL')

    insert_pragma(compound_node, pragma_str=pragma_strs)
    return max_bundle_idx + 1

def func_decl(func_name, args, func_type):
    '''
        func_name: string
        args:      list of Decl's
        func_type: string
    '''
    type_decl = c_ast.TypeDecl(declname=func_name,
                               type=c_ast.IdentifierType(names=[func_type]))
    arg_list = c_ast.ParamList(params=args)
    function_decl = c_ast.FuncDecl(args=arg_list, type=type_decl)
    decl = c_ast.Decl(name=func_name, quals=[], storage=[], funcspec=[], \
                      type=function_decl)
    return decl

def func_def(func_name, args, func_type, body=[]):
    '''
        func_name: string
        args:      list of Decl's
        func_type: string
        body:      list of statements
    '''
    function_decl = func_decl(func_name=func_name,
                              args=args,
                              func_type=func_type)
    return c_ast.FuncDef(decl=function_decl,
                         param_decls=[],
                         body=c_ast.Compound(block_items=body))

# def return_stmt(expr):
#     return c_ast.Return(expr=expr)
