import jinja2

Global_IP_file_path = {"conv1d" : "ip_template/convolve_1d",
"matmul" : "ip_template/matrixmultiplication",
"argmax_pipe" : "ip_template/find/argmax_pipe",
"argmax_nonepipe" : "ip_template/find/argmax_nonepipe",
"argmin" : "ip_template/find/argmin",
"max" : "ip_template/find/max",
"min" : "ip_template/find/min",
"sort_insertion": "ip_template/sort/insertion_sort_parallel",
"sort_merge": "ip_template/sort/merge_sort_parallel",
"sort_insertion_it": "ip_template/sort_itself/insertion_sort_itself",
"sort_merge_it": "ip_template/sort_itself/merge_sort_loop_merged",
"spmv" : "ip_template/spmv/spmv",
"spmv-re" : "ip_template/spmv/spmv_restructured",
"testip" : "ip_template/testip"
}

Global_IP_versions = {
"argmax" : [ "argmax_pipe",  "argmax_nonepipe"]
}

Global_IP_args = {
"conv1d" : {
                    'type' : ['d0','d0','d0'], 
                    'shape': ['s0','s1','s2'],
                    'dim'  : [1,1,1],
                    'ret'  : 'void gf' },
"matmul" : {
                    'type' : ['d0','d0','d0'], 
                    'shape': [['s0','s1'],['s1','s2'],['s0','s2']],
                    'dim'  : [2,2,2],
                    'ret'  : 'void' },
"argmax" : {
                    'type' : ['d0'], 
                    'shape': ['s0'],
                    'dim'  : [1],
                    'ret'  : 'int' },
"argmix" : {
                    'type' : ['d0'], 
                    'shape': ['s0'],
                    'dim'  : [1],
                    'ret'  : 'int' },
"max"    : {
                    'type' : ['d0'], 
                    'shape': ['s0'],
                    'dim'  : [1],
                    'ret'  : 'd0' },
"min"    : {
                    'type' : ['d0'], 
                    'shape': ['s0'],
                    'dim'  : [1],
                    'ret'  : 'd0' },
"sort_insertion": {
                    'type' : ['d0','d0'], 
                    'shape': ['s0','s0'],
                    'dim'  : [1,1],
                    'ret'  : 'void' },
"sort_merge"    : {
                    'type' : ['d0','d0'], 
                    'shape': ['s0','s0'],
                    'dim'  : [1,1],
                    'ret'  : 'void' },
"sort_insertion_it" : {
                    'type' : ['d0'], 
                    'shape': ['s0'],
                    'dim'  : [1],
                    'ret'  : 'void' },
"sort_merge_it" : {
                    'type' : ['d0'], 
                    'shape': ['s0'],
                    'dim'  : [1],
                    'ret'  : 'void' },
"spmv"    : {
                    'type' : ['int','int','d0', 'd0', 'd0'], 
                    'shape': ['s0','s1','s1','s2','s2'],
                    'dim'  : [1,1,1,1,1],
                    'ret'  : 'void' },
"spmv-re" : {
                    'type' : ['int','int','d0', 'd0', 'd0'], 
                    'shape': ['s0','s1','s1','s2','s2'],
                    'dim'  : [1,1,1,1,1],
                    'ret'  : 'void' }
,"testip" : {
                    'type' : ['int','d0'], 
                    'shape': ['s0','s1'],
                    'dim'  : [ 1,1],
                    'ret'  : 'void' }
}

Global_IP_func_configs = {
"conv1d" : ['d0', 's0', 's1', 's2'], 
"matmul" : ['d0', 's0', 's1', 's2'], 
"argmax" : ['d0', 's0'], 
"argmix" : ['d0', 's0'], 
"max"    : ['d0', 's0'], 
"min"    : ['d0', 's0'], 
"sort_insertion": ['d0', 's0'], 
"sort_merge"    : ['d0', 's0'], 
"sort_insertion_it" : ['d0', 's0'], 
"sort_merge_it" : ['d0', 's0'], 
"spmv"    :  ['d0', 's0', 's1', 's2'],
"spmv-re" :  ['d0', 's0', 's1', 's2'],
"testip" :  ['d0', 's0', 's1']
}



Global_IP_optm_configs_Default = {
"conv1d" : {'v0':10, 'v1':10}, 
"matmul" : {'v0':1}, 
"argmax_pipe" : { }, 
"argmax_nonepipe" : {'kernel_size' : 4 }, 
"argmix" : {'v1':10, 'v2':10},  
"max"    : {'v1':10, 'v2':10},  
"min"    : {'v1':10, 'v2':10}, 
"sort_insertion": {'v0':16, 'v1':1}, 
"sort_merge"    : {'v0':4}, 
"sort_insertion_it" : {'v0':2, 'vm':100}, 
"sort_merge_it" : {'v0':16, 'v1':1}, 
"spmv"    : {'v1':10, 'v2':10}, 
"spmv-re" : {'v1':10, 'v2':10}, 
"testip" : {'v1':10, 'v2':10}
}
