import argparse

from conf import *
from nsxramlclient.client import NsxClient
from ReadEdge import ReadEdge


def get_args():

    """ Get arguments from CLI """
    parser = argparse.ArgumentParser(description='Configure Edge Interfaces')
    parser.add_argument('-v','--vnic', help='vNIC index',type=int,required=True)
    parser.add_argument('-ip','--primaryIp', help='Primary IP',type=str,required=True)
    parser.add_argument('-m','--mask', help='Network Mask',type=str,required=True)
    parser.add_argument('-p','--prefix', help='Network Prefix Length',type=str,required=True)
    parser.add_argument('-conn','--isConnected', help='Connect or not',type=str,required=True)
    parser.add_argument('-mt','--mtu', help='vNIC MTU',type=str,required=True)
    parser.add_argument('-n','--name', help='vNIC name',type=str,required=True)
    parser.add_argument('-t','--type', help='vNIC type (i.e. uplink, internal)',type=str,required=True)

    args = parser.parse_args()
    
    return args

def ConfigureEdgeInterface(edgeId):

	args = get_args()

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

	edge_config = ReadEdge(edgeId)
	vnic_config = edge_config['body']['edge']['vnics']

	vnic = None
	i = 0
	while vnic is None:
		if args.vnic == i:
			vnic = vnic_config['vnic'][i]
		i += 1

	vnic['addressGroups'] = {'addressGroup': {'primaryAddress' : args.primaryIp, 'subnetMask' : args.mask, 'subnetPrefixLength' : args.prefix}}
	vnic['isConnected'] = args.primaryIp
	vnic['mtu'] = args.mtu
	vnic['name'] = args.name
	vnic['type'] = args.type

	session.view_body_dict(vnic)

	
		
def main():

	ConfigureEdgeInterface('edge-1367')
	
if __name__ == '__main__':
	exit(main())