from nsx.conf import *
from nsx.objects import *
from nsxramlclient.client import NsxClient
from nsx.CRUD import Edge, LogicalSwitch
from vcenter.CreateVMWVMfromTemplate import *
from paramiko import *
from time import sleep

def portgroupName(session, vw_name):
	search = getId(session)

	response = search.readVW(vw_name)

	session.view_body_dict(response)

	for i in range(0,len(response['virtualWire']['vdsContextWithBacking'])):
		if response['virtualWire']['vdsContextWithBacking'][i]['switch']['name'] == 'vdSwitch-SLO-HUB-01':
			index = i
			break

	dvs = response['virtualWire']['vdsContextWithBacking'][index]['switch']['objectId']
	sid = response['virtualWire']['vdnId']
	name = response['virtualWire']['name']

	pgname = 'vxw-%s-%s-sid-%s-%s' % (dvs, vw_name, sid, name)

	return pgname

def main():

  session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

  edge = Edge(session)
  ls = LogicalSwitch(session)
  
  N = 120							# Number of peers divided by two.
  host1 = 'host-2436'				# Host 1
  host2 = 'host-2443'				# Host 2

  for i in range(1,N/2+1):

  	# Create Logical Switches  	
  	response = ls.create(transportZone='SLO-HUB-01', controlPlaneMode='HYBRID_MODE',
  		description='VTEP-%s' % i, name='LS_UPLINK_%s' % i, tenantId='')
	virtualwireId = response['body']
	response = ls.create(transportZone='SLO-HUB-01', controlPlaneMode='HYBRID_MODE',
		description='Tenant1', name='LS_%s_1' % i, tenantId='')
	tenant_1_vw = response['body']
	response = ls.create(transportZone='SLO-HUB-01', controlPlaneMode='HYBRID_MODE',
		description='Tenant2', name='LS_2_%s' % i, tenantId='')
	tenant_2_vw = response['body']

	sleep(10)

	# Create NSX Edges
	response = edge.create(datastoreId='datastore-2458', hostId=host1, resourcePoolId='resgroup-2473',
		username='admin', password='F1b3rC*rp.2017', ip='10.10.10.1', netmask='255.255.255.252', index='0',
	  	mtu='9000', name='Uplink', type='Uplink', portgroupId=virtualwireId, applianceSize='large',
	  	datacenterId='datacenter-2', edgeType='gatewayServices', edgeName='EDGE_%s_1' % i)
	edgeId_h1 = response['objectId']

	sleep(30)

	response = edge.create(datastoreId='datastore-2458', hostId=host2, resourcePoolId='resgroup-2473',
	  	username='admin', password='F1b3rC*rp.2017', ip='10.10.10.2', netmask='255.255.255.252', index='0',
	 	mtu='9000', name='Uplink', type='Uplink', portgroupId=virtualwireId, applianceSize='large',
	 	datacenterId='datacenter-2', edgeType='gatewayServices', edgeName='EDGE_%s_2' % i)
	edgeId_h2 = response['objectId']

	sleep(30)

	# Disable Edge firewall
	edge.firewall(edgeId_h1)

	sleep(10)


	edge.firewall(edgeId_h2)

	sleep(30)	 
	
	edge.add_vnic(edgeId=edgeId_h1,primaryIp='192.168.0.1', mask='255.255.255.0',
	  	prefix='24', isConnected='True', mtu='9000', name='GW-Tenant-1', type='Internal',
	  	portgroupId=tenant_1_vw, portgroupName='', index='1')

	sleep(10)

	edge.add_vnic(edgeId=edgeId_h2, primaryIp='192.168.1.1', mask='255.255.255.0',
		prefix='24', isConnected='True', mtu='9000', name='GW-Tenant-2', type='Internal',
		portgroupId=tenant_2_vw, portgroupName='', index='1')

	sleep(30)

	# Configure BGP
	edge.bgp(edgeId=edgeId_h1, routerId='1.1.1.1', localAS='65431',
		remoteIP='10.10.10.2', remoteAS='65432')

	sleep(10)

	edge.bgp(edgeId=edgeId_h2, routerId='2.2.2.2', localAS='65432',
		remoteIP='10.10.10.1', remoteAS='65431')

	sleep(30)

	edge.redistribute(edgeId=edgeId_h1, action='permit', frm='bgp', prefix='')

	sleep(10)

	edge.redistribute(edgeId=edgeId_h2, action='permit', frm='bgp', prefix='')

	sleep(30)

	# Configure DHCP
	edge.dhcp(edgeId_h1, defaultGW='192.168.0.1', ipRange='192.168.0.2-192.168.0.250',
		subnetMask='255.255.255.0')

	sleep(10)

	edge.dhcp(edgeId_h2, defaultGW='192.168.1.1', ipRange='192.168.1.2-192.168.1.250',
		subnetMask='255.255.255.0')

	sleep(30)

	tenant1_pg = portgroupName(session, tenant_1_vw)
	tenant2_pg = portgroupName(session, tenant_2_vw)

	VMfromTemplate(vm_name='VM_TENANT_%s_1' % str(i), template_name='Ubuntu Xenial Xerus 16.04.1 LTS Server',
		user='administrator@vsphere.local', passw='F1b3rC*rp',cpus=1, mem=2, vm_folder='Tenants',
		datastore=None, resource_pool=None,	power_on=True, iops=100, disk=None,
		nic0=tenant1_pg, nic1=None, nic2=None)

	sleep(30)

	VMfromTemplate(vm_name='VM_TENANT_%s_2' % str(i), template_name='Ubuntu Xenial Xerus 16.04.1 LTS Server',
		user='administrator@vsphere.local', passw='F1b3rC*rp',cpus=1, mem=2, vm_folder='Tenants',
		datastore=None, resource_pool=None,	power_on=True, iops=100, disk=None,
		nic0=tenant2_pg, nic1=None, nic2=None)

if __name__ == '__main__':
	exit(main())
