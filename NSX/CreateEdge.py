from conf import *
from nsxramlclient.client import NsxClient

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
	
def main():

	Create('admin','F1b3rc0rp.2017','datacenter-2','datastore-2458',
		'resgroup-2473','host-2443','dvportgroup-2479','200.200.200.2',
		'255.255.255.252','9000','0','Uplink',
		'Uplink','large','gatewayServices','edge-002')

if __name__ == '__main__':
	exit(main())