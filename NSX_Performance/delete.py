from nsx.conf import *
from nsx.objects import *
from nsxramlclient.client import NsxClient
from nsx.CRUD import Edge, LogicalSwitch
from vcenter.DestroyVm import Destroy_VM
from time import sleep



def main():

	#session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)
	#edge = Edge(session)
	#ls = LogicalSwitch(session)

	for i in range(11,61):
		Destroy_VM('VM_TENANT_%s_1' % i)
		sleep(15)
		Destroy_VM('VM_TENANT_%s_2' % i)
		sleep(15)

	#for i in range(1618,1624):
	#	edge.delete('edge-%s' % str(i))

	#for i in range(375,383):
	#	ls.delete('virtualwire-%s' % str(i))

if __name__ == '__main__':
	exit(main())