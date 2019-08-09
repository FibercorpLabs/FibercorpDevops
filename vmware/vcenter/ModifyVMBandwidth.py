#ModifyVMBandwidth.py

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



def main():

    parser = argparse.ArgumentParser(description='Modify BW on VM')
    parser.add_argument('-u', '--user', help='VC User', required=True)
    parser.add_argument('-p', '--passw', help='VC User Pass', required=False)
    parser.add_argument('-n', '--name', help='VM  name', required=True)
    parser.add_argument('-b', '--bw', type=long, help='BW in Mbps', required=True)
    parser.add_argument('--portgroup', help='Portgroup in which the shaping will get applied', required=True)
    parser.add_argument('--sym', required=False, help='Symmetric or Assymetric traffic')



    args = parser.parse_args()
    if not args.passw:
        args.passw = getpass.getpass(prompt='Enter password')

    # print "python ModifyVMBandwidth.py -u aliguori@lab.fibercorp.com.ar -b 1 --portgroup LAB_Inside --sym -n ag-block1" 

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
        
        vmToModify = get_obj(content, [vim.VirtualMachine], args.name)
        vm = content.searchIndex.FindByUuid(None, vmToModify.config.uuid, True)
        for device in vm.config.hardware.device:
            if isinstance(device, vim.vm.device.VirtualEthernetCard):

                dvs = content.dvSwitchManager.QueryDvsByUuid(device.backing.port.switchUuid)

                criteria = vim.dvs.PortCriteria()
                criteria.portKey = device.backing.port.portKey
                portToModify = dvs.FetchDVPorts(criteria)

                # print dvs.LookupDvPortGroup(portToModify[0].portgroupKey).config.name
                if args.portgroup == dvs.LookupDvPortGroup(portToModify[0].portgroupKey).config.name:

                    outShapePolicy = vim.dvs.DistributedVirtualPort.TrafficShapingPolicy()
                    outShapePolicy.inherited = False
                    outShapePolicy.enabled = vim.BoolPolicy(value=True)
                    outShapePolicy.averageBandwidth = vim.LongPolicy(value=args.bw * 1000 * 1000)
                    outShapePolicy.peakBandwidth = vim.LongPolicy(value=args.bw * 1000 * 1000)
                    inShapePolicy = vim.dvs.DistributedVirtualPort.TrafficShapingPolicy()
                    if args.sym == "true":
                        inShapePolicy.inherited = False
                        inShapePolicy.enabled = vim.BoolPolicy(value=True)
                        inShapePolicy.averageBandwidth = vim.LongPolicy(value=args.bw * 1000 * 1000)
                        inShapePolicy.peakBandwidth = vim.LongPolicy(value=args.bw * 1000 * 1000)
                    else:
                        inShapePolicy.inherited = False
                        inShapePolicy.enabled = vim.BoolPolicy(value=True)
                        inShapePolicy.averageBandwidth = vim.LongPolicy(value=args.bw * 1000 * 1000 / 4)
                        inShapePolicy.peakBandwidth = vim.LongPolicy(value=args.bw * 1000 * 1000 / 4)

                    configSpec = vim.dvs.DistributedVirtualPort.ConfigSpec()
                    configSpec.operation = "edit"
                    configSpec.key = device.backing.port.portKey
                    setting = vim.dvs.DistributedVirtualPort.Setting()
                    setting.inShapingPolicy = inShapePolicy
                    setting.outShapingPolicy = outShapePolicy
                    configSpec.setting = setting

                    configs = []
                    configs.append(configSpec)

                    dvs.ReconfigureDVPort_Task(configs)
                else:
                    print "nothing to modify"



    except vmodl.MethodFault, e:
        print "Caught vmodl fault: %s" % e.msg
        return 1

    except Exception, e:
        print "Caught exception: %s" % str(e)
        return 1




# Start program
if __name__ == "__main__":
    main()


