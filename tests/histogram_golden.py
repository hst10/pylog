import sys
sys.path.extend(['.', '..', '../..'])

from pylog import *

#adapted from https://github.com/KastnerRG/pp4fpgas histogram_parallel-top.cpp

#This configuration does not follow the original configuration in pp4fpga historgram_parallel
INPUT_SIZE=1048756
VALUE_SIZE=256

def init_array(in_arr, hist):
    in_arr[:]=np.random.randint(0,VALUE_SIZE,INPUT_SIZE)
    hist[:]=0
    return

@pylog(mode='hwgen',board='zedboard')
def pl_histogram_golden(in_arr, hist):
    for i in range(1048756): # TODO: replace hard coded 1048756 with INPUT_SIZE
        val=in_arr[i]
        hist[val]=hist[val]+1

if __name__=="__main__":
    in_arr=np.empty(INPUT_SIZE,dtype=np.int)
    hist=np.empty(VALUE_SIZE,dtype=np.int)
    init_array(in_arr,hist)
    pl_histogram_golden(in_arr,hist)
    pass