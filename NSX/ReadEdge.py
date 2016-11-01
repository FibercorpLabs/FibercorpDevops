from conf import *
from nsxramlclient.client import NsxClient

def ReadEdge(edgeId):

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

	uri_parameters = {}
	uri_parameters['edgeId'] = edgeId

	edge_config = session.read('nsxEdge',uri_parameters)
	session.view_body_dict(edge_config['body'])


def main():

	ReadEdge('edge-2')

if __name__ == '__main__':
	exit(main())

