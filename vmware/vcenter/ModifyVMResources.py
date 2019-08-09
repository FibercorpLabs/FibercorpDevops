#ModifyVMResources.py

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
            print out
        else:
            out = '%s completed successfully.' % actionName
            print out
    else:
        out = '%s did not complete successfully: %s' % (actionName, task.info.error)
        raise task.info.error
        print out
    
    return task.info.result



def modify_iops(si, vm, iops):
    """
    :param si: Service Instance
    :param vm: Virtual Machine Object
    :param iops: IO to limit
    """
    spec = vim.vm.ConfigSpec()
    dev_changes = []

    for dev in vm.config.hardware.device:
        if isinstance(dev, vim.vm.device.VirtualDisk):
            disk_spec = vim.vm.device.VirtualDeviceSpec()
            disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
            disk_spec.device = dev
            disk_spec.device.storageIOAllocation.limit = iops
            dev_changes.append(disk_spec)
    spec.deviceChange = dev_changes
    e = vm.ReconfigVM_Task(spec=spec)

    print e



def modify_mem(si, vm, mem):
    """
    :param si: Service Instance
    :param vm: Virtual Machine Object
    :param mem: vMEM
    """
    spec = vim.vm.ConfigSpec()
    cpu_changes = []
    spec.memoryMB = int(mem) * 1024
    e = vm.ReconfigVM_Task(spec=spec)
    print e


def modify_cpu(si, vm, cpu):
    """
    :param si: Service Instance
    :param vm: Virtual Machine Object
    :param cpu: vCPU
    """
    spec = vim.vm.ConfigSpec()
    cpu_changes = []
    spec.numCPUs = int(cpu) # if you want 4 cpus
    print spec.numCPUs
    spec.numCoresPerSocket = int(cpu) / 2 # if you want dual-processor with dual-cores
    print spec.numCoresPerSocket 
    e = vm.ReconfigVM_Task(spec=spec)
    print e




def main():

    parser = argparse.ArgumentParser(description='Modify VM Resources')
    parser.add_argument('-u', '--user', help='VC User', required=True)
    parser.add_argument('-p', '--passw', help='VC User Pass', required=False)
    parser.add_argument('--iops', type=long, help='IOPS to add to Datastore', required=False)
    parser.add_argument('--cpu', help='vCPU to assign to VM', required=False)
    parser.add_argument('--mem', required=False, help='Mem to assign to VM')
    parser.add_argument('-v', '--vm-name', required=True, help='Name of the VM')



    args = parser.parse_args()
    if not args.passw:
        args.passw = getpass.getpass(prompt='Enter password')

    print "python ModifyVMResources.py -u aliguori@lab.fibercorp.com.ar -n ag-block1" 

    try:
        si = None
        try:
            
            #si = Service Instance of vCenter
            si = connect.SmartConnect(host=vc_settings["vcenter"],
                                      user=args.user,
                                      pwd=args.passw,
                                      port=443,
                                      sslContext=context)

        except IOError, e:
            pass
            atexit.register(Disconnect, si)

        content = si.RetrieveContent()
        vm = get_obj(content, [vim.VirtualMachine], args.vm_name)

        if vm:
            if args.cpu:
                modify_cpu(si, vm, args.cpu)
            if args.mem:
                modify_mem(si, vm, args.mem)
            if args.iops:
                modify_iops(si, vm, args.iops)
        else:
            print "ERROR: VM not found"
        

    except vmodl.MethodFault, e:
        print "ERROR: Caught vmodl fault: %s" % e.msg
        return 1

    except Exception, e:
        print "ERROR: Caught exception: %s" % str(e)
        return 1




# Start program
if __name__ == "__main__":
    main()


