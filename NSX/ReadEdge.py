from conf import *
from nsxramlclient.client import NsxClient

def ReadEdge(edgeId):

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

	edge_config = session.read('nsxEdge',uri_parameters={'edgeId': edgeId})
	#session.view_body_dict(edge_config['body'])
	return edge_config


def main():

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)
	edge_config = ReadEdge('edge-1367')
	session.view_body_dict(edge_config['body'])	

if __name__ == '__main__':
	exit(main())

