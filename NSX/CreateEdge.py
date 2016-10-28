from conf import *
from nsxramlclient.client import NsxClient

"""

 Variables

"""
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
	"""

	 Create session object to interact with NSX Manager

	"""
	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

	"""

	 Extract template as a dictonary to use for NSX Edge creation

	"""

	edge_template = session.extract_resource_body_example('nsxEdges', 'create')

	"""

	 Prints the template on the cli (Uncomment the line to view the dictonary)

	"""
	#session.view_body_dict(edge_template)

	"""

	 Copies some fields of the template in order to complete. The datastores, resource pools,
	 hosts Id can get retrieve them using GetAll*.py scripts. In addition, pops unused fields.

	 Also configure vnic parameters the same way as the other parameters.

	"""

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

	"""

	 Configure CLI credentials

	"""

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

	#session.view_body_dict(new_edge)
	create_response = session.create('nsxEdges', request_body_dict=new_edge)
	session.view_response(create_response)
	
def main():

	Create('admin',
		'admin',
		'datacenter-2',
		'datastore-10',
		'resgroup-33',
		'host-9',
		'dvportgroup-95',
		'5.4.3.1',
		'255.255.255.0',
		'9000',
		'0',
		'intprueba',
		'Uplink',
		'compact',
		'gatewayServices',
		'NOMBRE')

if __name__ == '__main__':
	exit(main())