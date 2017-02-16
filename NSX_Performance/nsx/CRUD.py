from nsxramlclient.client import NsxClient


class Edge(object):
	def __init__(self, session):
		self.session = session

	def create(self,**kwargs):
		edge_template = self.session.extract_resource_body_example('nsxEdges', 'create')

		#session.view_body_dict(edge_template)

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
		                            'name': kwargs['edgeName']}})

		response = self.session.create('nsxEdges', request_body_dict=new_edge)
		self.session.view_response(response)
		return response

	def read(self,edgeId):
		edge_config = self.session.read('nsxEdge',uri_parameters={'edgeId': edgeId})
		
		return edge_config['body']

	def delete(self, edgeId):
		uri_parameters = {}
		uri_parameters['edgeId'] = edgeId

		response = self.session.delete('nsxEdge',uri_parameters)
		self.session.view_response(response)


#NSX Logical Switch

class LogicalSwitch(object):
	def __init__(self,session):
		self.session = session

	def create(self, **kwargs):
		vdn_scopes = self.session.read('vdnScopes','read')['body']

		vdn_scope_dict_list = [scope_dict[1] for scope_dict in vdn_scopes['vdnScopes'].items()]
		#session.view_body_dict(vdn_scope_dict_list)

		for scope in vdn_scope_dict_list:
			for tz in scope:
				if tz['name']  == kwargs['transportZone']:
					scopeId = tz['objectId']
					break
			if scopeId is not None:
				break

		lswitch_create_dict = self.session.extract_resource_body_example('logicalSwitches', 'create')
		self.session.view_body_dict(lswitch_create_dict)

		lswitch_create_dict['virtualWireCreateSpec']['controlPlaneMode'] = kwargs['controlPlaneMode']
		lswitch_create_dict['virtualWireCreateSpec']['description'] = kwargs['description']
		lswitch_create_dict['virtualWireCreateSpec']['name'] = kwargs['name']

		try:
			lswitch_create_dict['virtualWireCreateSpec']['tenantId'] = kwargs['tenantId']
		except NameError:
			pass

		response = self.session.create('logicalSwitches', uri_parameters={'scopeId': scopeId},
			request_body_dict=lswitch_create_dict)

		self.session.view_response(response)
		return response

	def read(self, virtualwireId):
		print virtualwireId

	def delete(self, virtualwireId):
		response = self.session.delete('logicalSwitch', uri_parameters={'virtualWireID': virtualWireId})
		self.session.view_response(response)

class controller(object):
	def __init__(self,session):
		self.session = session

	def read(controllerId):
		controller_config = self.session.read('nsxControllers',uri_parameters={'controllerId': controllerId})
		self.session.view_body_dict(controller_config['body'])



