import argparse

from conf import *
from nsxramlclient.client import NsxClient
from CRUD import Edge


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

	#session.view_body_dict(edge_config['body'])
	#session.view_body_dict(nsx_template)

	vnics = nsx_template['edge']['vnics']
	

	vnics['vnic']['addressGroups'] = {'addressGroup': {'primaryAddress' : args.primaryIp, 'subnetMask' : args.mask, 'subnetPrefixLength' : args.prefix}}
	vnics['vnic']['isConnected'] = args.isConnected
	vnics['vnic']['mtu'] = args.mtu
	vnics['vnic']['name'] = args.name
	vnics['vnic']['type'] = args.type
	vnics['vnic']['portgroupId'] = args.portgroupId
	vnics['vnic']['portgroupName'] = args.portgroupName
	vnics['vnic']['index'] = args.vnic

	session.view_body_dict(vnics)
	response = session.update('vnic',uri_parameters={'edgeId' : edgeId, 'index' : str(args.vnic)}, request_body_dict=vnics)
	session.view_response(response)	


class interfaces(object):
	def __init__(self, session):
		self.session = session
		self.edge = Edge(self.session)

	def add_vnic(self, **kwargs):
		edge_config = self.edge.read(kwargs['edgeId'])
		nsx_template = self.session.extract_resource_body_example('nsxEdge', 'update')

		vnics = nsx_template['edge']['vnics']

		vnics['vnic']['addressGroups'] = {'addressGroup': {'primaryAddress' : kwargs['primaryIp'],
		 'subnetMask' : kwargs['mask'], 'subnetPrefixLength' : kwargs['prefix']}}
		vnics['vnic']['isConnected'] = kwargs['isConnected']
		vnics['vnic']['mtu'] = kwargs['mtu']
		vnics['vnic']['name'] = kwargs['name']
		vnics['vnic']['type'] = kwargs['type']
		vnics['vnic']['portgroupId'] = kwargs['portgroupId']

		try:
			vnics['vnic']['portgroupName'] = kwargs['portgroupName']
		except NameError:
			pass

		vnics['vnic']['index'] = kwargs['index']

		#self.session.view_body_dict(vnics)
		response = self.session.update('vnic',uri_parameters={'edgeId' : kwargs['edgeId'], 
			'index' : kwargs['index']}, request_body_dict=vnics)
		self.session.view_response(response)	