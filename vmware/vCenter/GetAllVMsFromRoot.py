#GetAllVMWTemplates.py

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


# Disabling urllib3 ssl warnings
requests.packages.urllib3.disable_warnings()
 
# Disabling SSL certificate verification
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.verify_mode = ssl.CERT_NONE

def wait_for_tasks(service_instance, tasks):
    """Given the service instance si and tasks, it returns after all the
   tasks are complete
   """
    property_collector = service_instance.content.propertyCollector
    task_list = [str(task) for task in tasks]
    # Create filter
    obj_specs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task)
                 for task in tasks]
    property_spec = vmodl.query.PropertyCollector.PropertySpec(type=vim.Task,
                                                               pathSet=[],
                                                               all=True)
    filter_spec = vmodl.query.PropertyCollector.FilterSpec()
    filter_spec.objectSet = obj_specs
    filter_spec.propSet = [property_spec]
    pcfilter = property_collector.CreateFilter(filter_spec, True)
    try:
        version, state = None, None
        # Loop looking for updates till the state moves to a completed state.
        while len(task_list):
            update = property_collector.WaitForUpdates(version)
            for filter_set in update.filterSet:
                for obj_set in filter_set.objectSet:
                    task = obj_set.obj
                    for change in obj_set.changeSet:
                        if change.name == 'info':
                            state = change.val.state
                        elif change.name == 'info.state':
                            state = change.val
                        else:
                            continue

                        if not str(task) in task_list:
                            continue

                        if state == vim.TaskInfo.State.success:
                            # Remove task from taskList
                            task_list.remove(str(task))
                        elif state == vim.TaskInfo.State.error:
                            raise task.info.error
            # Move to next version
            version = update.version
    finally:
        if pcfilter:
            pcfilter.Destroy()


def get_vim_objects(content, vim_type):
    '''Get vim objects of a given type.'''
    return [item for item in content.viewManager.CreateContainerView(
        content.rootFolder, [vim_type], recursive=True
    ).view]





def main():

    parser = argparse.ArgumentParser(description='Create VMW portgroup on DVS')
    parser.add_argument('-u', '--user', help='VC User', required=True)
    parser.add_argument('-p', '--passw', help='VC User Pass', required=True)
    parser.add_argument('-f', '--folder', help='VC User Pass', required=False)

    args = parser.parse_args()

    try:
        si = None
        try:
            
            # print "Trying to connect to VCENTER SERVER . . ."

            #si = Service Instance of vCenter
            si = connect.SmartConnect(host="10.120.80.10",
                                      user=args.user,
                                      pwd=args.passw,
                                      port=443,
                                      sslContext=context)

        except IOError, e:
            pass
            atexit.register(Disconnect, si)

        content = si.RetrieveContent()
        for vm in get_vim_objects(content, vim.VirtualMachine):
            if not vm.config == None:
                if not vm.config.template:
                    time.sleep ( 4 )
                    if  vm.resourcePool.summary.name == "Resources":
                        print "VM Name    : ", vm.name
                        if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                            task = vm.PowerOff()
                            wait_for_tasks(si, [task])
                            task2 = vm.Destroy_Task()
                            wait_for_tasks(si, [task2])
                        task2 = vm.Destroy_Task()
                        wait_for_tasks(si, [task2])
 

    except vmodl.MethodFault, e:
        print "Caught vmodl fault: %s" % e.msg
        return 1

    except Exception, e:
        print "Caught exception: %s" % str(e)
        return 1




# Start program
if __name__ == "__main__":
    main()