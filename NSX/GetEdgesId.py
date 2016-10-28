from conf import *
from nsxramlclient.client import NsxClient

def GetEdgesId():

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)
	edgesId = []
	edges_config = session.read('nsxEdges')
	#session.view_body_dict(edges_config['body'])
	for i in range(len(edges_config['body']['pagedEdgeList']['edgePage']['edgeSummary'])):
		r = edges_config['body']['pagedEdgeList']['edgePage']['edgeSummary'][i]
		#edgesId[i] = r['id']
		print r['id'] + " -- " + r['name']

def main():

	GetEdgesId()

if __name__ == '__main__':
	exit(main())