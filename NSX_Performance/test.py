from conf import *
from nsxramlclient.client import NsxClient
from nsx.CRUD import Edge, LogicalSwitch

def main():

  session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)
  edge = Edge(session)

  edge.create(datasourceId='', hostId='', resourcePoolId='',
  	username='', password='', ip='', netmask='', index='',
  	mtu='', name='', type='', portgroupId='', applianceSize='',
  	datacenterId='', edgeType='', edgeName='')
  
if __name__ = '__main__':
	exit(main())