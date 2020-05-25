import copy

from nodes import *
from typer import PLType

class PLOptLoop:
    def __init__(self, plfor, subloops):
        self.plnode   = plfor
        self.subloops = subloops

    def append(self, plfor):
        self.subloops.append(plfor)

    def __repr__(self):
        return f'Loop_{self.plnode.target.name}{self.subloops}'

    def unroll(self, factor=None):
        self.plnode.iter_dom.attr = 'unroll'
        self.plnode.iter_dom.attr_args = [PLConst(factor)] if factor else None

    def pipeline(self):
        self.plnode.iter_dom.attr = 'pipeline'
        self.plnode.iter_dom.attr_args = None


def get_loop_structure(node):
    loops_found = []
    if isinstance(node, PLNode):
        for field in node._fields:
            try:
                obj = getattr(node, field)
            except AttributeError:
                pass
            if obj is not None:
                loops_found += get_loop_structure(obj)

    elif isinstance(node, list):
        for item in node:
            if item != None:
                loops_found += get_loop_structure(item)

    if isinstance(node, PLFor):
        print(f'get_loop_structure {node}, {node.target.name}')
        return [ PLOptLoop(plfor=node, subloops=loops_found) ]
    else:
        return loops_found

class PLOptMapTransformer:

    def __init__(self, debug=False):
        self.debug = debug

    def visit(self, node, config=None):
        """Visit a node."""

        if self.debug:
            print(f'OPT visiting {node.__class__.__name__}, {node}')

        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        visit_return = visitor(node, config)

        return visit_return

    def generic_visit(self, node, config=None):
        for field, old_value in iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, PLNode):
                        value = self.visit(value, config)
                        if value is None:
                            continue
                        elif not isinstance(value, PLNode):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, PLNode):
                new_node = self.visit(old_value, config)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node


    def get_subscript(self, op_node, iter_prefix='i', config=None):

        assert(isinstance(op_node, (PLSubscript, PLVariable)))

        target_shape = len(op_node.pl_shape)

        if isinstance(op_node, PLSubscript):
            subs       = []
            for i in range(len(op_node.pl_shape)):
                if op_node.pl_shape[i] == 1:
                    if isinstance(op_node.indices[i], PLSlice):
                        idx, _, _ = op_node.indices[i].updated_slice
                        subs.append(PLConst(idx))
                    else:
                        subs.append(self.visit(op_node.indices[i], config))
                else:
                    if isinstance(op_node.indices[i], PLSlice):
                        bounds = op_node.indices[i].updated_slice
                        lower, upper, step = bounds

                        if lower == 0:
                            if step == 1:
                                subs.append(PLVariable(f'{iter_prefix}{i}'))
                            else:
                                subs.append(PLVariable(
                                    f'({iter_prefix}{i}*({step}))'))
                        else:
                            if step == 1:
                                subs.append(PLVariable(
                                    f'({lower}+{iter_prefix}{i})'))
                            else:
                                subs.append(PLVariable(
                                    f'({lower}+{iter_prefix}{i}*({step}))'))
                    else:
                        subs.append(PLVariable(f'{iter_prefix}{i}'))

            target = PLSubscript(var=op_node.var,
                                 indices=subs)

        else:
            subs = [ PLVariable(f'{iter_prefix}{i}') \
                                        for i in range(target_shape)]

            target = PLSubscript(var=op_node,
                                 indices=subs)


        return target


    def visit_list(self, node, config=None):
        return [ self.visit(item, config) for item in node ]

    def visit_PLVariable(self, node, config=None):
        if (config is not None) and ('arg_map' in config):
            if node.name in config['arg_map']:
                return config['arg_map'][node.name]
        return node

    def visit_PLLambda(self, node, config=None):
        if hasattr(node, 'arg_map') and hasattr(node, 'target'):
            new_config = copy.deepcopy(config)
            if new_config is None:
                new_config = { 'arg_map': node.arg_map,
                           'target' : node.target }
            else:
                new_config['arg_map'] = node.arg_map
                new_config['target']  = node.target

        else:
            new_config = config

        assert(isinstance(node.body, PLAssign))
        stmts = self.visit(node.body, new_config)

        if not isinstance(stmts, list):
            stmts = [ stmts ]
        return stmts


    def visit_PLMap(self, node, config=None):

        args_subs = []
        for array in node.arrays:
            args_subs.append(self.get_subscript(array, 'i_map_', config))

        target_subs = self.get_subscript(node.target, 'i_map_', config)
        lambda_args = [ arg.name for arg in node.func.args ]

        target_subs.pl_type  = PLType(node.pl_type.ty, 0)
        target_subs.pl_shape = ( 1 for i in node.pl_shape ) # assuming scalar

        node.func.arg_map = dict(zip(lambda_args, args_subs))
        node.func.target  = target_subs

        lambda_func_body = node.func.body
        assert(not isinstance(lambda_func_body, PLAssign))
        # create a PLAssign node to assign original expression in lambda
        # function body to the map target

        new_lambda_body = PLAssign(op='=',
                                   target=target_subs,
                                   value=lambda_func_body)

        new_lambda_body.is_decl = False

        node.func.body = new_lambda_body
        stmt = self.visit(node.func, config)

        for i in range(len(node.pl_shape)-1, -1, -1):
        # for i in range(len(node.pl_shape)):
            target = PLVariable(f'i_map_{i}')
            target.pl_type  = PLType('int', 0)
            target.pl_shape = ()

            stmt = [ PLFor(target=target,
                           iter_dom=PLIterDom(end=PLConst(node.pl_shape[i])),
                           body=stmt,
                           orelse=[]) ]

        return stmt[0]


class PLOptimizer:
    def __init__(self, debug=False):
        self.debug = debug
        self.map_transformer = PLOptMapTransformer(debug)

    def opt(self, node):
        self.map_transformer.visit(node)
        self.loops = get_loop_structure(node)

        if self.debug:
            print('PLOptimizer', self.loops)

        def unroll_innermost(loop_lst):
            assert(isinstance(loop_lst, list))
            for loop in loop_lst:
                if loop.subloops == []:
                    loop.unroll()
                else:
                    unroll_innermost(loop.subloops)

        unroll_innermost(self.loops)
