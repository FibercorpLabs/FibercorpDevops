from pyVim.task import WaitForTask
import atexit
import ssl
import requests
import argparse
from VMWConfigFile import *
from pyVim import connect
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vmodl
from pyVmomi import vim
import os
import sys
import time
import getpass

# Disabling urllib3 ssl warnings
requests.packages.urllib3.disable_warnings()

# Disabling SSL certificate verification
#context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)

context.verify_mode = ssl.CERT_NONE


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


def get_vim_objects(content, vim_type):
    '''Get vim objects of a given type.'''
    return [item for item in content.viewManager.CreateContainerView(
        content.rootFolder, [vim_type], recursive=True
    ).view]


def main():

    parser = argparse.ArgumentParser(
        description='Set Fibercorp Type & Category custom attribute')
    parser.add_argument('-u', '--user', help='VC User', required=False)
    parser.add_argument('-p', '--passw', help='VC User Pass', required=False)
    parser.add_argument('-c', '--cluster', help='Cluster Name', required=False)
    parser.add_argument('--file', help='JSON File', required=False)

    args = parser.parse_args()
    if not args.passw:
        args.passw = getpass.getpass(prompt='Enter password')

    try:
        si = None
        try:
            si = connect.SmartConnect(host="10.120.85.2",
                                      user=args.user,
                                      pwd=args.passw,
                                      port=443,
                                      sslContext=context)

        except IOError as e:
            pass
            atexit.register(Disconnect, si)

        content = si.RetrieveContent()

        # Load JSON in dict

        # Iterate all VMs
        for vm in get_vim_objects(content, vim.VirtualMachine):
            if not vm.config == None:
                if not vm.config.template:
                    if vm.customValue:
                        for i in vm.customValue:
                            print("VM Custom Value: ", i.key)

                    # if VM matches custom attribute in dict
                    # if vm.name:
                    #     # Find Cluster for the VM
                    #     cluster = get_obj(
                    #         content, [vim.ClusterComputeResource], args.cluster)

                    #     # Find affinity rule
                    #     rule = get_obj(
                    #         content, [vim.cluster.AffinityRuleSpec], affinityRule)

                    #     # create rule spec & config spec
                    #     ruleSpec = vim.cluster.RuleSpec(info=rule, operation='add')
                    #     configSpec = vim.cluster.ConfigSpecEx(rulesSpec=[ruleSpec])

                    #     # apply AR
                    #     WaitForTask(cluster.ReconfigureEx(configSpec, modify=True))

    except vmodl.MethodFault as e:
        print("Caught vmodl fault: %s" % e.msg)
        return 1

    except Exception as e:
        print("Caught exception: %s" % str(e))
        return 1


# Start program
if __name__ == "__main__":
    main()
