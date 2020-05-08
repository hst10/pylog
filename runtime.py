#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import numpy as np
import hashlib
import inspect

from pynq import Xlnk
from pynq import Overlay
from pynq import allocate

DESIGN_LIB = "/home/shuang91/vivado_projects/pylog_projects/"

class LogicInstance:
    def __init__(self, key=None):
        self.key = key


def load_design_keys(filename="design_keys"):
    fin = open(DESIGN_LIB+filename)
    keys = fin.read().strip().splitlines()
    fin.close()
    return keys

def pylog_go(func):

    def wrap_func(*args, **kwargs):
        source_func = inspect.getsource(func)
        for arg in args:
            assert(isinstance(arg, (np.ndarray, np.generic)))
            print(arg, type(arg))
        design_key = hashlib.md5(source_func.encode("UTF-8"))
        existing_keys = load_design_keys()
        # if design_key in existing_keys:

        # else:
        #     Print("Design doesn't exist. Need to run synthesis first. ")

    return wrap_func

class PLRuntime:
    def __init__(self, config):
        self.workspace_base = config['workspace_base']
        self.project_name = config['project_name']
        self.num_bundles = config['num_bundles']
        self.config = config
        self.xlnk = Xlnk()
        self.xlnk.xlnk_reset()

    def load_overlay(self):
        self.overlay = Overlay(f'{self.workspace_base}/{self.project_name}/{self.project_name}.bit')
        self.accelerator = getattr(self.overlay, f'{self.project_name}_0')

    def call(self, args):
        self.load_overlay()
        self.plrt_arrays = []
        curr_addr = 0x18
        for arg in args:
            new_array = allocate(shape=arg.shape, dtype=arg.dtype)
            np.copyto(new_array, arg)
            new_array.sync_to_device()
            self.accelerator.write(curr_addr, new_array.physical_address)
            curr_addr += 8
            self.plrt_arrays.append(new_array)

        print("FPGA starts. ")

        self.accelerator.write(0x00, 1)
        isready = self.accelerator.read(0x00)
        while( isready == 1 ):
            isready = self.accelerator.read(0x00)

        for i in range(len(self.plrt_arrays)):
            self.plrt_arrays[i].sync_from_device()
            np.copyto(args[i], self.plrt_arrays[i])
            self.plrt_arrays[i].close()
