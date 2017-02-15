from nsx.conf import *
from nsxramlclient.client import NsxClient
from nsx.CRUD import Edge, LogicalSwitch

def main():

  session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)
  edge = Edge(session)

  edge.create(datastoreId='datastore-2458', hostId='host-2436', resourcePoolId='resgroup-2473',
  	username='admin', password='F1b3rC*rp.2017', ip='10.10.10.1', netmask='255.255.255.252', index='0',
  	mtu='9000', name='Uplink', type='Uplink', portgroupId='dvportgroup-2479', applianceSize='large',
  	datacenterId='datacenter-2', edgeType='gatewayServices', edgeName='Edge001')

if __name__ == '__main__':
	exit(main())
