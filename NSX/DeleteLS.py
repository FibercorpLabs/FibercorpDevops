from conf import *
from nsxramlclient.client import NsxClient

def Delete(virtualWireId):

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=False)
	
	del_ls = session.delete('logicalSwitch', uri_parameters={'virtualWireId': virtualWireId},
		request_body_dict=lswitch_create_dict)
	session.view_response(del_ls)

def main():

	Delete('virtualwire-2')
	
if __name__ == '__name__':
	exit(main())



