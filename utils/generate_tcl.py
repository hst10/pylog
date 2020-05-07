import jinja2

templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE = "../tcl_temps/pynq_vivado.tcl.jinja"
template = templateEnv.get_template(TEMPLATE_FILE)

config = {
    'project_name': 'jinja_vivado',
    'base_path':    '/home/shuang91/vivado_projects',
    'ip_repo_path': '/home/shuang91/vivado_projects/hls_test_project/solution1',
    'pl_freq':      100.00, 
    'ip_name':      'matmul',
    'num_hp_ports': 3,
    'bundle':       [ 'DATA_INPUT_A', 'DATA_INPUT_B', 'DATA_OUTPUT' ]
}

outputText = template.render(config)  # this is where to put args to the template renderer

print(outputText, file=open("run_vivado.tcl", "w"))
