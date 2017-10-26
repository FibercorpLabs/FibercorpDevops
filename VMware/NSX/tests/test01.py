import sys
import jinja2

sys.path.append("../utils/")

from nsx_crud import *

def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)

    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)

nsx_edge_xml, jinja_vars = createEdge("data1", "some1", "descriptIOnN", "xL", "rs-1", "ds-1", "idx99", "vnicSome", "UPLINK",
  "pg0101", "192.168.0.1", "255.255.255.0", "1500", "True", "user01", "jaja123", "True")

#print render(nsx_edge_xml, jinja_vars)


