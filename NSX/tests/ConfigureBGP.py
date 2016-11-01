from conf import *
from nsxramlclient.client import NsxClient


def BGP(edgeId, localAS, remoteAS, ip):

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

	routingBGP_template = session.extract_resource_body_example('routingBGP','update')
	#session.view_body_dict(routingBGP_template)

	bgp_template = routingBGP_template['bgp'].copy()

	session.view_body_dict(bgp_template)

	bgp_template['enabled'] = 'True'
	bgp_template['localAS'] = localAS
	bgp_template['bgpNeighbours']['bgpNeighbour']['ipAddress'] = '1.1.1.2'
	bgp_template['bgpNeighbours']['bgpNeighbour']['remoteAS'] = remoteAS


def main():

	BGP()

if __name__ == '__main__':
	exit(main())






