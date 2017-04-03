from nsxramlclient.client import NsxClient


class Edge(object):
	def __init__(self, session):
		self.session = session

	def create(self,**kwargs):
		edge_template = self.session.extract_resource_body_example('nsxEdges', 'create')

		appliance_props = edge_template['edge']['appliances']['appliance'].copy()
		appliance_props['datastoreId'] = kwargs['datastoreId']
		appliance_props['resourcePoolId'] = kwargs['resourcePoolId']
		appliance_props['hostId'] = kwargs['hostId']

		appliance_props.pop('customField')
		appliance_props.pop('memoryReservation')
		appliance_props.pop('cpuReservation')

		vnic = edge_template['edge']['vnics']['vnic'].copy()

		vnic.pop('macAddress')
		vnic.pop('fenceParameter')
		vnic.pop('inShapingPolicy')
		vnic.pop('outShapingPolicy')
		
		cli_settings = edge_template['edge']['cliSettings'].copy()
		cli_settings['userName'] = kwargs['username']
		cli_settings['password'] = kwargs['password']

		vnic['addressGroups']['addressGroup']['primaryAddress'] = kwargs['ip']
		vnic['addressGroups']['addressGroup']['subnetMask'] = kwargs['netmask']
		vnic['index'] = kwargs['index']
		vnic['mtu'] = kwargs['mtu']
		vnic['name'] = kwargs['name']
		vnic['type'] = kwargs['type']
		vnic['portgroupId'] = kwargs['portgroupId'] #or virtualwireId
		vnic['isConnected'] = 'true'

		new_edge = {}
		new_edge.update({'edge': {'appliances': {'appliance': appliance_props,
		                            'applianceSize': kwargs['applianceSize']},
			                        'datacenterMoid': kwargs['datacenterId'],
		                            'vnics': {'vnic': vnic},
		                            'type': kwargs['edgeType'],
		                            'name': kwargs['edgeName'],
		                            'cliSettings' : cli_settings}})

		response = self.session.create('nsxEdges', request_body_dict=new_edge)
		
		return response

	def read(self,edgeId):
		edge_config = self.session.read('nsxEdge',uri_parameters={'edgeId': edgeId})
		
		return edge_config['body']

	def add_vnic(self, **kwargs):
		edge_config = self.edge.read(kwargs['edgeId'])
		nsx_template = self.session.extract_resource_body_example('nsxEdge', 'update')

		vnics = nsx_template['edge']['vnics']

		vnics['vnic']['addressGroups'] = {'addressGroup': {'primaryAddress' : kwargs['primaryIp'],
		 'subnetMask' : kwargs['mask'], 'subnetPrefixLength' : kwargs['prefix']}}
		vnics['vnic']['isConnected'] = kwargs['isConnected']
		vnics['vnic']['mtu'] = kwargs['mtu']
		vnics['vnic']['name'] = kwargs['name']
		vnics['vnic']['type'] = kwargs['type']
		vnics['vnic']['portgroupId'] = kwargs['portgroupId']

		try:
			vnics['vnic']['portgroupName'] = kwargs['portgroupName']
		except NameError:
			pass

		vnics['vnic']['index'] = kwargs['index']

		response = self.session.update('vnic',uri_parameters={'edgeId' : kwargs['edgeId'], 
			'index' : kwargs['index']}, request_body_dict=vnics)
		
	def add_vnic(self, **kwargs):
		edge = Edge(self.session)
		edge_config = edge.read(kwargs['edgeId'])
		nsx_template = self.session.extract_resource_body_example('nsxEdge', 'update')

		vnics = nsx_template['edge']['vnics']

		vnics['vnic']['addressGroups'] = {'addressGroup': {'primaryAddress' : kwargs['primaryIp'],
		 'subnetMask' : kwargs['mask'], 'subnetPrefixLength' : kwargs['prefix']}}
		vnics['vnic']['isConnected'] = kwargs['isConnected']
		vnics['vnic']['mtu'] = kwargs['mtu']
		vnics['vnic']['name'] = kwargs['name']
		vnics['vnic']['type'] = kwargs['type']
		vnics['vnic']['portgroupId'] = kwargs['portgroupId']

		try:
			vnics['vnic']['portgroupName'] = kwargs['portgroupName']
		except NameError:
			pass

		vnics['vnic']['index'] = kwargs['index']

		response = self.session.update('vnic',uri_parameters={'edgeId' : kwargs['edgeId'], 
			'index' : kwargs['index']}, request_body_dict=vnics)
		
	def firewall(self, edgeId, **kwargs):
		uri_parameters = {}
		uri_parameters = {'edgeId': edgeId}

		firewall_template = self.session.extract_resource_body_example('nsxEdgeFirewallConfig',
		 'update')
		
		response = self.session.update('nsxEdgeFirewallConfig', uri_parameters,
		 request_body_dict={'firewall' : {'enabled' : 'false'}})
		
	def dhcp(self, edgeId, **kwargs):
		uri_parameters = {}
		uri_parameters = {'edgeId': edgeId}

		dhcp_template = self.session.extract_resource_body_example('dhcp',
				'update')
		
		dhcp_template['dhcp']['enabled'] = 'True'
		dhcp_template['dhcp']['ipPools']['ipPool'] = {'defaultGateway' : kwargs['defaultGW'],
		'ipRange' : kwargs['ipRange'], 'subnetMask' : kwargs['subnetMask']}
		dhcp_template['dhcp'].pop('staticBindings')
		
		response = self.session.update('dhcp', uri_parameters,
		 request_body_dict=dhcp_template)
		
	def bgp(self, **kwargs):
		uri_parameters = {}
		uri_parameters = {'edgeId': kwargs['edgeId']}

		routing_template = self.session.extract_resource_body_example('routingConfig',
			'update')
		
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

		response = self.session.update('routingConfig', uri_parameters,
		 request_body_dict={'routing': {'bgp': bgp_template, 
		 'routingGlobalConfig': routingGlobal_template}})

	def redistribute(self, **kwargs):
		uri_parameters = {}
		uri_parameters = {'edgeId': kwargs['edgeId']}

		edge = Edge(self.session)
		edge_config = edge.read(kwargs['edgeId'])

		routing = edge_config['edge']['features']['routing']
		
		routing['bgp']['redistribution']['enabled'] = 'true'
		routing['bgp']['redistribution']['rules'] = {'rule' : {'action': kwargs['action'],
		 'from' : {'bgp' : 'true', 'static' : 'true', 'connected' : 'true'}}}#, 'prefixName' : kwargs['prefix']}}
		
		response = self.session.update('routingConfig',uri_parameters=uri_parameters,request_body_dict={'routing' : routing})
		

	def delete(self, edgeId):
		uri_parameters = {}
		uri_parameters['edgeId'] = edgeId

		response = self.session.delete('nsxEdge',uri_parameters)
		
#NSX Logical Switch

class LogicalSwitch(object):
	def __init__(self,session):
		self.session = session

	def create(self, **kwargs):
		vdn_scopes = self.session.read('vdnScopes','read')['body']

		vdn_scope_dict_list = [scope_dict[1] for scope_dict in vdn_scopes['vdnScopes'].items()]
		
		for scope in vdn_scope_dict_list:
			for tz in scope:
				if tz['name']  == kwargs['transportZone']:
					scopeId = tz['objectId']
					break
			if scopeId is not None:
				break

		lswitch_create_dict = self.session.extract_resource_body_example('logicalSwitches', 'create')
		
		lswitch_create_dict['virtualWireCreateSpec']['controlPlaneMode'] = kwargs['controlPlaneMode']
		lswitch_create_dict['virtualWireCreateSpec']['description'] = kwargs['description']
		lswitch_create_dict['virtualWireCreateSpec']['name'] = kwargs['name']

		try:
			lswitch_create_dict['virtualWireCreateSpec']['tenantId'] = kwargs['tenantId']
		except NameError:
			pass

		response = self.session.create('logicalSwitches', uri_parameters={'scopeId': scopeId},
			request_body_dict=lswitch_create_dict)

		return response

	def read(self, virtualwireId):
		print virtualwireId

	def delete(self, virtualwireId):
		response = self.session.delete('logicalSwitch', uri_parameters={'virtualWireID': virtualwireId})
		

class controller(object):
	def __init__(self,session):
		self.session = session

	def read(controllerId):
		controller_config = self.session.read('nsxControllers',uri_parameters={'controllerId': controllerId})
		self.session.view_body_dict(controller_config['body'])



