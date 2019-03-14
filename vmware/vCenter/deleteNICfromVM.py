#deleteNICfromVM.py

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

    parser = argparse.ArgumentParser(description='Delete nic from existing VM')
    parser.add_argument('--nic',required=False, help='Nic number to delete')
    parser.add_argument('-u', '--user', help='VC User', required=True)
    parser.add_argument('-p', '--passw', help='VC User Pass', required=False)
    parser.add_argument('-v', '--vm-name', required=True, help='Name of the VM')

    args = parser.parse_args()

    if not args.passw:
        args.passw = getpass.getpass(
            prompt='Enter password')

    return args


def del_nic(si, vm, nic_number):
    """ Deletes virtual NIC based on nic number
    :param si: Service Instance
    :param vm: Virtual Machine Object
    :param nic_number: Unit Number
    :return: True if success
    """
    nic_prefix_label = 'Network adapter '
    nic_label = nic_prefix_label + str(nic_number)
    virtual_nic_device = None
    for dev in vm.config.hardware.device:
        if isinstance(dev, vim.vm.device.VirtualEthernetCard)   \
                and dev.deviceInfo.label == nic_label:
            virtual_nic_device = dev

    if not virtual_nic_device:
        raise RuntimeError('Virtual {} could not be found.'.format(nic_label))

    virtual_nic_spec = vim.vm.device.VirtualDeviceSpec()
    virtual_nic_spec.operation = \
        vim.vm.device.VirtualDeviceSpec.Operation.remove
    virtual_nic_spec.device = virtual_nic_device

    spec = vim.vm.ConfigSpec()
    spec.deviceChange = [virtual_nic_spec]
    task = vm.ReconfigVM_Task(spec=spec)
    print task
    return True



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
            del_nic(si, vm, args.nic)
        else:
            print "ERROR: VM not found"



    except vmodl.MethodFault, e:
        print "Caught vmodl fault: %s" % e.msg
        return 1

    except Exception, e:
        print "Caught exception: %s" % str(e)
        return 1



if __name__ == "__main__":
    main()














