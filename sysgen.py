import os
import jinja2
import subprocess

TEMPLATE_DIR='/home/shuang91/pylog/tcl_temps/'

# list of supported boards
supported_boards = [
    'zedboard',
    'pynq',
    'ultra96'
]

# An example config:
config = {
    'project_name': 'pl_matmul',
    'project_path': '/home/shuang91/vivado_projects/pylog_projects/pl_matmul',
    'base_path':    '/home/shuang91/vivado_projects/pylog_projects',
    'freq':         125.00, 
    'top_name':     'matmul',
    'num_bundles':  3,
}


class PLSysGen:
    def __init__(self, board='pynq', config=None):
        self.target_board = board
        self.config = config
        if board not in supported_boards:
            print(f'{board} is not supported. Using pynq as target. ')
            self.target_board = 'pynq'

    def gen_configs(self, config=None):
        '''generate configs for Vivado and Vivado HLS tcl templates'''
        if config is None:
            config = self.config

        assert(config is not None)

        vivado_config = {
        'project_name': f"{config['project_name']}_{self.target_board}_vivado",
        'base_path':    config['project_path'],
        'ip_repo_path': config['project_path'] + \
                        f"/{config['project_name']}_{self.target_board}_hls/" +
                        f"solution1",
        'pl_freq':      config['freq'],
        'ip_name':      config['top_name'],
        'num_hp_ports': config['num_bundles'],
        'bundle':       [ f'DATA_{i}' for i in range(config['num_bundles']) ]
        }

        hls_config = {
        'hls_base_path':    config['project_path'],
        'hls_project_name': f"{config['project_name']}_{self.target_board}_hls",
        'hls_top':          config['top_name'],
        'hls_file_name':    config['top_name'] + '.cpp',
        'hls_freq':         config['freq']
        }

        return vivado_config, hls_config

    def generate_system(self, config):
        if config is None:
            config = self.config

        assert(config is not None)

        project_path = config['project_path']
        project_name = config['project_name']
        if not os.path.exists(project_path):
            os.makedirs(project_path)
        # else:
        #     print(f"Directory {project_path} exists! Overwriting... ")

        vivado_config, hls_config = self.gen_configs(config)
        
        template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATE_DIR)
        template_env = jinja2.Environment(loader=template_loader)
        hls_template = f"{self.target_board}_hls.tcl.jinja"
        template = template_env.get_template(hls_template)
        output_text = template.render(hls_config)

        hls_tcl_script = f"{project_path}/run_hls.tcl"

        print(output_text, file=open(hls_tcl_script, "w"))

        vivado_template = f"{self.target_board}_vivado.tcl.jinja"
        template = template_env.get_template(vivado_template)
        output_text = template.render(vivado_config)

        vivado_tcl_script = f"{project_path}/run_vivado.tcl"

        print(output_text, file=open(vivado_tcl_script, "w"))

        process = subprocess.call(
            f"cd {project_path}; " + \
            f"vivado_hls -f {hls_tcl_script}; " + \
            f"cd -;",
            shell=True)

        process = subprocess.call(
            f"cd {project_path}; " + \
            f"vivado -mode batch -source {vivado_tcl_script}; " + \
            f"cd -;",
            shell=True)

        print("project_path = ", project_path)

        process = subprocess.call(
            f"cd {project_path}; " + \
            f"cp ./{project_name}_{self.target_board}_vivado/" + \
            f"{project_name}_{self.target_board}_vivado.runs/impl_1/"+\
            f"design_1_wrapper.bit ./{project_name}_{self.target_board}.bit;"+\
            f"cd -;",
            shell=True)

        process = subprocess.call(
            f"cd {project_path}; " + \
            f"cp ./{project_name}_{self.target_board}_vivado/" + \
            f"{project_name}_{self.target_board}_vivado.srcs/sources_1/bd/" + \
            f"design_1/hw_handoff/design_1.hwh " + \
            f" ./{project_name}_{self.target_board}.hwh; " + \
            f"cd -;",
            shell=True)

if __name__ == '__main__':
    plsysgen = PLSysGen(board='ultra96')
    plsysgen.generate_system(config)
