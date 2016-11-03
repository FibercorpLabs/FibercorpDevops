from conf import *
from nsxramlclient.client import NsxClient

def ReadController(controllerId):
	session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

	controller_config = session.read('nsxControllers',uri_parameters={'controllerId': controllerId})
	session.view_body_dict(controller_config['body'])

def main():

	ReadController('')

if __name__ == '__main__':
	exit(main())