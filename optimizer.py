from nodes import *

class PLOptimizer:

    def __init__(self, debug=False):
        self.debug = debug

    def visit(self, node):
        """Visit a node."""

        if self.debug:
            print(f'OPT visiting {node.__class__.__name__}, {node}')

        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        visit_return = visitor(node)

        return visit_return

    def generic_visit(self, node):
        for field, old_value in iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, PLNode):
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, PLNode):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, PLNode):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node

    def visit_list(self, node):
        return [ self.visit(item) for item in node ]

    def visit_PLMap(self, node):
        assert(hasattr(node, 'parent') and isinstance(node.parent, PLAssign))

        for_node = PLFor(target=PLVariable(name='i'),
                         iter_dom=PLIterDom(end=PLConst(1024)),
                         body=[ PLBinOp(op='@',
                                        left=PLVariable(name='left'),
                                        right=PLVariable(name='right'))],
                         orelse=[])
        return for_node
