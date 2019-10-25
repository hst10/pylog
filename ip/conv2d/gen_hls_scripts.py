#!/usr/bin/python3


def gen_tcl_script(top_func, num_designs):

    import jinja2
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "run_hls.tcl.jinja"
    template = templateEnv.get_template(TEMPLATE_FILE)
    outputText = template.render(top_func=top_func, num_designs=num_designs)  # this is where to put args to the template renderer

    print(outputText, file=open("run_hls.tcl", "w"))


