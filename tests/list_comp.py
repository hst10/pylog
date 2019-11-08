import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/newhdd/logicpy/')

from logicpy import *

logicpy_compile("[a**2 for a in list_a if a +1 for b in list_b if a == b]")
