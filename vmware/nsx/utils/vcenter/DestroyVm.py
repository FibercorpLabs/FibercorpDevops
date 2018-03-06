#!/usr/bin/env python
"""
vSphere Python SDK program for shutting down VMs
"""

from VMWConfigFile import *
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl

import argparse
import atexit
import getpass
import sys
import ssl

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

def Destroy_VM(vmname):

    service_instance = None
    context = ssl._create_unverified_context()
    context.verify_mode = ssl.CERT_NONE

    try:
        service_instance = SmartConnect(host="",
                                        user="",
                                        pwd="",
                                        port=443,
                                        sslContext=context)
        if not service_instance:
            print("Could not connect to the specified host using specified "
                  "username and password")
            return -1

        atexit.register(Disconnect, service_instance)

        content = service_instance.RetrieveContent()
        vm = get_obj(content, [vim.VirtualMachine], vmname)
        #vm.PowerOnVM_Task()
        #vm.Destroy_Task()

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0