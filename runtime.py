#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import time
import numpy as np
import hashlib
import inspect

# DESIGN_LIB = "/home/ubuntu/vivado_projects/pylog_projects/"

# class LogicInstance:
#     def __init__(self, key=None):
#         self.key = key


# def load_design_keys(filename="design_keys"):
#     fin = open(DESIGN_LIB+filename)
#     keys = fin.read().strip().splitlines()
#     fin.close()
#     return keys

# def pylog_go(func):

#     def wrap_func(*args, **kwargs):
#         source_func = inspect.getsource(func)
#         for arg in args:
#             assert(isinstance(arg, (np.ndarray, np.generic)))
#             print(arg, type(arg))
#         design_key = hashlib.md5(source_func.encode("UTF-8"))
#         existing_keys = load_design_keys()
#         # if design_key in existing_keys:

#         # else:
#         #     Print("Design doesn't exist. Need to run synthesis first. ")

#     return wrap_func

class PLRuntime:
    def __init__(self, config):
        self.board = config['board']
        self.timing = config['timing']
        self.workspace_base = config['workspace_base']
        self.project_name = config['project_name']
        self.num_bundles = config['num_bundles']
        self.return_void = config['return_void']
        self.config = config

    def call(self, args):
        if self.board == 'aws_f1' or self.board.startswith('alveo'):
            return self.call_xrt(args)
        else:
            return self.call_soc(args)

    def call_soc(self, args):
        from pynq import Xlnk
        from pynq import Overlay
        # from pynq import allocate  # requires PYNQ v2.5 or newer

        self.xlnk = Xlnk()
        self.xlnk.xlnk_reset()

        self.overlay = Overlay(f'{self.workspace_base}/{self.project_name}/'+\
                               f'{self.project_name}_{self.board}.bit')
        self.accelerator = getattr(self.overlay, f'{self.project_name}_0')

        self.plrt_arrays = []
        curr_addr = 0x10 if self.return_void else 0x18
        for i in range(len(args)):
            if args[i].shape == ():
                self.accelerator.write(curr_addr, args[i])
            else:
                # "allocate" requires PYNQ v2.5 or newer
                # new_array = allocate(shape=arg.shape, dtype=arg.dtype)
                new_array = self.xlnk.cma_array(args[i].shape, args[i].dtype)
                np.copyto(new_array, args[i])
                # new_array.sync_to_device() # requires PYNQ v2.5 or newer
                new_array.flush()
                self.accelerator.write(curr_addr, new_array.physical_address)
                self.plrt_arrays.append((i, new_array))
            curr_addr += 8

        print("FPGA starts. ")

        start_time = time.time()

        self.accelerator.write(0x00, 1)
        isready = self.accelerator.read(0x00)
        while( isready == 1 ):
            isready = self.accelerator.read(0x00)

        end_time = time.time()

        fpga_time = end_time - start_time

        print("FPGA finishes. ")
        if self.timing:print(f'FPGA Execution Time: {fpga_time:.10f} s')

        for i, array in self.plrt_arrays:
            # "sync_from_device" only available starting PYNQ v2.5
            # self.plrt_arrays[i].sync_from_device()
            array.invalidate()
            np.copyto(args[i], array)
            array.close()

        return self.accelerator.read(0x10)

    def call_xrt(self, args):
        from pynq import Overlay
        from pynq import allocate  # requires PYNQ v2.5 or newer

        ext = 'awsxclbin' if (self.board == 'aws_f1') else 'xclbin'

        self.overlay = Overlay(f'{self.workspace_base}/{self.project_name}/'+\
                               f'{self.project_name}_{self.board}.{ext}')
        self.accelerator = getattr(self.overlay, f'{self.project_name}_1')

        self.plrt_arrays = []
        self.plrt_args = []
        for i in range(len(args)):
            if args[i].shape == ():
                self.plrt_args.append(args[i])
            else:
                # "allocate" requires PYNQ v2.5 or newer
                new_array = allocate(shape=args[i].shape, dtype=args[i].dtype)
                np.copyto(new_array, args[i])
                new_array.sync_to_device() # requires PYNQ v2.5 or newer
                self.plrt_arrays.append((i, new_array))
                self.plrt_args.append(new_array)

        print("FPGA starts. ")

        start_time = time.time()

        result = self.accelerator.call(*self.plrt_args)

        end_time = time.time()

        fpga_time = end_time - start_time

        print("FPGA finishes. ")
        if self.timing:  print(f'FPGA Execution Time: {fpga_time:.10f} s')

        for i, array in self.plrt_arrays:
            # "sync_from_device" only available starting PYNQ v2.5
            array.sync_from_device()
            np.copyto(args[i], array)
            array.close()

        self.overlay.free()

        return result
