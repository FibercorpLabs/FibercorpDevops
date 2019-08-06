from lib.vcenter import *
from pyVmomi import vim

def get_all_vms(si):
	vms = []

	content = si.RetrieveContent()

	for vm in get_vim_objects(content, vim.VirtualMachine):
		if not vm.config == None:
			if not vm.config.template:
				vms.append({'name' : vm.name, 'moId' : vm._moId})

	return vms
