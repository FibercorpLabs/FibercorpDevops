#CreateVMWPortGroup.py

from VMWConfigFile import *
from pyVim import connect
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
import atexit
import os
import sys
import ssl
import requests
import argparse
import time
import getpass


# Disabling urllib3 ssl warnings
requests.packages.urllib3.disable_warnings()
 
# Disabling SSL certificate verification
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.verify_mode = ssl.CERT_NONE


def get_obj(content, vimtype, name):
# """
#  Get the vsphere object associated with a given text name
# """
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj


def wait_for_task(task, actionName='job', hideResult=False):
    # """
    # Waits and provides updates on a vSphere task
    # """
    
    while task.info.state == vim.TaskInfo.State.running:
        time.sleep(2)
    
    if task.info.state == vim.TaskInfo.State.success:
        if task.info.result is not None and not hideResult:
            out = '%s completed successfully, result: %s' % (actionName, task.info.result)
            print(out)
        else:
            out = '%s completed successfully.' % actionName
            print(out)
    else:
        out = '%s did not complete successfully: %s' % (actionName, task.info.error)
        raise task.info.error
        print(out)
    
    return task.info.result



def add_dvPort_group(si, dv_switch, vlanId, name, bw):
    dv_pg_spec = vim.dvs.DistributedVirtualPortgroup.ConfigSpec()
    dv_pg_spec.name = name
    dv_pg_spec.numPorts = 32
    dv_pg_spec.type = vim.dvs.DistributedVirtualPortgroup.PortgroupType.earlyBinding
    policy = vim.dvs.DistributedVirtualPortgroup.PortgroupPolicy()
    policy.shapingOverrideAllowed = True
    dv_pg_spec.policy = policy

    dv_pg_spec.defaultPortConfig = vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy()
    dv_pg_spec.defaultPortConfig.securityPolicy = vim.dvs.VmwareDistributedVirtualSwitch.SecurityPolicy()

    if bw:
        inShapePolicy = vim.dvs.DistributedVirtualPort.TrafficShapingPolicy()
        inShapePolicy.enabled = vim.BoolPolicy(value=True)
        inShapePolicy.averageBandwidth = vim.LongPolicy(value=bw * 1000 * 1000)
        inShapePolicy.peakBandwidth = vim.LongPolicy(value=bw * 1000 * 1000)

        dv_pg_spec.defaultPortConfig.inShapingPolicy = inShapePolicy
        dv_pg_spec.defaultPortConfig.outShapingPolicy = inShapePolicy

    dv_pg_spec.defaultPortConfig.vlan = vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec()
    dv_pg_spec.defaultPortConfig.vlan.vlanId = vlanId
    dv_pg_spec.defaultPortConfig.securityPolicy.allowPromiscuous = vim.BoolPolicy(value=False)
    dv_pg_spec.defaultPortConfig.securityPolicy.forgedTransmits = vim.BoolPolicy(value=False)        

    dv_pg_spec.defaultPortConfig.vlan.inherited = False
    dv_pg_spec.defaultPortConfig.securityPolicy.macChanges = vim.BoolPolicy(value=False)
    dv_pg_spec.defaultPortConfig.securityPolicy.inherited = False

    task = dv_switch.AddDVPortgroup_Task([dv_pg_spec])
    wait_for_task(task, si)


def CreateVMWPortGroup(si, vlanId, name, bw, dvs):

        content = si.RetrieveContent()
        datacenter = get_obj(content, [vim.Datacenter], vc_settings["datacenter"])
        
        # get cluster //ToDo: Needed?
        # cluster = get_obj(content, [vim.ClusterComputeResource], vc_settings["cluster"])
        dv_switch = get_obj(content, [vim.DistributedVirtualSwitch], dvs)
        network_folder = datacenter.networkFolder

        #Add port group to this switch
        add_dvPort_group(si, dv_switch, int(vlanId), name, bw)

	return 0


# def main(*args, **kwargs):

# 	parser = argparse.ArgumentParser(description='Create VMW portgroup on DVS')
# 	parser.add_argument('-u', '--user', help='VC User', required=False)
# 	parser.add_argument('-p', '--passw', help='VC User Pass', required=False)
# 	# parser.add_argument('-d', '--dvs', help='DVS Name', required=False)

# 	args = parser.parse_args()

# 	if not args.user:
# 		args.user = raw_input('User: ')
# 	if not args.passw:
# 		args.passw = getpass.getpass(prompt='Password:')
# 	# if not args.dvs:
# 	#     args.dvs = raw_input('DVS: ')

# 	try:
# 		si = None
# 		try:
		
# 		# print "Trying to connect to VCENTER SERVER . . ."

# 		#si = Service Instance of vCenter
# 			si = connect.SmartConnect(host=vc_settings["vcenter"],
# 									user=args.user,
# 									pwd=args.passw,
# 									port=443,
# 									sslContext=context)
# 		except IOError, e:
# 			pass
# 			atexit.register(Disconnect, si)

# 		print "Connected to vCenter vSphere"

# 		vlanIdRange = [1031, 1051]

# 		for i in range(vlanIdRange[0], vlanIdRange[1]):
# 			exitCode = CreateVMWPortGroup(si, i, 'DCHornos-NW01-MPLS-VLAN%d' % i, None, 'vdSwitch-DCHornos-Networking-01')
# 			if exitCode == 0:
# 				print "--------- PORTGROUP %d --------- \n\n" % i
# 				print "Vlan-ID: %d" % i
# 				print "DVS: vdSwitch-DCHornos-Networking-01"
# 			else:
# 				break
# 			time.sleep(2)

# 	except vmodl.MethodFault, e:
# 		print "Caught vmodl fault: %s" % e.msg
# 		return 1

# 	except Exception, e:
# 		print "Caught exception: %s" % str(e)
# 		return 1


# if __name__ == '__main__':
#     exit(main())