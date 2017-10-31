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

def get_vim_objects(content, vim_type):
    '''Get vim objects of a given type.'''
    return [item for item in content.viewManager.CreateContainerView(
        content.rootFolder, [vim_type], recursive=True
    ).view]

def getHostId(name):

    hostList = getAllHostsId()
    # print hostList

    for host in hostList:
        if host['name'] == name:
            return host['moId']

    return ""

def getAllHostsId():

    try:
        si = None
        try:
            
            si = connect.SmartConnect(host=vc_settings["vcenter"],
                                      user=vc_settings["user"],
                                      pwd=vc_settings["password"],
                                      port=443,
                                      sslContext=context)

        except IOError as e:
            pass
            atexit.register(Disconnect, si)

        hosts = []

        content = si.RetrieveContent()
        for host in get_vim_objects(content, vim.HostSystem):
            if not host.config == None:
                hosts.append({'name' : host.name, 'moId' : host._moId})               

    except vmodl.MethodFault as e:
        print("Caught vmodl fault: %s" % e.msg)
        return 1

    except Exception as e:
        print("Caught exception: %s" % str(e))
        return 1

    return hosts