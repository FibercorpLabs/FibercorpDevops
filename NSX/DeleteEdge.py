from conf import *
from nsxramlclient.client import NsxClient

def DeleteEdge(edgeId):

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

	uri_parameters = {}
	uri_parameters['edgeId'] = edgeId

	delete_response = session.delete('nsxEdge',uri_parameters)
	session.view_response(delete_response)


def main():

	DeleteEdge('edge-25')
	DeleteEdge('edge-26')
	DeleteEdge('edge-27')
	DeleteEdge('edge-28')

if __name__ == '__main__':
	exit(main())