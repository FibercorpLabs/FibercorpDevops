from conf import *
from nsxramlclient.client import NsxClient

EDGE_AS_1 = '54000'
EDGE_AS_2 = '55000'

session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

routingBGP_template = session.extract_resource_body_example('routingBGP','update')
#session.view_body_dict(routingBGP_template)

bgp_template = routingBGP_template['bgp'].copy()

session.view_body_dict(bgp_template)

bgp_template['enabled'] = 'True'
bgp_template['localAS'] = EDGE_AS_1
bgp_template['bgpNeighbours']['bgpNeighbour']['ipAddress'] = '1.1.1.2'
bgp_template['bgpNeighbours']['bgpNeighbour']['remoteAS'] = EDGE_AS_2






