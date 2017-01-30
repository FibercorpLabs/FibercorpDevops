import argparse

from conf import *
from nsxramlclient.client import NsxClient
from ReadEdge import ReadEdge


def get_args():

    """ Get arguments from CLI """
    parser = argparse.ArgumentParser(description='Configure Edge Interfaces')
    parser.add_argument('-v','--vnic', help='vNIC index',type=int,required=True)
    parser.add_argument('-ip','--primaryIp', help='Primary IP',type=str,required=True)
    parser.add_argument('-pg','--portgroupId', help='Portgroup ID',type=str,required=True)
    parser.add_argument('-pgn','--portgroupName', help='Portgroup name',type=str,required=False)
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
	nsx_template = session.extract_resource_body_example('nsxEdge','update')
	session.view_body_dict(nsx_template)

`

	
	vnics = edge_config['body']['edge']['vnics']
	vnic = vnics['vnic'][args.vnic]
	nsx_template['edge']['id'] = edgeId
	nsx_template['vnics'][vni]


	
	vnic['addressGroups'] = {'addressGroup': {'primaryAddress' : args.primaryIp, 'subnetMask' : args.mask, 'subnetPrefixLength' : args.prefix}}
	vnic['isConnected'] = args.isConnected
	vnic['mtu'] = args.mtu
	vnic['name'] = args.name
	vnic['type'] = args.type
	vnic['portgroupId'] = args.portgroupId
	vnic['portgroupName'] = args.portgroupName
	session.view_body_dict(vnics)
	response = session.update('nsxEdge',uri_parameters={'edgeId' : edgeId}, request_body_dict={'edge' : { 'id' : edgeId , 'vnics' : {'vnic' : vnic}}})
	session.view_response(response)


def main():

	ConfigureEdgeInterface('edge-1368')
	
if __name__ == '__main__':
	exit(main())
