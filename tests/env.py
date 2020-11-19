import sys
import os
pylog_path = os.environ.get('PYLOGPATH')
if pylog_path == None:
    print("[ERROR] Please do `source ./pylog_init` before run test/env.py script")
else:
    sys.path.extend([pylog_path])
