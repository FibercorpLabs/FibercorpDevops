from conf import *
from nsxramlclient.client import NsxClient
from nsx.CRUD import Edge, LogicalSwitch

def main():

  session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)
  edge = Edge(session)

  edge.create(datasourceId='datastore-2458', hostId='host-2436', resourcePoolId='resgroup-152',
  	username='admin', password='F1b3rC*rp.2017', ip='10.10.10.1', netmask='255.255.255.252', index='0',
  	mtu='9000', name='Uplink', type='Uplink', portgroupId='', applianceSize='large',
  	datacenterId='datacenter-', edgeType='gatewayServices', edgeName='Edge001')

if __name__ = '__main__':
	exit(main())