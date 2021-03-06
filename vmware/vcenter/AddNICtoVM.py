#AddNICtoVM.py

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
    parser.add_argument('--portgroup',required=True,help='Portgroup')
    parser.add_argument('-u', '--user', help='VC User', required=True)
    parser.add_argument('-p', '--passw', help='VC User Pass', required=False)
    parser.add_argument('-v', '--vm-name', required=True, help='Name of the VM')

    args = parser.parse_args()

    if not args.passw:
        args.passw = getpass.getpass(
            prompt='Enter password')

    return args



def add_nic(si, vm, network):
    """
    :param si: Service Instance
    :param vm: Virtual Machine Object
    :param network: Virtual Network
    """

    spec = vim.vm.ConfigSpec()
    nic_changes = []

    nic = vim.vm.device.VirtualDeviceSpec()
    nic.operation = vim.vm.device.VirtualDeviceSpec.Operation.add  # or edit if a device exists
    nic.device = vim.vm.device.VirtualVmxnet3()
    nic.device.wakeOnLanEnabled = True
    nic.device.addressType = 'assigned'
    nic.device.key = 4000  # 4000 seems to be the value to use for a vmxnet3 device
    nic.device.deviceInfo = vim.Description()
    nic.device.deviceInfo.summary = "added nic"

    content = si.RetrieveContent()
    pg_obj = get_obj(content, [vim.dvs.DistributedVirtualPortgroup], network)
    dvs_port_connection = vim.dvs.PortConnection()
    dvs_port_connection.portgroupKey= pg_obj.key
    dvs_port_connection.switchUuid= pg_obj.config.distributedVirtualSwitch.uuid

    nic.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
    nic.device.backing.port = dvs_port_connection

    nic.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    nic.device.connectable.startConnected = True
    nic.device.connectable.allowGuestControl = True
    nic.device.connectable.connected = False
    nic.device.connectable.status = 'untried'
    nic.device.wakeOnLanEnabled = True
    nic.device.addressType = 'assigned'

    nic_changes.append(nic)
    spec.deviceChange = nic_changes
    e = vm.ReconfigVM_Task(spec=spec)
    print e





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
            add_nic(si, vm, args.portgroup)
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














