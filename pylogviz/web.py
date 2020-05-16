"""
Entry points for managing a micro-http server to serve tables.
"""
import sys
sys.path.append('..')
from nodes import *

import json
from bottle import run, jinja2_view, route, static_file, TEMPLATE_PATH
import os
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from dill import source

data = {}


@route("/static/<filename>")
def server_static(filename):
    abs_app_dir_path = os.path.dirname(os.path.realpath(__file__))
    root_path = os.path.join(abs_app_dir_path, 'static')
    return static_file(filename, root=root_path)


@route("/", name="home")
@jinja2_view("home.html")
def home():
    global data
    data["style"] = HtmlFormatter().get_style_defs(".highlight")
    data["code"] = highlight(
        "".join(data["src"]),
        PythonLexer(),
        HtmlFormatter(
            linenos=True, linenostart=0, linespans="src"
        ),
    )
    return data


def start(host="localhost", port=8080):
    """
    Run the web server
    """
    # set TEMPLATE_PATH to use an absolute path pointing to our directory
    abs_app_dir_path = os.path.dirname(os.path.realpath(__file__))
    abs_views_path = os.path.join(abs_app_dir_path, "templates")
    TEMPLATE_PATH.insert(0, abs_views_path)
    run(host=host, port=port)
    print(f"Running web-server on http://{host}:{port}/")


def dedupe_nodes(l):
    new_list = []
    ids_collected = []
    for i in l:
        if i["id"] not in ids_collected:
            new_list.append(i)
            ids_collected.append(i["id"])
    return new_list


def iter_fields(node):
    """
    Yield a tuple of ``(fieldname, value)`` for each field in
    ``node._fields`` that is present on *node*.
    """
    if isinstance(node, list):
        yield 'list', node
    elif isinstance(node, PLNode):
        for field in node._fields:
            try:
                yield field, getattr(node, field)
            except AttributeError:
                pass

def iter_child_nodes(node):
    """
    Yield all direct child nodes of *node*, that is, all fields that are nodes
    and all items of fields that are lists of nodes.
    """
    if isinstance(node, list):
        for item in node:
            yield item
    elif isinstance(node, PLNode):
        for name, field in iter_fields(node):
            if isinstance(field, PLNode):
                yield field
            elif isinstance(field, list):
                for item in field:
                    if isinstance(item, PLNode):
                        yield item


def node_properties(node):
    d = {}
    for field, value in iter_fields(node):
        if isinstance(value, PLNode):
            d[field] = node_properties(value)
        elif (
            isinstance(value, list) and len(value) > 0 and isinstance(value[0], PLNode)
        ):
            d[field] = [node_properties(v) for v in value]
        else:
            d[field] = value
    return d


def node_to_dict(node, parent):
    i = []
    children = list(iter_child_nodes(node))
    if len(children) > 0:
        for n in children:
            i.extend(node_to_dict(n, node))

    d = node_properties(node)

    i.append(
        {
            "id": id(node),
            "name": type(node).__name__,
            "parent": id(parent),
            "data": json.dumps(d, skipkeys=True),
        }
    )
    return i


def show_pylog_object(src, plnode_root):
    """
    Render code object
    """
    global data

    nodes = node_to_dict(plnode_root, None)
    data["nodes"] = dedupe_nodes(nodes)
    data["src"] = src
    data["last_line"] = src.count('\n')

    print(data['nodes'])

    start()


def show_ast(ast):
    # Not implemented
    pass
