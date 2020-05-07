from visitors import *
from nodes import *

def make_parent(root):
    for node in ast.walk(root):
        for child in ast.iter_child_nodes(node):
            child.parent = node

class PLConfig:
    def __init__(self, indent_level=0, indent_str=" "*2, idx_var_num=0, \
                 context=None, var_list={}, targets=None, node=None):
        self.indent_level = indent_level
        self.indent_str = indent_str
        self.idx_var_num = idx_var_num
        self.context = context
        self.var_list = var_list
        self.tarets = targets
        self.curr_node = node

class PLTester(PLPostorderVisitor):
    # pass
    def visit_Module(self, node, config=None):
        print("Tester|||>>>>", type(node))

    def visit_Assign(self, node, config=None):
        print("Tester|||>>>>", type(node))
        print("Tester|||>>>> is a Assign node? ", isinstance(node, ast.Assign))
        print("Tester|||>>>> is a stmt node? ", isinstance(node, ast.stmt))
        # self.visit(node.value, config)

    def visit_BinOp(self, node, config=None):
        print("Tester|||>>>>", type(node))
        print("Tester|||>>>> is a BinOp node? ", isinstance(node, ast.BinOp))
        print("Tester|||>>>> is a expr node? ", isinstance(node, ast.expr))
        # self.visit(node.value, config)

    def visit_Lambda(self, node, config=None):
        print("Tester|||>>>>", type(node))

    def visit_arg(self, node, config=None):
        print("Tester|||>>>>", type(node))
        print(type(node.arg))

    def visit_NoneType(self, node, config=None):
        print("Tester|||>>>>", type(node))
        print("NONE!!! ")



class PLAnalyzer(PLPostorderVisitor):

    def __init__(self):
        PLPostorderVisitor.__init__(self)
        self.args = {}

    # def isLambdaArg(self, node):
    #     assert(isinstance(node, ast.Subscript))
    #     """Check if Subscript node is lambda argument, which represents delta/offset. """
    #     is_lambda_arg = False
    #     p_node = node.parent
    #     while (not isinstance(p_node, ast.Module)):
    #         if isinstance(p_node, ast.Lambda):
    #             arg_lst = [elem.arg for elem in p_node.args.args]

    #             if node.value.id in arg_lst:
    #                 is_lambda_arg = True
    #                 break
    #         p_node = p_node.parent
    #     return is_lambda_arg

    # def assign_targets(self, assign_node):
    #     """Propagate pl_targets to all downstream nodes. """
    #     pass


    ######## Literals ########

    # def visit_NoneType(self, node, config=None):
    #     pass

    def visit_Constant(self, node, config=None):
        node.pl_data = PLConst(node.value, node, config)
        return node.pl_data

    def visit_Num(self, node, config=None):
        node.pl_data = PLConst(node.n, node, config)
        return node.pl_data

    def visit_Str(self, node, config=None):
        node.pl_data = PLConst(node.s, node, config)
        return node.pl_data

    def visit_List(self, node, config=None):
        elts=[ e.pl_data for e in node.elts ]
        node.pl_data = PLArray(elts, node, config)
        return node.pl_data

    def visit_Tuple(self, node, config=None):
        elts=[ e.pl_data for e in node.elts ]
        node.pl_data = PLArray(elts, node, config)
        return node.pl_data

    def visit_Set(self, node, config=None):
        pass

    def visit_Dict(self, node, config=None):
        pass

    def visit_NameConstant(self, node, config=None):
        '''True, False or None'''
        node.pl_data = PLConst(node.value, node, config)
        return node.pl_data


    ######## Variables ########

    def visit_Name(self, node, config=None):
        node.pl_data = PLVariable(node.id, node, config)
        return node.pl_data


    ######## Expressions ########

    def visit_Expr(self, node, config=None):
        node.pl_data = node.value.pl_data # simply propagate the value
        return node.pl_data

    def visit_UnaryOp(self, node, config=None):
        if (node.operand.pl_data != None) and \
            isinstance(node.operand.pl_data, PLConst) and \
            isinstance(node.op, (ast.USub, ast.UAdd)):
            if isinstance(node.op, ast.USub):
                node.pl_data = PLConst(-node.operand.pl_data.value, node, config)
            elif isinstance(node.op, ast.UAdd):
                node.pl_data = PLConst(node.operand.pl_data.value, node, config)
        else:
            node.pl_data = PLUnaryOp(op=token(node.op), 
                                     operand=node.operand.pl_data, 
                                     ast_node=node, 
                                     config=None)
        return node.pl_data

    def visit_BinOp(self, node, config=None):
        node.pl_data = PLBinOp(op=token(node.op), 
                               left=node.left.pl_data, 
                               right=node.right.pl_data, 
                               ast_node=node, 
                               config=config)
        return node.pl_data

    def visit_BoolOp(self, node, config=None):
        expr = node.values[0].pl_data
        for i in range(1, len(node.values)):
            expr = PLBinOp(op=token(node.op), 
                           left=expr, 
                           right=node.values[i].pl_data,
                           ast_node=node, 
                           config=config)
        node.pl_data = expr
        return node.pl_data

    def visit_Compare(self, node, config=None):
        expr = node.left.pl_data
        for i in range(len(node.comparators)):
            expr = PLBinOp(op=token(node.ops[i]), 
                           left=expr, 
                           right=node.comparators[i].pl_data,
                           ast_node=node, 
                           config=config)
        node.pl_data = expr
        return node.pl_data

    def visit_Call(self, node, config=None):

#        if (config != None) and (config.target != None):

        if hasattr(node, "pl_targets"):
            node.func.pl_targets = node.pl_targets

        # self.visit(node.func, config)
        # for arg in node.args:
        #     self.visit(arg, config)

        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Call):
                node.pl_data = PLCall(func=node.func.value.func.pl_data,
                                      args=[ e.pl_data for e in node.func.value.args ],
                                      attr=node.func.attr,
                                      attr_args=[ e.pl_data for e in node.args ],
                                      ast_node=node,
                                      config=config)

            elif node.func.value.id == 'np':
                if node.func.attr == 'empty':
                    if isinstance(node.parent, ast.Assign):
                        node.pl_data = PLArrayDecl(ele_type=node.args[1].pl_data,
                                                   name=node.parent.targets[0].pl_data,
                                                   dims=node.args[0].pl_data,
                                                   ast_node=node,
                                                   config=config)
                        node.parent.pl_data = node.pl_data
                else:
                    raise NotImplementedError



        elif node.func.id == "pragma":
            node.pl_data = PLPragma(node.args[0].pl_data, node, config)
        elif node.func.id == "hmap":
            node.pl_data = PLHmap(node, config)
            # node.args[0].pl_targets = 

        elif node.func.id == "map":
            node.pl_data = PLMap(node, config)
        elif node.func.id == "dot":
            node.pl_data = PLDot(node, config)
        elif node.func.id == "PLType" and len(node.args) == 2 \
            and isinstance(node.args[0], ast.Name) \
            and isinstance(node.args[1], ast.Num):
            node.pl_data = TypeNode(node, config)
            return node.pl_data.type
        else:
            node.pl_data = PLCall(func=node.func.pl_data,
                                  args=[ e.pl_data for e in node.args ],
                                  ast_node=node,
                                  config=config)
        return node.pl_data

    def visit_keyword(self, node, config=None):
        pass

    def visit_IfExp(self, node, config=None):
        node.pl_data = PLIfExp(test=node.test.pl_data, 
                               body=node.body.pl_data,
                               orelse=node.orelse.pl_data, 
                               ast_node=node, 
                               config=config)
        return node.pl_data

    def visit_Attribute(self, node, config=None):
        node.pl_data = PLAttribute(value=node.value.pl_data,
                                   attr=node.attr,
                                   ast_node=node,
                                   config=config)


    ######## Subscripting ########

    def visit_Subscript(self, node, config=None):
        var = node.value.pl_data
        indices =  node.slice.pl_data
        if not isinstance(indices, list):
            indices = [ indices ]

        if isinstance(var, PLSubscript):
            node.pl_data = PLSubscript(var=var.var,
                                       indices=(var.indices+indices),
                                       ast_node=node, 
                                       config=config)
        else:
            node.pl_data = PLSubscript(var=var, 
                                       indices=indices,
                                       ast_node=node, 
                                       config=config)
        return node.pl_data

    def visit_Index(self, node, config=None):
        node.pl_data = node.value.pl_data
        return node.pl_data

    def visit_Slice(self, node, config=None):
        lower = upper = step = None
        if node.lower:
            lower = node.lower.pl_data
        if node.upper:
            upper = node.upper.pl_data
        if node.step:
            step = node.step.pl_data
        node.pl_data = PLSlice(lower=lower,
                               upper=upper,
                               step=step,
                               ast_node=node,
                               config=config)
        return node.pl_data

    def visit_ExtSlice(self, node, config=None):
        # for slc in node.dims:
        #     self.visit(slc)
        node.pl_data = [ e.pl_data for e in node.dims ]
        return node.pl_data


    ######## Statements ########

    def visit_Assign(self, node, config=None):
        # for target in node.targets:
        #     self.visit(target, config)

        # sometimes the pl_data has already been populated
        # when visiting the right-hand side, for example, 
        # a = np.empty([3, 4]) generates array declaration
        # for the whole assignment.  

        if hasattr(node, "pl_data"):
            return node.pl_data

        node.pl_targets = [ t.pl_data for t in node.targets ]
        if len(node.targets) > 1:
            raise NotImplementedError
        node.value.pl_targets = node.pl_targets

        node.pl_data = PLAssign(op='=',
                                target=node.targets[0].pl_data, 
                                value=node.value.pl_data,
                                ast_node=node, 
                                config=config)

        if config == None:
            config = PLConfig()
        config.targets = [ t.pl_data for t in node.targets ]
        config.curr_node = node.pl_data



        return node.pl_data

        # self.visit(node.value, config)

    def visit_AugAssign(self, node, config=None):
        node.pl_data = PLAssign(op=token(node.op)+'=',
                                target=node.target.pl_data, 
                                value=node.value.pl_data,
                                ast_node=node, 
                                config=config)

    def visit_Assert(self, node, config=None):
        pass

    def visit_Delete(self, node, config=None):
        pass

    def visit_Pass(self, node, config=None):
        pass



    ######## Control flow ########

    def visit_If(self, node, config=None):
        node.pl_data = PLIf(test=node.test.pl_data,
                            body=[ e.pl_data for e in node.body ],
                            orelse=[ e.pl_data for e in node.orelse ],
                            ast_node=node, 
                            config=config)

    def visit_For(self, node, config=None):
        node.iter.pl_data = PLIterDom(expr=node.iter.pl_data,
                                      ast_node=node,
                                      config=config)
        node.pl_data = PLFor(target=node.target.pl_data,
                             iter_dom=node.iter.pl_data,
                             body=[ s.pl_data for s in node.body ],
                             orelse=[ s.pl_data for s in node.orelse ],
                             ast_node=node,
                             config=config)

    def visit_While(self, node, config=None):
        node.pl_data = PLWhile(test=node.test.pl_data,
                               body=[ e.pl_data for e in node.body ],
                               orelse=[ e.pl_data for e in node.orelse ],
                               ast_node=node, 
                               config=config)

    def visit_Break(self, node, config=None):
        pass

    def visit_Continue(self, node, config=None):
        pass

    ######## Function and class definitions ########

    def parse_func_args(self, arg_lst, config=None):
        return { arg.arg:self.visit(arg.annotation, config) for arg in arg_lst }

    def visit_FunctionDef(self, node, config=None):
        # self.visit(node.args, config)

        if node.decorator_list:
            decorator_names = [e.id if isinstance(e, ast.Name) else e.func.id \
                                                     for e in node.decorator_list]
            # print(decorator_names)
            if "pylog" in decorator_names:
                self.top_func = node.name
                if node.args.args:
                    self.args.update(self.parse_func_args(node.args.args, config))
                    print(self.args)

        if config == None:
            config = PLConfig()
        config.var_list = self.args

        # if isinstance(node.body, list):
        #     for item in node.body:
        #         if isinstance(item, ast.AST):
        #             self.visit(item, config)
        # elif isinstance(node.body, ast.AST):
        #     self.visit(node.body, config)

        node.pl_data = PLFunctionDef(name=node.name,
                                     args=node.args.pl_data,
                                     body=[stmt.pl_data for stmt in node.body],
                                     decorator_list=[e.pl_data for e in node.decorator_list],
                                     ast_node=node,
                                     config=config)

        return node.pl_data

    def visit_Lambda(self, node, config=None):
        # self.visit(node.args, config)
        # self.visit(node.body, config)
        node.pl_data = LambdaNode(node, config)
        return node.pl_data

    def visit_arguments(self, node, config=None):
        for arg in node.args:
            self.visit(arg, config)
        for arg in node.args:
            print(arg.arg)
        node.pl_data = [ arg.pl_data for arg in node.args ]

        print("PyLog arguments |||>>>>", type(node))
        return node.pl_data

    def visit_arg(self, node, config=None):
        # if node.annotation != None:
        #     self.visit(node.annotation, config)

        node.pl_data = PLVariable(name=node.arg, 
                                  ast_node=node, 
                                  config=config)

        # print("PyLog arg |||>>>>", type(node))
        return node.pl_data


    def visit_Return(self, node, config=None):
        node.pl_data = PLReturn(value=node.value.pl_data,
                                ast_node=node,
                                config=config)
        return node.pl_data

    def visit_Module(self, node, config=None):
        node.pl_data = [ stmt.pl_data for stmt in node.body ]
        return node.pl_data
        # for stmt in node.body:
        #     self.visit(stmt, config)
