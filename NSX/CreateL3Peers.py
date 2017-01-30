import ipaddress
import CreateEdge

from conf import *
from nsxramlclient.client import NsxClient

"""

 Variables

"""

N_OF_EDGES = 120
SUPERNET = '8.8.8.0/24'
MTU = '9000'

SUBNET_FLAG = 1
SUBNET_INDEX = 0
HOST_INDEX = 1

"""
 Supernetting and subnetting handling. Using the previous supernet defined at the beginning
 of the script, subnets it using some criteria (/30 for example) and adds to a list all
 those subnets for future use.

"""

supernet = ipaddress.ip_network(SUPERNET)
subnets_in_supernet = supernet.subnets(prefixlen_diff=6, new_prefix=None)

subnets = []
for snet in subnets_in_supernet:
	subnets.append(snet)

N_OF_HOSTS = ipaddress.ip_network(subnets[0]).num_addresses

for i in range(6,N_OF_EDGES+6):

	if HOST_INDEX > N_OF_HOSTS-2:
		SUBNET_INDEX += 1
		HOST_INDEX = 1

	network = ipaddress.ip_network(subnets[SUBNET_INDEX])
		
	ip = str(network[HOST_INDEX])

	CreateEdge.Create('admin',
		'F1b3rC*rp.2016!',
		'datacenter-2',
		'datastore-83',
		'resgroup-152',
		'host-82',
		'dvportgroup-166',
		ip,
		str(network.netmask),
		MTU,
		'0',
		'interface-edge-' + str(i),
		'Uplink',
		'compact',
		'gatewayServices',
		'NSX-EDGE-%s' % str(i))
	
	HOST_INDEX += 1