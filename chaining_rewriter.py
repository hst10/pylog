import re
import copy

from utils import *
from nodes import *


class PLChainingRewriter:
    NOT_IN_CHAINING_OR_DONT_CARE = 0
    IN_CHAINING = 1
    IN_CHAINING_AND_TOP_NODE = 2

    def __init__(self, debug=False):
        self.debug = debug

    def visit(self, node, stmt_node=None, is_statement=False):
        """Visit a node."""

        if self.debug:
            print(f'Visiting {node.__class__.__name__}, {node}')

        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        visit_return = visitor(node, stmt_node)

        # If visit_return == IN_CHAINING_AND_TOP_NODE, wrap the current node with a new PLChainingTop to handle this
        if visit_return == self.IN_CHAINING_AND_TOP_NODE:
            new_PLChainingTop = PLChainingTop(node, node.pl_type, node.pl_shape)
            node.pl_type.dim = 0
            node.pl_shape = ()  # can safely change the PLChainingTop.stmt typer information to scalar now
            replace_child(node.parent, node, new_PLChainingTop)
            node.parent = new_PLChainingTop
            return self.NOT_IN_CHAINING_OR_DONT_CARE  # no chaining to handle at this moment

        return visit_return

    def generic_visit(self, node, stmt_node=None):
        """Called if no explicit visitor function exists for a node."""
        # visit children
        if isinstance(node, PLNode):
            for field, value in iter_fields(node):
                self.visit(value, stmt_node)
        elif isinstance(node, list):
            for item in node:  # item is a complete statement
                assert (not hasattr(item, 'parent'))
                item.parent = node  # assign node to item.parent so that in case of chaining the visitor can replace the item in the list with new node
                self.visit(item, stmt_node=item)
                del item.parent
        return self.NOT_IN_CHAINING_OR_DONT_CARE

    def visit_PLIPcore(self, node, stmt_node=None):
        # TODO: not supported function call
        return self.NOT_IN_CHAINING_OR_DONT_CARE

    def visit_PLChainingTop(self, node, stmt_node=None):
        assert (
                0 and "visiting chaining top is not supposed to happen. Possible reason: reusing function but this is not supported")

    def visit_PLFunctionDef(self, node, stmt_node=None):

        if hasattr(node, 'chaining_rewriter_done'):
            return self.NOT_IN_CHAINING_OR_DONT_CARE  # node.pl_type, node.pl_shape, node.pl_ctx

        # if node.pl_top:
        # for arg in node.args: # assumes no scenario involves chaining in formal argument

        if all(hasattr(arg, 'pl_type') for arg in node.args):
            # for arg in node.args: # assumes no scenario involves chaining in formal argument
            for stmt in node.body:
                self.visit(stmt, is_statement=True,
                           stmt_node=stmt)  # This could include chaining for-loop expression. ending point of propagation
                # if isinstance(stmt, PLReturn):

            node.chaining_rewriter_done = True

    def visit_PLPragma(self, node, stmt_node=None):
        return self.NOT_IN_CHAINING_OR_DONT_CARE

    def visit_PLConst(self, node, stmt_node=None):
        return self.visit_general_variable_nodes(node, stmt_node=stmt_node)

    def visit_PLArray(self, node, stmt_node=None):
        # dim = len(node.elts)
        # if dim == 0:
        #    pass
        # else:
        #    self.visit(node.elts[0], stmt_node) #TODO: not dealing with node.elts
        return self.visit_general_variable_nodes(node, stmt_node=stmt_node)

    def visit_PLArrayDecl(self, node, stmt_node=None):
        return self.NOT_IN_CHAINING_OR_DONT_CARE

    def visit_PLVariableDecl(self, node, stmt_node=None):
        return self.NOT_IN_CHAINING_OR_DONT_CARE

    def visit_PLVariable(self, node, stmt_node=None):
        return self.visit_general_variable_nodes(node, stmt_node)

    def visit_PLUnaryOp(self, node, stmt_node=None):
        operand_ret_value = self.visit(node.operand, stmt_node)  # This could include chaining for-loop expression
        if operand_ret_value != self.NOT_IN_CHAINING_OR_DONT_CARE:
            if node != stmt_node:  # need to keep the stmt_node information and move that to new PLChainingTop and then replace its typer information to scalar
                node.pl_shape = ()
                node.pl_type.dim = 0
            if stmt_node != node:
                return self.IN_CHAINING
            else:
                return self.IN_CHAINING_AND_TOP_NODE
        else:
            return self.NOT_IN_CHAINING_OR_DONT_CARE

    def visit_PLBinOp(self, node, stmt_node=None):
        self.visit(node.op, stmt_node)  # What is this for?
        left_ret_value = self.visit(node.left, stmt_node)  # This could include chaining for-loop expression
        right_ret_value = self.visit(node.right,
                                     stmt_node)  # This could include chaining for-loop expression #TODO: if left and right can share the node, in the scenario where left is inserted a PLSubscript, there will be problem.
        in_chaining = False
        if left_ret_value != self.NOT_IN_CHAINING_OR_DONT_CARE or right_ret_value != self.NOT_IN_CHAINING_OR_DONT_CARE:
            in_chaining = True
        if in_chaining:
            if node != stmt_node:  # need to keep the stmt_node information and move that to new PLChainingTop and then replace its typer information to scalar
                node.pl_shape = ()
                node.pl_type.dim = 0
            if stmt_node == node:
                return self.IN_CHAINING_AND_TOP_NODE
            else:
                return self.IN_CHAINING
        else:
            return self.NOT_IN_CHAINING_OR_DONT_CARE

    def visit_PLSlice(self, node, stmt_node=None):

        # visit each field first (constant propagation may happen:
        # expression -> PLConst)
        # self.visit(node.lower, stmt_node)  # TODO: not dealing with chaining propagation here (array as subscription)
        # self.visit(node.upper, stmt_node)  # TODO: not dealing with chaining propagation here (array as subscription)
        # self.visit(node.step, stmt_node)  # TODO: not dealing with chaining propagation here (array as subscription)
        return self.visit_general_variable_nodes(node, stmt_node)

    def visit_PLAssign(self, node, stmt_node=None):
        # TODO: not handling PLMap for this moment
        if isinstance(node.value, PLMap):
            return self.NOT_IN_CHAINING_OR_DONT_CARE

        value_ret_value = self.visit(node.value,
                                     stmt_node=stmt_node)  # not dealing with chaining propagation here (array as subscription)

        # if node.is_decl:
        #    assert (not isinstance(node.target, PLSubscript))
        #    target_ret_value = self.NOT_IN_CHAINING_OR_DONT_CARE
        # else:
        target_ret_value = self.visit(node.target,
                                      stmt_node=stmt_node)  # This could include chaining for-loop expression
        if (target_ret_value != self.NOT_IN_CHAINING_OR_DONT_CARE) or (
                value_ret_value != self.NOT_IN_CHAINING_OR_DONT_CARE):
            if node != stmt_node:  # need to keep the stmt_node information and move that to new PLChainingTop and then replace its typer information to scalar
                node.pl_shape = ()
                node.pl_type.dim = 0
            if stmt_node == node:
                return self.IN_CHAINING_AND_TOP_NODE
            else:
                return self.IN_CHAINING
        else:
            return self.NOT_IN_CHAINING_OR_DONT_CARE

    def visit_PLReturn(self, node, stmt_node=None):
        # TODO: not supporting expression (return value) at this time
        return self.NOT_IN_CHAINING_OR_DONT_CARE
        # self.visit(node.value, stmt_node=node.value)  # This could include chaining for-loop expression. ending point of propagation
        # if node.value:
        #    pass
        # else:
        #    pass

    def visit_PLFor(self, node, stmt_node=None):
        # TODO: not supporting expression (loop variable and bound) at this time
        for stmt in node.body:
            self.visit(stmt,
                       stmt_node=stmt)  # This could include chaining for-loop expression. ending point of propagation
        return

    def visit_PLWhile(self, node, stmt_node=None):
        # TODO: not supporting expression (loop condition) at this time
        for stmt in node.body:
            self.visit(stmt,
                       stmt_node=stmt)  # This could include chaining for-loop expression. ending point of propagation
        return

    def visit_PLIf(self, node, stmt_node=None):
        # TODO: the condition expr *test* is harder to deal with (maybe temporary object is needed) yet not visited by this vistor
        # TODO: don't know how elif is visited but now the condition expression there is not supported either
        for stmt in node.body:
            self.visit(stmt,
                       stmt_node=stmt)  # This could include chaining for-loop expression. ending point of propagation

        for stmt in node.orelse:
            self.visit(stmt,
                       stmt_node=stmt)  # This could include chaining for-loop expression. ending point of propagation

        return self.NOT_IN_CHAINING_OR_DONT_CARE

    def visit_PLIfExp(self, node, stmt_node=None):
        # TODO: single-line expression not yet suppported
        # TODO: the condition expr *test* is harder to deal with (maybe temporary object is needed) yet not visited by this vistor
        return self.NOT_IN_CHAINING_OR_DONT_CARE
        # self.visit(node.body,
        #               stmt_node=stmt_node)  # This could include chaining for-loop expression. ending point of propagation

        # self.visit(node.orelse,
        #               stmt_node=stmt_node)  # This could include chaining for-loop expression. ending point of propagation

    def visit_PLCall(self, node, stmt_node=None):
        # breakpoint()
        func_name = node.func.name
        if func_name == "range":
            # TODO: not supporting chaining in built-in function invocation at this moment
            # len has been replaced with PLConst during typer traversal
            return self.NOT_IN_CHAINING_OR_DONT_CARE
        else:
            func_def_node = getattr(node, "func_def_node", None)
            if func_def_node is not None:
                # TODO: args values are harder to deal with (maybe temporary object is needed) so not visited by this visitor currently
                # for i in range(len(node.args)):
                #    self.visit(node.args[i],stmt_node=node.args[i])  # This could include chaining for-loop expression. ending point of propagation
                self.visit(func_def_node,
                           stmt_node)  # Add the for loop inside the func_def, don't need to propagate up.
                return self.NOT_IN_CHAINING_OR_DONT_CARE
            else:
                print(f'Function {func_name} called before definition!')
                raise NameError

    def visit_general_variable_nodes(self, node, stmt_node=None):
        if len(stmt_node.pl_shape) > 0 and not (all([ele == 1 for ele in stmt_node.pl_shape])):
            # create a new PLSubscript to realize PLSubscript to PLSubscript
            if isinstance(node.parent, PLAssign) and isinstance(node.parent.value, PLFor):
                # this stmt_node is already dealt with by the optimizer and should not be considered again here
                return self.NOT_IN_CHAINING_OR_DONT_CARE

            indices = []
            if len(node.pl_shape) == 0:
                return self.IN_CHAINING  # no need to insert new PLSubscript node as the chaining will constantly use this scalar as the element in the generated for loops
            for reverse_idx, idx in enumerate(range(len(stmt_node.pl_shape) - 1, -1, -1)):
                if reverse_idx >= len(node.pl_shape):
                    continue
                else:
                    if node.pl_shape[len(node.pl_shape) - 1 - reverse_idx] == 1:
                        indices = [PLConst(0)] + indices
                    else:
                        indices = [PLVariable("i_chaining_{idx}".format(idx=idx))] + indices  # assume step equals 1
            new_PLSubscript = PLSubscript(node, indices)

            new_PLSubscript.pl_type = node.pl_type
            if node != stmt_node:  # need to keep the stmt_node information and move that to new PLChainingTop and then replace its typer information to scalar
                new_PLSubscript.pl_shape = ()
                new_PLSubscript.pl_type.dim = 0

            replace_child(node.parent, node, new_PLSubscript)
            node.parent = new_PLSubscript
            return self.IN_CHAINING
        else:
            return self.NOT_IN_CHAINING_OR_DONT_CARE

    # Indices could be an array
    def visit_PLSubscript(self, node, stmt_node=None):
        # for i in range(len(indices)):
        # indices[i].parent = node
        # the length along that dimension
        # if self.debug:
        #    print('VISITING INDICS')
        #    print(f'{type(indices[i])}')
        # self.visit(indices[i], stmt_node)  # TODO: not dealing with chaining propagation here
        return self.visit_general_variable_nodes(node, stmt_node)

    def visit_PLLambda(self, node, stmt_node=None):
        return self.NOT_IN_CHAINING_OR_DONT_CARE  # TODO: not handling lambda yet
        # if all(hasattr(arg, 'pl_type') for arg in node.args):
        #     # for arg in node.args:
        #
        #     self.visit(node.body,
        #                stmt_node=node.body)  # This could include chaining for-loop expression. ending point of propagation

    def visit_PLMap(self, node, stmt_node=None):
        assert (0 and "PLMap should be replaced with non-PLMap nodes by the optimizer already")
        # for array in node.arrays:
        #     self.visit(array, stmt_node)
        #
        # # in plmap, the args of lambda function are all scalars
        # # since plmap iterates through each element in arrays
        # # for i in range(len(node.func.args)):
        #
        # self.visit(node.func, stmt_node)

    def visit_PLDot(self, node, stmt_node=None):
        op1_ret_val = self.visit(node.op1, stmt_node)
        op2_ret_val = self.visit(node.op2, stmt_node)
        if op1_ret_val != self.NOT_IN_CHAINING_OR_DONT_CARE or op2_ret_val != self.NOT_IN_CHAINING_OR_DONT_CARE:
            if stmt_node == node:
                return self.IN_CHAINING_AND_TOP_NODE
            else:
                return self.IN_CHAINING
        else:
            return self.NOT_IN_CHAINING_OR_DONT_CARE
