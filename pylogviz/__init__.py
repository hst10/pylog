"""
PyLogViz: a tool for visualizing PyLog PLNode objects in a web server. 
Derived from InstaViz: https://github.com/tonybaloney/instaviz
"""
from .web import show_ast, show_pylog_object

def show(src, plnode_root):
    show_pylog_object(src, plnode_root)
