#AddDisk2VM.py
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


def get_args():
    """ Get arguments from CLI """

    parser = argparse.ArgumentParser(description='Add disk to existing VM')

    parser.add_argument('--disk-type',required=False,action='store',default='thin',choices=['thick', 'thin'],help='thick or thin')
    parser.add_argument('--disk-size',required=True,action='store',help='disk size, in GB, to add to the VM')
    parser.add_argument('-u', '--user', help='VC User', required=True)
    parser.add_argument('-p', '--passw', help='VC User Pass', required=False)
    parser.add_argument('-v', '--vm-name', required=True, help='Name of the VM')

    args = parser.parse_args()

    if not args.passw:
        args.passw = getpass.getpass(
            prompt='Enter password')

    return args


def add_disk(vm, si, disk_size, disk_type):
        spec = vim.vm.ConfigSpec()
        # get all disks on a VM, set unit_number to the next available
        for dev in vm.config.hardware.device:
            if hasattr(dev.backing, 'fileName'):
                unit_number = int(dev.unitNumber) + 1
                # unit_number 7 reserved for scsi controller
                if unit_number == 7:
                    unit_number += 1
                if unit_number >= 16:
                    print "ERROR: we don't support this many disks"
                    return
            if isinstance(dev, vim.vm.device.VirtualSCSIController):
                controller = dev
        # add disk here
        dev_changes = []
        new_disk_kb = int(disk_size) * 1024 * 1024
        disk_spec = vim.vm.device.VirtualDeviceSpec()
        disk_spec.fileOperation = "create"
        disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        disk_spec.device = vim.vm.device.VirtualDisk()
        disk_spec.device.backing = \
            vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
        if disk_type == 'thin':
            disk_spec.device.backing.thinProvisioned = True
        disk_spec.device.backing.diskMode = 'persistent'
        disk_spec.device.unitNumber = unit_number
        disk_spec.device.capacityInKB = new_disk_kb
        disk_spec.device.controllerKey = controller.key
        dev_changes.append(disk_spec)
        spec.deviceChange = dev_changes
        vm.ReconfigVM_Task(spec=spec)
        print "%sGB disk added to %s" % (disk_size, vm.config.name)


def main():
    args = get_args()

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
            add_disk(vm, si, args.disk_size, args.disk_type)
        else:
            print "ERROR: VM not found"

    except vmodl.MethodFault, e:
        print "ERROR: Caught vmodl fault: %s" % e.msg
        return 1

    except Exception, e:
        print "ERROR: Caught exception: %s" % str(e)
        return 1



if __name__ == "__main__":
    main()














