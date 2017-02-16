from nsxramlclient.client import NsxClient
from CRUD import Edge

class bgp(object):
	def __init__(self, session):
		self.session = session
		
	def create(self, **kwargs):
		uri_parameters = {}
		uri_parameters = {'edgeId': kwargs['edgeId']}

		routing_template = self.session.extract_resource_body_example('routingConfig',
			'update')
		self.session.view_body_dict(routing_template)

		routingGlobal_template = routing_template['routing']['routingGlobalConfig']
		bgp_template = routing_template['routing']['bgp']
		
		routingGlobal_template['routerId'] = kwargs['routerId']
		bgp_template['enabled'] = 'true'
		bgp_template['localAS'] = kwargs['localAS']
		bgp_template['bgpNeighbours']['bgpNeighbour']['ipAddress'] = kwargs['remoteIP']
		bgp_template['bgpNeighbours']['bgpNeighbour']['remoteAS'] = kwargs['remoteAS']

		bgp_template.pop('redistribution')
		bgp_template['bgpNeighbours']['bgpNeighbour'].pop('bgpFilters')
		routingGlobal_template.pop('ipPrefixes')
		routingGlobal_template.pop('logging')

		self.session.view_body_dict(bgp_template)
		self.session.view_body_dict(routingGlobal_template)

		response = self.session.update('routingConfig', uri_parameters,
		 request_body_dict={'routing': {'bgp': bgp_template, 
		 'routingGlobalConfig': routingGlobal_template}})

		self.session.view_response(response)

	def redistribute(self, **kwargs):
		uri_parameters = {}
		uri_parameters = {'edgeId': kwargs['edgeId']}

		edge = Edge(self.session)
		edge_config = edge.read(self.edgeId)

		self.session.view_body_dict(edge_config)

		
		routing = edge_config['body']['edge']['features']['routing']
		self.session.view_body_dict(routing)

		routing['bgp']['redistribution']['enabled'] = 'true'
		routing['bgp']['redistribution']['rules'] = {'rule' : {'action': kwargs['action'],
		 'from' : {kwargs['frm'] : 'true'}, 'prefixName' : kwargs['prefix']}}
		
		self.session.view_body_dict(routing)

		response = self.session.update('routingConfig',uri_parameters=uri_parameters,request_body_dict={'routing' : routing})
		self.session.view_response(response)
