import os
import glob
import json
import time
import jinja2
import subprocess

TEMPLATE_DIR=r'D:\github-repos\logicpy\tcl_temps'

# list of supported boards
supported_boards = [
    'zedboard',
    'pynq',
    'ultra96',
    'aws_f1',
    'alveo_u200',
    'alveo_u250',
    'alveo_u280'
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

        self.using_vitis = (board == 'aws_f1' or board.startswith('alveo'))


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
        'bundle':       [ f'data{i}' for i in range(config['num_bundles']) ]
        }

        hls_config = {
        'hls_base_path':   config['project_path'],
        'hls_project_name':f"{config['project_name']}_{self.target_board}_hls",
        'hls_top':         config['top_name'],
        'hls_file_name':   config['top_name'] + '.cpp',
        'hls_freq':        config['freq'],
        'hls_board':       self.target_board
        }

        return vivado_config, hls_config

    def get_afi_id(self, txt_file):
        with open(txt_file) as f:
            content = f.read()
            data = json.loads(content)
            return data['FpgaImageId']

    def get_afi_status(self, afi_id):
        info = subprocess.Popen(
            f'aws ec2 describe-fpga-images --fpga-image-ids {afi_id}',
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     shell=True)
        stdout, stderr = info.communicate()
        data = json.loads(stdout)
        status = data['FpgaImages'][0]['State']['Code']
        return status

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

        hls_tcl_script = os.path.join(f"{project_path}","run_hls.tcl")

        print(output_text, file=open(hls_tcl_script, "w"))

        if not self.using_vitis:
            vivado_template = f"{self.target_board}_vivado.tcl.jinja"
            template = template_env.get_template(vivado_template)
            output_text = template.render(vivado_config)

            vivado_tcl_script = os.path.join(f"{project_path}","run_vivado.tcl")

            print(output_text, file=open(vivado_tcl_script, "w"))

        if os.name=="nt":
            process = subprocess.call(
                f"cd {project_path} && " + \
                f"vivado_hls.bat -f {hls_tcl_script} && " + \
                f"cd ..",
                shell=True)

            process = subprocess.call(
                f"cd {project_path} && " + \
                f"vivado.bat -mode batch -source {vivado_tcl_script} && " + \
                f"cd ..",
                shell=True)

            print("project_path = ", project_path)

            process = subprocess.call(f"cd {project_path} && COPY " +os.path.join(".",f"{project_name}_{self.target_board}_vivado",f"{project_name}_{self.target_board}_vivado.runs",f"impl_1",f"design_1_wrapper.bit")+" " +os.path.join(".",f"{project_name}_{self.target_board}.bit")+" && "+f"cd ..",shell=True)

            process = subprocess.call(
                f"cd {project_path} && COPY "+os.path.join(".",f"{project_name}_{self.target_board}_vivado",f"{project_name}_{self.target_board}_vivado.srcs","sources_1","bd","design_1","hw_handoff","design_1.hwh")+" " + os.path.join(".",f"{project_name}_{self.target_board}.hwh")+"&& cd ..",shell=True)


        else:
            if self.target_board == 'aws_f1':
                if 'RELEASE_VER' not in os.environ:
                    print('Please source vitis_setup.sh first.')
                    exit(-1)
                if 'AWS_PLATFORM' in os.environ:
                    platform = os.environ['AWS_PLATFORM']
                else:
                    print("Please set $AWS_PLATFORM to platform file path.")
                    exit(-1)

                if 'VITIS_DIR' in os.environ:
                    vitis_dir = os.environ['VITIS_DIR']
                else:
                    print("Please set $VITIS_DIR to AWS Vitis directory.")
                    exit(-1)

                if 'S3_BUCKET' in os.environ:
                    s3_bucket = os.environ['S3_BUCKET']
                else:
                    print("Please set $S3_BUCKET to S3 bucket name.")
                    exit(-1)

                if 'S3_DCP' in os.environ:
                    s3_dcp = os.environ['S3_DCP']
                else:
                    print("Please set $S3_DCP to S3 dcp directory name.")
                    exit(-1)

                if 'S3_LOGS' in os.environ:
                    s3_logs = os.environ['S3_LOGS']
                else:
                    print("Please set $S3_LOGS to S3 logs directory name.")
                    exit(-1)


            elif self.target_board == 'alveo_u200':
                platform = 'xilinx_u200_xdma_201830_2'
            elif self.target_board == 'alveo_u250':
                platform = 'xilinx_u250_xdma_201830_2'
            elif self.target_board == 'alveo_u280':
                platform = 'xilinx_u280_xdma_201920_3'

            process = subprocess.call(
                f" cd {project_path}; " + \
                f" v++ -t hw --platform {platform} " + \
                f" --link {project_name}_{self.target_board}.xo "+\
                f" -o {project_name}_{self.target_board}.xclbin; cd -;",
                shell=True)

            if self.target_board == 'aws_f1':

                print("Start creating Amazon FPGA Image (AFI)...")
                process = subprocess.call(
                    f" cd {project_path}; " + \
                    f" {vitis_dir}/tools/create_vitis_afi.sh " + \
                    f" -xclbin={project_name}_{self.target_board}.xclbin " + \
                    f" -o={project_name}_{self.target_board} " + \
                    f" -s3_bucket={s3_bucket} -s3_dcp_key={s3_dcp} " + \
                    f" -s3_logs_key={s3_logs}; cd -;",
                    shell=True)

                print("Amazon FPGA Image (AFI) creation requested. ")

                list_of_files = glob.glob(f'{project_path}/*_afi_id.txt')
                latest_afi = max(list_of_files, key=os.path.getctime)

                afi_id = self.get_afi_id(latest_afi)
                status = self.get_afi_status(afi_id)

                print("Waiting for Amazon FPGA Image (AFI) creation... ")

                while status == 'pending':
                    time.sleep(10)
                    status = self.get_afi_status(afi_id)

                if status == 'available':
                    print("Amazon FPGA Image (AFI) creation done. ")
                else:
                    print(f"Error in AFI creation. Status: {status}. ")

if __name__ == '__main__':
    plsysgen = PLSysGen(board='ultra96')
    plsysgen.generate_system(config)
