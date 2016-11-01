from conf import *
from nsxramlclient.client import NsxClient

def GetVWiresId():

	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

	uri_parameters = {}
	uri_parameters = {'scopeId': 'vdnscope-1'}

	vwires = session.read('logicalSwitches',uri_parameters)
	#session.view_body_dict(vwires['body'])
	for i in range(len(vwires['body']['virtualWires']['dataPage']['virtualWire'])):
		vw = vwires['body']['virtualWires']['dataPage']['virtualWire'][i]
		print vw['name'] + " -- " + vw['objectId']

def main():
	GetVWiresId()
if __name__ == '__main__':
	exit(main())

