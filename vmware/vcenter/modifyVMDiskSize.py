#modifyVMDiskSize.py

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



def modify_size(si, vm, size, unit):
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
            if disk_spec.device.unitNumber == unit:
                disk_spec.device.capacityInKB=size*1024*1024
                dev_changes.append(disk_spec)
    spec.deviceChange = dev_changes
    e = vm.ReconfigVM_Task(spec=spec)

    print e




def main():

    parser = argparse.ArgumentParser(description='Modify VM Resources')
    parser.add_argument('-u', '--user', help='VC User', required=True)
    parser.add_argument('-p', '--passw', help='VC User Pass', required=False)
    parser.add_argument('--size', type=long, help='New disk Size (Expanded) in GB', required=False)
    parser.add_argument('--unit', type=int, help='Disk Id to modify', required=False)
    parser.add_argument('-v', '--vm-name', required=True, help='Name of the VM')



    args = parser.parse_args()
    if not args.passw:
        args.passw = getpass.getpass(prompt='Enter password')

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
            if args.size:
                modify_size(si, vm, args.size, args.unit)
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


