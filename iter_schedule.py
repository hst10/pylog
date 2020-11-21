from nodes import *

class PLSchedule:
    def __init__(self, schedule):
        self.schedule = schedule
        self.mapping = None

    def replace_variable(self, root, name, new_node):
        for node in plnode_walk(root):
            replace_child_generic(
                node, 
                lambda n: True if isinstance(n, PLVariable) and 
                                  (n.name == name) else False,
                new_node)

    def interchange_list(self, nest, idx_a, idx_b):
        if len(nest) == 0:
            return
        assert(isinstance(nest, list))
        nest[idx_a], nest[idx_b] = nest[idx_b], nest[idx_a]
        return nest

    def interchange_PLSubscript(self, nest, idx_a, idx_b):
        assert(isinstance(nest, PLSubscript))
        # Loop interchange doesn't change subscript index variables
        # nest.indices = self.interchange_list(nest.indices, idx_a, idx_b)
        # self.mapping = list(range(len(nest.indices)))
        self.mapping = self.interchange_list(self.mapping, idx_a, idx_b)
        return nest

    def tile_list(self, nest, loop_idx, tile_size):
        if len(nest) == 0:
            return
        assert(isinstance(nest, list))

        if isinstance(nest[0], str):
            org_var = f'{nest[loop_idx]}'
            nest[loop_idx] = f'{org_var}0'
            nest.insert(loop_idx+1, f'{org_var}1')
        else:
            org_size = nest[loop_idx]
            assert(isinstance(org_size, int))
            if org_size % tile_size != 0:
                print("WARNING: loop size not divisible by tile size.")
            new_size = (org_size + tile_size - 1) // tile_size
            nest[loop_idx] = new_size
            nest.insert(loop_idx+1, tile_size)
        return nest

    def tile_PLSubscript(self, nest, loop_idx, tile_size, iter_prefix):
        assert(isinstance(nest, PLSubscript))
        actual_loop_idx = self.mapping[loop_idx]
        variable_name = f'{iter_prefix}{actual_loop_idx}'
        new_expr = PLVariable(f'{variable_name}0') * tile_size
        new_expr = new_expr + PLVariable(f'{variable_name}1')
        self.mapping[loop_idx] = actual_loop_idx + '0'
        self.mapping.insert(loop_idx+1, actual_loop_idx + '1')
        self.replace_variable(nest, variable_name, new_expr)
        return nest

    def error(self):
        raise NotImplementedError

    def apply(self, nest, iter_prefix=None):
        assert(isinstance(nest, (list, PLSubscript)))
        if isinstance(nest, list):
            self.mapping = [ str(i) for i in range(len(nest))]
        else:
            self.mapping = [ str(i) for i in range(len(nest.indices))]
        nest_type = nest.__class__.__name__
        for s in self.schedule:
            action, *args = s
            func_name = f'{action}_{nest_type}'
            func = getattr(self, f'{func_name}', self.error)
            if func_name == 'tile_PLSubscript':
                nest = func(nest, *args, iter_prefix)
            else:
                nest = func(nest, *args)
        return nest

if __name__ == "__main__":
    s = PLSchedule([('interchange', 1, 3), ('tile', 2, 8)])
    nest = [43, 5, 64, 4]
    a = s.apply(nest)
    print(a)
