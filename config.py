# Please modify the following line to your actual PyLog root path
PYLOG_ROOT_DIR = '/home/ubuntu/pylog'

# Directory for generated Vitis/Vivado project files
WORKSPACE = PYLOG_ROOT_DIR + '/pylog_projects'

# # Only used in deploy mode (for scp'ing bitstreams and configurations):
# HOST_ADDR = 'ubuntu@localhost'
# TARGET_ADDR = 'ubuntu@localhost'

# The project path on TARGET FPGA system, only used in deploy mode
TARGET_BASE = '/home/ubuntu/pylog_projects'

# Used in sysgen.py
TEMPLATE_DIR = PYLOG_ROOT_DIR + '/boards/'

HLS_CMD = 'vitis_hls'
