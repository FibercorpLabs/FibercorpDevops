from conf import *
from nsxramlclient.client import NsxClient

def Delete(virtualWireId):

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=False)

	del_ls = session.delete('logicalSwitch', uri_parameters={'virtualWireID': virtualWireId})
	session.view_response(del_ls)

def main():

	Delete('virtualwire-4')

if __name__ == '__main__':
	exit(main())





