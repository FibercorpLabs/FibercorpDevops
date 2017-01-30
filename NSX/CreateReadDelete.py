from conf import *
from nsxramlclient.client import NsxClient

#NSX Edge

def Create(username,
	password,
	datacenterId,
	datastoreId,
	resourcePoolId,
	hostId,
	portgroupId,
	ip,
	netmask,
	mtu,
	vnicIndex,
	vnicName,
	vnicType,
	applianceSize,
	edgeType,
	edgeName
	):

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

	edge_template = session.extract_resource_body_example('nsxEdges', 'create')

	#session.view_body_dict(edge_template)

	appliance_props = edge_template['edge']['appliances']['appliance'].copy()
	appliance_props['datastoreId'] = datastoreId
	appliance_props['resourcePoolId'] = resourcePoolId
	appliance_props['hostId'] = hostId

	appliance_props.pop('customField')
	appliance_props.pop('memoryReservation')
	appliance_props.pop('cpuReservation')

	vnic = edge_template['edge']['vnics']['vnic'].copy()

	vnic.pop('macAddress')
	vnic.pop('fenceParameter')
	vnic.pop('inShapingPolicy')
	vnic.pop('outShapingPolicy')
	
	cli_settings = edge_template['edge']['cliSettings'].copy()
	cli_settings['userName'] = username
	cli_settings['password'] = password

	vnic['addressGroups']['addressGroup']['primaryAddress'] = ip
	vnic['addressGroups']['addressGroup']['subnetMask'] = netmask
	vnic['index'] = vnicIndex
	vnic['mtu'] = mtu
	vnic['name'] = vnicName
	vnic['type'] = vnicType
	vnic['portgroupId'] = portgroupId
	vnic['isConnected'] = 'true'

	new_edge = {}
	new_edge.update({'edge': {'appliances': {'appliance': appliance_props,
	                            'applianceSize': applianceSize},
		                        'datacenterMoid': datacenterId,
	                            'vnics': {'vnic': vnic},
	                            'type': edgeType,
	                            'name': edgeName}})

	create_response = session.create('nsxEdges', request_body_dict=new_edge)
	session.view_response(create_response)

def ReadEdge(edgeId):

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

	edge_config = session.read('nsxEdge',uri_parameters={'edgeId': edgeId})
	#session.view_body_dict(edge_config['body'])
	return edge_config

def DeleteEdge(edgeId):

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

	uri_parameters = {}
	uri_parameters['edgeId'] = edgeId

	delete_response = session.delete('nsxEdge',uri_parameters)
	session.view_response(delete_response)


#NSX Logical Switch

def CreateLS(transportZone,
	controlPlaneMode,
	description,
	name,
	tenantId):

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=False)
	vdn_scopes = session.read('vdnScopes','read')['body']
	#session.view_body_dict(vdn_scopes)
	vdn_scope_dict_list = [scope_dict[1] for scope_dict in vdn_scopes['vdnScopes'].items()]
	#session.view_body_dict(vdn_scope_dict_list)

	for scope in vdn_scope_dict_list:
		for tz in scope:
			if tz['name']  == transportZone:
				scopeId = tz['objectId']
				break
		if scopeId is not None:
			break


	lswitch_create_dict = session.extract_resource_body_example('logicalSwitches', 'create')
	session.view_body_dict(lswitch_create_dict)

	lswitch_create_dict['virtualWireCreateSpec']['controlPlaneMode'] = controlPlaneMode
	lswitch_create_dict['virtualWireCreateSpec']['description'] = description
	lswitch_create_dict['virtualWireCreateSpec']['name'] = name
	lswitch_create_dict['virtualWireCreateSpec']['tenantId'] = tenantId

	new_ls = session.create('logicalSwitches', uri_parameters={'scopeId': scopeId},
		request_body_dict=lswitch_create_dict)
	session.view_response(new_ls)

def DeleteLSk(virtualWireId):

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=False)

	del_ls = session.delete('logicalSwitch', uri_parameters={'virtualWireID': virtualWireId})
	session.view_response(del_ls)

#NSX Controller

def ReadController(controllerId):
	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

	controller_config = session.read('nsxControllers',uri_parameters={'controllerId': controllerId})
	session.view_body_dict(controller_config['body'])