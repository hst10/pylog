import os
import jinja2
import subprocess

# list of supported boards
supported_boards = [
    'zedboard',
    'pynq'
]

# example config: 


config = {
    'project_name': 'pl_matmul',
    'base_path':    '/home/shuang91/vivado_projects',
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
            'project_name': config['project_name'] + '_vivado',
            'base_path':    config['base_path'] + '/' + config['project_name'],
            'ip_repo_path': config['base_path'] + '/' + config['project_name'] + \
                                    f"/{config['project_name']}_hls/solution1",
            'pl_freq':      config['freq'], 
            'ip_name':      config['top_name'],
            'num_hp_ports': config['num_bundles'],
            'bundle':       [ f'DATA_{i}' for i in range(config['num_bundles']) ]
        }

        hls_config = {
            'hls_base_path':    config['base_path'] + '/' + config['project_name'],
            'hls_project_name': f"{config['project_name']}_hls",
            'hls_top':          config['top_name'],
            'hls_file_name':    config['top_name'] + '.cpp',
            'hls_freq':         config['freq']
        }

        return vivado_config, hls_config

    def generate_system(self, config):
        if config is None:
            config = self.config

        assert(config is not None)

        project_path = f"{config['base_path']}/{config['project_name']}"
        if not os.path.exists(project_path):
            os.makedirs(project_path)
        else:
            print(f"Directory {project_path} exists! Overwriting the directory. ")

        vivado_config, hls_config = self.gen_configs(config)
        
        template_loader = jinja2.FileSystemLoader(searchpath="./tcl_temps/")
        template_env = jinja2.Environment(loader=template_loader)
        hls_template = f"{self.target_board}_hls.tcl.jinja"
        template = template_env.get_template(hls_template)
        output_text = template.render(hls_config)  # this is where to put args to the template renderer

        hls_tcl_script = f"{project_path}/run_hls.tcl"

        print(output_text, file=open(hls_tcl_script, "w"))

        vivado_template = f"{self.target_board}_vivado.tcl.jinja"
        template = template_env.get_template(vivado_template)
        output_text = template.render(vivado_config)  # this is where to put args to the template renderer

        vivado_tcl_script = f"{project_path}/run_vivado.tcl"

        print(output_text, file=open(vivado_tcl_script, "w"))

        process = subprocess.call(f"cd {project_path}; vivado_hls -f {hls_tcl_script}; cd -;", shell=True)
        process = subprocess.call(f"cd {project_path}; vivado -mode batch -source {vivado_tcl_script}; cd -;", shell=True)

if __name__ == '__main__':
    plsysgen = PLSysGen(board='zedboard')
    plsysgen.generate_system(config)
