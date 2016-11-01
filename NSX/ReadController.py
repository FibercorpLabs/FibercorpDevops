from conf import *
from nsxramlclient.client import NsxClient

session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

uri_parameters = {}
uri_parameters['controllerId'] = ''

edge_config = session.read('nsxControllers')
session.view_body_dict(edge_config['body'])
