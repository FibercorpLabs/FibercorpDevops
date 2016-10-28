from conf import *
from nsxramlclient.client import NsxClient

TRANSPORT_ZONE = 'HORNOS-HUB-01'


client_session = NsxClient(nsxraml_file, nsxmanager, nsx_username,
	nsx_password, debug=False)

####
# FIND objectId of the Scope with the name of the TZ
####
vdn_scopes = client_session.read('vdnScopes','read')['body']
vdn_scope_dict_list = [scope_dict for scope_dict in vdn_scopes['vdnScopes'].items()]
vdn_scope = [scope[1]['objectId'] for scope in vdn_scope_dict_list if scope[1]['name'] == TRANSPORT_ZONE][0]

####
# GET template dict to create LS
####

lswitch_create_dict = client_session.extract_resource_body_example('logicalSwitches', 'create')
client_session.view_body_dict(lswitch_create_dict)

####
# PASS LS parameters
####

lswitch_create_dict['virtualWireCreateSpec']['controlPlaneMode'] = 'HYBRID_MODE'
lswitch_create_dict['virtualWireCreateSpec']['description'] = 'Testing'
lswitch_create_dict['virtualWireCreateSpec']['name'] = 'TEST-LS1'
lswitch_create_dict['virtualWireCreateSpec']['tenantId'] = 'Tenant1'

####
# CREATE logical switch
####

new_ls = client_session.create('logicalSwitches', uri_parameters={'scopeId': vdn_scope},
	request_body_dict=lswitch_create_dict)
client_session.view_response(new_ls)

