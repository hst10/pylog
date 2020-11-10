from IPinforms import *
import jinja2
import numpy as np

def analyze_ip_configuration(node):
    ip_config = {}
    if (len(node.func_configs)!=len(Global_IP_func_configs[node.name])):
        print('The number of func_configs is incorrect!')
        raise NameError

    for i in node.func_configs:
        if i in Global_IP_func_configs[node.name]:
            ip_config[i] = node.func_configs[i]
        else:
            print(f'func_configs {i} should not appear!')
            raise NameError

    for i in Global_IP_optm_configs_Default[analyze_ip_versions(node)]:
        if i in node.optm_configs:
            ip_config[i] = node.optm_configs[i]
        else:
            ip_config[i] = Global_IP_optm_configs_Default[analyze_ip_versions(node)][i]
    
    if node.name == "argmax":
        if ('version' not in node.optm_configs ) or node.optm_configs['version'] == 0:
            ip_config['log2_kernel_size']  =  int(np.log2(ip_config['s0']))
        else:
            ip_config['log2_kernel_size']  =  int(np.log2(ip_config['kernel_size']))
            ip_config['II']  = int(ip_config['s0']) /int(ip_config['kernel_size'])


    return ip_config


def analyze_ip_versions(node):
    ip_name = node.name
    if (node.name in Global_IP_versions ):
        if 'version' in node.optm_configs:
            ip_name = Global_IP_versions[node.name][node.optm_configs['version']  ]
        else:
            ip_name = Global_IP_versions[node.name][0]
    return ip_name



def ip_generator(node,project_path, recordip):
    
    ip_name = analyze_ip_versions(node)
    ip_config = analyze_ip_configuration(node)

    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    file_path = Global_IP_file_path[ip_name]
    template_cpp = templateEnv.get_template(file_path+'.cpp.jinja')
    template_h = templateEnv.get_template(file_path+'.h.jinja')

    ip_config['recordip'] = recordip
    cppoutputText = template_cpp.render(ip_config)  # where to put args to the template renderer    
    houtputText = template_h.render(ip_config)
    f_h = open(project_path+"/"+ip_name+'_'+str(recordip)+".h",'w')
    f_cpp = open(project_path+"/"+ip_name+'_'+str(recordip)+".cpp",'w')
    f_h.write(houtputText)
    f_cpp.write(cppoutputText)

    file_h= project_path+"/configured_IPcores.h"
    include_str = f'#include "{ip_name}_{str(recordip)}.h"\n'
    if recordip == 0:
        f = open(file_h,'w')
        f.close()
    f=open(file_h, "a+")
    f.writelines(include_str)

    f.close()
    f_h.close()
    f_cpp.close()



    

