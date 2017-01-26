from conf import *
from nsxramlclient.client import NsxClient


def BGP(edgeId, localAS, remoteAS, neighbourIP, routerId):

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

	uri_parameters = {}
	uri_parameters = {'edgeId': edgeId}

	routing_template = session.extract_resource_body_example('routingConfig','update')
	session.view_body_dict(routing_template)

	routingGlobal_template = routing_template['routing']['routingGlobalConfig']
	bgp_template = routing_template['routing']['bgp']
	
	routingGlobal_template['routerId'] = routerId
	bgp_template['enabled'] = 'true'
	bgp_template['localAS'] = localAS
	bgp_template['bgpNeighbours']['bgpNeighbour']['ipAddress'] = neighbourIP
	bgp_template['bgpNeighbours']['bgpNeighbour']['remoteAS'] = remoteAS

	bgp_template.pop('redistribution')
	bgp_template['bgpNeighbours']['bgpNeighbour'].pop('bgpFilters')
	routingGlobal_template.pop('ipPrefixes')
	routingGlobal_template.pop('logging')


	session.view_body_dict(bgp_template)
	session.view_body_dict(routingGlobal_template)

	response = session.update('routingConfig', uri_parameters, request_body_dict={'routing': {'bgp': bgp_template, 'routingGlobalConfig': routingGlobal_template}})
	session.view_response(response)
	
def main():

	BGP('edge-1367','64000','64001','200.200.200.2','1.1.1.1')
	BGP('edge-1368','64001','64000','200.200.200.1','1.1.1.2')

if __name__ == '__main__':
	exit(main())






