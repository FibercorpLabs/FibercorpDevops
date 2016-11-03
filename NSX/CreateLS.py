from conf import *
from nsxramlclient.client import NsxClient

def Create(transportZone,
	controlPlaneMode,
	description,
	name,
	tenantId):

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=False)
	vdn_scopes = session.read('vdnScopes','read')['body']
	vdn_scope_dict_list = [scope_dict for scope_dict in vdn_scopes['vdnScopes'].items()]
	vdn_scope = [scope[1]['objectId'] for scope in vdn_scope_dict_list if scope[1]['name'] == transportZone][0]

	lswitch_create_dict = session.extract_resource_body_example('logicalSwitches', 'create')
	session.view_body_dict(lswitch_create_dict)

	lswitch_create_dict['virtualWireCreateSpec']['controlPlaneMode'] = controlPlaneMode
	lswitch_create_dict['virtualWireCreateSpec']['description'] = description
	lswitch_create_dict['virtualWireCreateSpec']['name'] = name
	lswitch_create_dict['virtualWireCreateSpec']['tenantId'] = tenantId

	new_ls = session.create('logicalSwitches', uri_parameters={'scopeId': vdn_scope},
		request_body_dict=lswitch_create_dict)
	session.view_response(new_ls)



def main():

	Create('HORNOS-HUB-01','HYBRID_MODE','Test','Test-LS','Tenant2')

if __name__ == '__main__':
	exit(main())
