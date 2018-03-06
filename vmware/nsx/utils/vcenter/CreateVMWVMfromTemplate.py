#CreateVMWVMfromTemplate.py

from VMWConfigFile import *
from pyVim import connect
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
import atexit
import os
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



def find_disk(vm,index):
    """Return the disk of the given index in the vm"""
    i=0
    for device in vm.config.hardware.device:
        if hasattr(device.backing,"fileName"):
            if i==index:
                return device
            else:
                i +=1

def disk_controller(vm):
    """Return the first disk controller for the given vm"""
    for device in vm.config.hardware.device:
        if isinstance(device,vim.vm.device.VirtualSCSIController):
            return device



def get_vim_objects(content, vim_type):
    '''Get vim objects of a given type.'''
    return [item for item in content.viewManager.CreateContainerView(
        content.rootFolder, [vim_type], recursive=True
    ).view]



def get_args():
    """ Get arguments from CLI """
    parser = argparse.ArgumentParser(description='Create VMW VM from template')
    parser.add_argument('-u', '--user', help='VC User', required=True)
    parser.add_argument('-p', '--passw', help='VC User Pass', required=False)
    parser.add_argument('-v', '--vm-name', required=True, help='Name of the VM')
    parser.add_argument('-t','--template', required=True, help='Name of the template')
    parser.add_argument('-f','--vm-folder', required=False, default=None, help='Name of the VMFolder')    
    parser.add_argument('-d','--datastore', required=False, default=None, help='Datastore you wish the VM to end up on\
    					If left blank, VM will be put on the same \
    					datastore as the template')

    parser.add_argument('-r','--resource-pool', required=False, default=None, help='Resource Pool to use. If left blank the first\
    					resource pool found will be used')

    parser.add_argument('--power-on', dest='power_on', required=False, action='store_true', help='power on the VM after creation')
    parser.add_argument('--no-power-on', dest='power_on', required=False, action='store_false', help='do not power on the VM after creation')
    parser.add_argument('-c', '--cpus', type=int, help='Number of CPUs, default:  1 vCPU', default=1)
    parser.add_argument('-m', '--mem', type=int, help='Memory in GB, default: 2 Gb', default=2)
    parser.add_argument('--nic0', help='NIC0 portgroup to use', required=False, nargs='?')
    parser.add_argument('--nic1', help='NIC1 portgroup to use', required=False, nargs='?')
    parser.add_argument('--nic2', help='NIC2 portgroup to use', required=False, nargs='?')
    parser.add_argument('--iops', type=int, help='IOPS limit to use, by default 100 is used', required=False, default=100)
    parser.add_argument('--disk', type=int, help='Disk size to use, by default the template size is used', required=False)


    args = parser.parse_args()

    if not args.passw:
        args.passw = getpass.getpass(
            prompt='Enter password')

    return args


def wait_for_task(task):
    """ wait for a vCenter task to finish """
    task_done = False
    while not task_done:
        if task.info.state == 'success':
            print("ok")
            return task.info.result

        if task.info.state == 'error':
            print("error")
            task_done = True


def get_obj(content, vimtype, name):
    """
    Return an object by name, if name is None the
    first found object is returned
    """
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if name:
            if c.name == name:
                obj = c
                break
        else:
            obj = c
            break

    return obj


def clone_vm(
        content, template, vm_name, si,
        datacenter_name, vm_folder, datastore,
        cluster_name, resource_pool, power_on, nic0, nic1, nic2, 
        cpus, mem, iops, disk_size ):
    """
    Clone a VM from a template/VM, datacenter_name, vm_folder, datastore
    cluster_name, resource_pool, and power_on are all optional.
    """

    # if none git the first one
    datacenter = get_obj(content, [vim.Datacenter], datacenter_name)

    if vm_folder:
        destfolder = get_obj(content, [vim.Folder], vm_folder)
    else:
        destfolder = datacenter.vmFolder

    if datastore:
        datastore = get_obj(content, [vim.Datastore], datastore)
    else:
        datastore = get_obj(
            content, [vim.Datastore], template.datastore[0].info.name)

    # if None, get the first one
    cluster = get_obj(content, [vim.ClusterComputeResource], cluster_name)

    if resource_pool:
        resource_pool = get_obj(content, [vim.ResourcePool], resource_pool)
    else:
        resource_pool = cluster.resourcePool

    # set relospec
    relospec = vim.vm.RelocateSpec()
    relospec.datastore = datastore
    relospec.pool = resource_pool

    devices = []

    if nic0:
        # VM device
        nic = vim.vm.device.VirtualDeviceSpec()
        nic.operation = vim.vm.device.VirtualDeviceSpec.Operation.add  # or edit if a device exists
        nic.device = vim.vm.device.VirtualVmxnet3()
        nic.device.wakeOnLanEnabled = True
        nic.device.addressType = 'assigned'
        nic.device.key = 4000  # 4000 seems to be the value to use for a vmxnet3 device
        nic.device.deviceInfo = vim.Description()
        nic.device.deviceInfo.summary = nic0
        nic.device.deviceInfo.label = "Network Adapter 1"

        pg_obj = get_obj(content, [vim.dvs.DistributedVirtualPortgroup], nic0)
        dvs_port_connection = vim.dvs.PortConnection()
        dvs_port_connection.portgroupKey= pg_obj.key
        dvs_port_connection.switchUuid= pg_obj.config.distributedVirtualSwitch.uuid

        nic.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
        nic.device.backing.port = dvs_port_connection

        nic.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        nic.device.connectable.startConnected = True
        nic.device.connectable.allowGuestControl = True
        devices.append(nic)

    if nic1:
        # VM device
        nic = vim.vm.device.VirtualDeviceSpec()
        nic.operation = vim.vm.device.VirtualDeviceSpec.Operation.add  # or edit if a device exists
        nic.device = vim.vm.device.VirtualVmxnet3()
        nic.device.wakeOnLanEnabled = True
        nic.device.addressType = 'assigned'
        nic.device.key = 4000  # 4000 seems to be the value to use for a vmxnet3 device
        nic.device.deviceInfo = vim.Description()
        nic.device.deviceInfo.summary = nic1
        nic.device.deviceInfo.label = "Network Adapter 2"

        pg_obj = get_obj(content, [vim.dvs.DistributedVirtualPortgroup], nic1)
        dvs_port_connection = vim.dvs.PortConnection()
        dvs_port_connection.portgroupKey= pg_obj.key
        dvs_port_connection.switchUuid= pg_obj.config.distributedVirtualSwitch.uuid

        nic.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
        nic.device.backing.port = dvs_port_connection

        nic.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        nic.device.connectable.startConnected = True
        nic.device.connectable.allowGuestControl = True
        devices.append(nic)

    if nic2:
        # VM device
        nic = vim.vm.device.VirtualDeviceSpec()
        nic.operation = vim.vm.device.VirtualDeviceSpec.Operation.add  # or edit if a device exists
        nic.device = vim.vm.device.VirtualVmxnet3()
        nic.device.wakeOnLanEnabled = True
        nic.device.addressType = 'assigned'
        nic.device.key = 4000  # 4000 seems to be the value to use for a vmxnet3 device
        nic.device.deviceInfo = vim.Description()
        nic.device.deviceInfo.summary = nic2
        nic.device.deviceInfo.label = "Network Adapter 3"

        pg_obj = get_obj(content, [vim.dvs.DistributedVirtualPortgroup], nic2)
        dvs_port_connection = vim.dvs.PortConnection()
        dvs_port_connection.portgroupKey= pg_obj.key
        dvs_port_connection.switchUuid= pg_obj.config.distributedVirtualSwitch.uuid

        nic.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
        nic.device.backing.port = dvs_port_connection

        nic.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        nic.device.connectable.startConnected = True
        nic.device.connectable.allowGuestControl = True
        devices.append(nic)


    disk=find_disk(template,0)
    controller=disk_controller(template)
    disk_spec=vim.vm.device.VirtualDeviceSpec()
    disk_spec.operation=vim.vm.device.VirtualDeviceSpec.Operation.edit
    disk_spec.device=disk
    disk_spec.device.controllerKey=controller.key
    if disk_size > 50:
        disk_spec.device.capacityInKB=disk_size*1024*1024
    #disk_spec.device.backing.thinProvisioned=True
    disk_spec.device.storageIOAllocation.limit = iops
    devices.append(disk_spec)


     # VM config spec
    vmconf = vim.vm.ConfigSpec()
    vmconf.numCPUs = cpus
    vmconf.memoryMB = mem * 1024
    vmconf.cpuHotAddEnabled = True
    vmconf.memoryHotAddEnabled = True
    vmconf.deviceChange = devices

    clonespec = vim.vm.CloneSpec()

    clonespec.location = relospec
    clonespec.config = vmconf
    clonespec.powerOn = power_on


    #print "cloning VM..."
    task = template.Clone(folder=destfolder, name=vm_name, spec=clonespec)
    #wait_for_task(task)
    print(task.info.key)

def VMfromTemplate(**kwargs):
    try:
        si = None
        try:
            #si = Service Instance of vCenter
            si = connect.SmartConnect(host=vc_settings["vcenter"],
                                      user=kwargs['user'],
                                      pwd=kwargs['passw'],
                                      port=443,
                                      sslContext=context)


        except IOError as e:
            pass
            atexit.register(Disconnect, si)
        content = si.RetrieveContent()
        template = None


        template = get_obj(content, [vim.VirtualMachine], kwargs['template_name'])

        if template:
            clone_vm(content, template, kwargs['vm_name'], si,vc_settings["datacenter"],
                kwargs['vm_folder'], kwargs['datastore'], vc_settings["cluster"],
                kwargs['resource_pool'], kwargs['power_on'], kwargs['nic0'], kwargs['nic1'],
                kwargs['nic2'], kwargs['cpus'], kwargs['mem'],
                kwargs['iops'], kwargs['disk'])

        else:
            print("template not found")

    except vmodl.MethodFault as e:
        print("Caught vmodl fault: %s" % e.msg)
        return 1

    except Exception as e:
        print("Caught exception: %s" % str(e))
        return 1