import copy

from nodes import *
from typer import PLType
from iter_schedule import *

class PLOptLoop:
    def __init__(self, plfor, subloops):
        self.plnode = plfor
        self.subloops = subloops
        self.source   = plfor.source

    def append(self, plfor):
        self.subloops.append(plfor)

    def __repr__(self):
        return f'Loop_{self.plnode.target.name}({self.source}){self.subloops}'

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
        return [PLOptLoop(plfor=node, subloops=loops_found)]
    else:
        return loops_found


class PLOptMapTransformer:

    def __init__(self, backend='vhls', debug=False):
        self.backend = backend
        self.debug = debug
        self.count = 0

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
                    if value is list:
                        new_values.extend(value)
                    else:
                        new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, PLNode):
                new_node = self.visit(old_value, config)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node

    def get_subscript(self, op_node, iter_prefix='i',
                      config=None, schedule=None):

        assert (isinstance(op_node, (PLSubscript, PLVariable)))

        if isinstance(op_node, PLSubscript):
            subs = []
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
                                subs.append(
                                    PLVariable(f'{iter_prefix}{i}')*step)
                                # subs.append(PLVariable(
                                #     f'({iter_prefix}{i}*({step}))'))
                        else:
                            if step == 1:
                                subs.append(
                                    PLVariable(f'{iter_prefix}{i}') + lower)
                                    # f'({lower}+{iter_prefix}{i})'))
                            else:
                                subs.append(
                                    PLVariable(f'{iter_prefix}{i}')*step+lower)
                                    # f'({lower}+{iter_prefix}{i}*({step}))'))
                    else:
                        subs.append(PLVariable(f'{iter_prefix}{i}'))

            target = PLSubscript(var=op_node.var,
                                 indices=subs)

        else:
            subs = [PLVariable(f'{iter_prefix}{i}') \
                    for i in range(len(op_node.pl_shape))]

            target = PLSubscript(var=op_node,
                                 indices=subs)

        if schedule:
            s = PLSchedule(schedule)
            target = s.apply(target, iter_prefix=iter_prefix)

        target.pl_shape = ()
        target.pl_type = op_node
        target.pl_type.dim = 0
        return target

    def filter_none(self, lst):
        return list(filter(None, lst))

    def visit_list(self, node, config=None):
        stmt_list = []

        for e in node:
            stmt = self.visit(e, config)
            if isinstance(stmt, list):
                stmt_list += stmt
            else:
                stmt_list.append(stmt)
        return self.filter_none(stmt_list)

    def visit_PLVariable(self, node, config=None):
        if (config is not None) and ('arg_map' in config):
            if node.name in config['arg_map']:
                return config['arg_map'][node.name]
        return node

    def visit_PLAssign(self, node, config=None):
        if isinstance(node.value, PLDot):
            return self.visit(node.value, config)
        # node.target = self.visit(node.target, config)
        # node.value  = self.visit(node.value, config)
        node_value = self.visit(node.value, config)
        if isinstance(node_value, (PLFor, list)):
            return node_value
        else:
            return node

    def visit_PLSubscript(self, node, config=None):
        node.var = self.visit(node.var, config)
        node.indices = [self.visit(idx, config) for idx in node.indices]
        return node

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

    def visit_PLMap(self, node, config=None):

        decl = None
        if node.parent.is_decl:
            if node.pl_type.dim == 0:
                pass
            else:
                elts = [PLConst(i) for i in node.pl_shape]
                decl = PLArrayDecl(ele_type=node.target.pl_type.ty,
                                   name=node.target,
                                   dims=PLArray(elts=elts),
                                   ast_node=node,
                                   config=config)

        schedules = node.schedules
        num_schedules = len(schedules)
        sched_idx = self.count % num_schedules
        self.count = self.count + 1
        schedule = schedules[sched_idx]

        args_subs = []
        for array in node.arrays:
            args_subs.append(self.get_subscript(array, 'i_map_',
                             config, schedule))

        target_subs = self.get_subscript(node.target, 'i_map_',
                                         config, schedule)
        lambda_args = [arg.name for arg in node.func.args]

        target_subs.pl_type = PLType(node.pl_type.ty, 0)
        target_subs.pl_shape = tuple(1 for i in node.pl_shape)# assuming scalar

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
        new_lambda_body.pl_shape = target_subs.pl_shape
        new_lambda_body.pl_type = target_subs.pl_type

        node.func.body = new_lambda_body
        stmt = self.visit(node.func, config)

        orig_shape    = list(node.pl_shape)
        orig_ind_vars = [f'i_map_{i}' for i in range(len(orig_shape))]
        scheduled_shape    = PLSchedule(schedule).apply(orig_shape)
        scheduled_ind_vars = PLSchedule(schedule).apply(orig_ind_vars)

        loops = gen_loop_nest(scheduled_shape, stmt, 'map', scheduled_ind_vars)

        return [decl, loops]

        # # for i in range(len(node.pl_shape)-1, -1, -1):
        # for i in range(node.pl_type.dim - 1, -1, -1):
        #     target = PLVariable(f'i_map_{i}')
        #     target.pl_type = PLType('int', 0)
        #     target.pl_shape = ()

        #     stmt = [ PLFor(target=target,
        #                    iter_dom=PLIterDom(end=PLConst(node.pl_shape[i])),
        #                    body=stmt,
        #                    orelse=[],
        #                    source='map') ]

        # # add Merlin parallel pragma
        # if self.backend == 'merlin':
        #     stmt[0].iter_dom.attr = 'parallel'

        # return stmt[0]

    def visit_PLDot(self, node, config=None):

        op_type = node.op_type
        op_shape = node.op_shape

        tmp_var = PLVariable('tmp_dot')

        tmp_var.pl_type = PLType(ty=op_type.ty, dim=0)
        tmp_var.pl_shape = ()

        var_decl = PLVariableDecl(ty=op_type.ty,
                                  name=tmp_var,
                                  init=PLConst(0))

        var_decl.pl_type = PLType(ty=op_type.ty, dim=0)
        var_decl.pl_shape = ()

        op1_subs = self.get_subscript(node.op1, 'i_dot_', config)
        op2_subs = self.get_subscript(node.op2, 'i_dot_', config)

        op1_subs = self.visit(op1_subs, config)
        op2_subs = self.visit(op2_subs, config)

        op1_subs.pl_type = PLType(ty=op_type.ty, dim=0)
        op1_subs.pl_shape = tuple(1 for i in range(len(node.op1.pl_shape)))
        op2_subs.pl_type = PLType(ty=op_type.ty, dim=0)
        op2_subs.pl_shape = tuple(1 for i in range(len(node.op2.pl_shape)))

        mult = PLBinOp(op='*',
                       left=op1_subs,
                       right=op2_subs)

        mult.pl_type = PLType(ty=op_type.ty, dim=0)
        mult.pl_shape = ()

        stmt = [PLAssign(op='+=',
                         target=tmp_var,
                         value=mult)]

        stmt[0].pl_type = PLType(ty=op_type.ty, dim=0)
        stmt[0].pl_shape = ()
        stmt[0].is_decl = False

        for i in range(len(op_shape) - 1, -1, -1):
            target = PLVariable(f'i_dot_{i}')
            target.pl_type = PLType('int', 0)
            target.pl_shape = ()

            stmt = [ PLFor(target=target,
                           iter_dom=PLIterDom(end=PLConst(op_shape[i])),
                           body=stmt,
                           orelse=[],
                           source='dot') ]

        # write back to target

        if node.target:
            target = node.target
        elif hasattr(node, 'parent'):
            target = node.parent.target
        else:
            raise NotImplementedError

        write_back = PLAssign(op='=',
                              target=target,
                              value=tmp_var)
        write_back.pl_type = PLType(ty=node.pl_type.ty, dim=0)
        write_back.pl_shape = ()
        write_back.is_decl = False

        return [var_decl, stmt[0], write_back]
        # return stmt[0]

    def visit_PLFunctionDef(self, node, config=None):
        # breakpoint()
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


class PLOptimizer:
    def __init__(self, backend='vhls', debug=False):
        self.backend = backend
        self.debug = debug
        self.map_transformer = PLOptMapTransformer(backend, debug)

    def opt(self, node):
        self.map_transformer.visit(node)
        self.loops = get_loop_structure(node)

        if self.debug:
            print('PLOptimizer', self.loops)

        def unroll_innermost(loop_lst):
            assert (isinstance(loop_lst, list))
            for loop in loop_lst:
                if loop.subloops == []:
                    loop.unroll()
                else:
                    unroll_innermost(loop.subloops)

        # unroll_innermost(self.loops)
