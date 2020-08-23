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
def pl_histogram_parallel4(in_arr1, in_arr2, in_arr3, in_arr4, hist):
    def histogram_map4(in_arr, hist):
        pragma("HLS DEPENDENCE variable=hist intra RAW false")
        for i in range(256):#TODO: replace hard coded 256 with VALUE_SIZE
            pragma("HLS PIPELINE II=1")
            hist[i]=0
        old=in_arr[0]
        acc=0
        for i in range(1048756/4):#TODO: replace hard coded 1048756 with INPUT_SIZE
            pragma("HLS PIPELINE II=1")
            val=in_arr[i]
            if old == val:
                acc=acc+1
            else:
                hist[old]=acc
                acc=hist[val]+1
            old=val
        hist[old]=acc

    def histogram_reduce4(hist1, hist2, hist3, hist4, output):
        for i in range(256):#TODO: replace hard coded 256 with VALUE_SIZE
            pragma("HLS PIPELINE II=1")
            output[i]=hist1[i]+hist2[i]+hist3[i]+hist4[i]


    hist1=np.empty([256],np.int)#TODO: replace hard coded 256 with VALUE_SIZE
    hist2=np.empty([256],np.int)#TODO: replace hard coded 256 with VALUE_SIZE
    hist3=np.empty([256],np.int)#TODO: replace hard coded 256 with VALUE_SIZE
    hist4=np.empty([256],np.int)#TODO: replace hard coded 256 with VALUE_SIZE

    histogram_map4(in_arr1,hist1)#TODO: replace hard coded 1048756 with INPUT_SIZE
    histogram_map4(in_arr2,hist2)#TODO: replace hard coded 1048756 with INPUT_SIZE
    histogram_map4(in_arr3,hist3)#TODO: replace hard coded 1048756 with INPUT_SIZE
    histogram_map4(in_arr4,hist4)#TODO: replace hard coded 1048756 with INPUT_SIZE
    histogram_reduce4(hist1,hist2,hist3,hist4,hist)

if __name__=="__main__":
    in_arr=np.empty(INPUT_SIZE,dtype=np.int)
    hist=np.empty(VALUE_SIZE,dtype=np.int)
    init_array(in_arr,hist)
    pl_histogram_parallel4(in_arr[:INPUT_SIZE//4],in_arr[INPUT_SIZE//4:INPUT_SIZE*2//4],in_arr[INPUT_SIZE*2//4:INPUT_SIZE*3//4],in_arr[INPUT_SIZE*3//4:],hist)
    pass