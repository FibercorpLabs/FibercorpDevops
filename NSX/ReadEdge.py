from conf import *
from nsxramlclient.client import NsxClient

#def GetEdgesId():

session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

uri_parameters = {}
uri_parameters['edgeId'] = 'edge-23'

edge_config = session.read('nsxEdge',uri_parameters)
session.view_body_dict(edge_config['body'])
