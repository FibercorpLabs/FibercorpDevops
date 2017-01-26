from conf import *
from nsxramlclient.client import NsxClient

def Create(transportZone,
	controlPlaneMode,
	description,
	name,
	tenantId):

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=False)
	vdn_scopes = session.read('vdnScopes','read')['body']
	#session.view_body_dict(vdn_scopes)
	vdn_scope_dict_list = [scope_dict[1] for scope_dict in vdn_scopes['vdnScopes'].items()]
	#session.view_body_dict(vdn_scope_dict_list)

	for scope in vdn_scope_dict_list:
		for tz in scope:
			if tz['name']  == transportZone:
				scopeId = tz['objectId']
				break
		if scopeId is not None:
			break


	lswitch_create_dict = session.extract_resource_body_example('logicalSwitches', 'create')
	session.view_body_dict(lswitch_create_dict)

	lswitch_create_dict['virtualWireCreateSpec']['controlPlaneMode'] = controlPlaneMode
	lswitch_create_dict['virtualWireCreateSpec']['description'] = description
	lswitch_create_dict['virtualWireCreateSpec']['name'] = name
	lswitch_create_dict['virtualWireCreateSpec']['tenantId'] = tenantId

	new_ls = session.create('logicalSwitches', uri_parameters={'scopeId': scopeId},
		request_body_dict=lswitch_create_dict)
	session.view_response(new_ls)



def main():

	Create('SLO-HUB-01','HYBRID_MODE','Tenant-1','Tenant-1','TENANT_ID')
	Create('SLO-HUB-01','HYBRID_MODE','Tenant-2','Tenant-2','TENANT_ID')

if __name__ == '__main__':
	exit(main())
