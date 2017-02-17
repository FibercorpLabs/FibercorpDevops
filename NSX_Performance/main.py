from nsx.conf import *
from nsxramlclient.client import NsxClient
from nsx.CRUD import Edge, LogicalSwitch
from nsx.interfaces import interfaces
from nsx.BGP import bgp

def main():

  session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

  edge = Edge(session)
  ls = LogicalSwitch(session)
  interface = interfaces(session)
  #bgp_ins = bgp(session)

  N = 1								# Number of peers divided by two.
  host1 = 'host-2436'				# Host 1
  host2 = 'host-2443'				# Host 2

  for i in range(0,N):

  	# Create LS and Edge  	
  	response = ls.create(transportZone='SLO-HUB-01', controlPlaneMode='HYBRID_MODE',
	   description='VTEP-%s' % i, name='LS-%s' % i, tenantId='')
	virtualwireId = response['body']

	response = edge.create(datastoreId='datastore-2458', hostId=host1, resourcePoolId='resgroup-2473',
		username='admin', password='F1b3rC*rp.2017', ip='10.10.10.1', netmask='255.255.255.252', index='0',
	  	mtu='9000', name='Uplink', type='Uplink', portgroupId=virtualwireId, applianceSize='large',
	  	datacenterId='datacenter-2', edgeType='gatewayServices', edgeName='EdgeH1-%s' % i)
	edgeId_h1 = response['objectId']

	# Disable Edge firewall
	edge.firewall(edgeId_h1)

	# Create LS and Edge	 
	response = ls.create(transportZone='SLO-HUB-01', controlPlaneMode='HYBRID_MODE',
	   description='Tenant1', name='LS-Tenant1-%s' % i, tenantId='')
	tenant_1_vw = response['body']

	edge.add_vnic(edgeId=edgeId_h1,primaryIp='192.168.0.1', mask='255.255.255.0',
	  	prefix='24', isConnected='True', mtu='9000', name='GW-Tenant-1', type='Internal',
	  	portgroupId=tenant_1_vw, portgroupName='', index='1')
	 
	response = edge.create(datastoreId='datastore-2458', hostId=host2, resourcePoolId='resgroup-2473',
	  	username='admin', password='F1b3rC*rp.2017', ip='10.10.10.2', netmask='255.255.255.252', index='0',
	 	mtu='9000', name='Uplink', type='Uplink', portgroupId=virtualwireId, applianceSize='large',
	 	datacenterId='datacenter-2', edgeType='gatewayServices', edgeName='EdgeH2-%s' % i)
	edgeId_h2 = response['objectId']

	# Disable Edge firewall
	edge.firewall(edgeId_h2)

	response = ls.create(transportZone='SLO-HUB-01', controlPlaneMode='HYBRID_MODE',
		description='Tenant2', name='LS-Tenant2-%s' % i, tenantId='')
	tenant_2_vw = response['body']

	edge.add_vnic(edgeId=edgeId_h2, primaryIp='192.168.1.1', mask='255.255.255.0',
		prefix='24', isConnected='True', mtu='9000', name='GW-Tenant-2', type='Internal',
		portgroupId=tenant_2_vw, portgroupName='', index='1')

	# Configure BGP
	edge.bgp(edgeId=edgeId_h1, routerId='1.1.1.1', localAS='65431',
		remoteIP='10.10.10.2', remoteAS='65432')
	edge.bgp(edgeId=edgeId_h2, routerId='2.2.2.2', localAS='65432',
		remoteIP='10.10.10.1', remoteAS='65431')

	edge.redistribute(edgeId=edgeId_h1, action='permit', frm='bgp', prefix='')
	edge.redistribute(edgeId=edgeId_h2, action='permit', frm='bgp', prefix='')

	# Configure DHCP
	edge.dhcp(edgeId_h1, defaultGW='192.168.0.1', ipRange='192.168.0.2-192.168.0.250',
		subnetMask='255.255.255.0')
	edge.dhcp(edgeId_h2, defaultGW='192.168.1.1', ipRange='192.168.1.2-192.168.1.250',
		subnetMask='255.255.255.0')

if __name__ == '__main__':
	exit(main())
