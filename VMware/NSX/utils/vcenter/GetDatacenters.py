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

def getDatacenterId(name):

    dc_list = getAllDatacenters()
    # print dc_list

    for dc in dc_list:
        if dc['name'] == name:
            return dc['moId']

    return ""



def getAllDatacenters():

    try:
        si = None
        try:
            
            si = connect.SmartConnect(host=vc_settings["vcenter"],
                                      user="",
                                      pwd="",
                                      port=443,
                                      sslContext=context)

        except IOError, e:
            pass
            atexit.register(Disconnect, si)

        content = si.RetrieveContent()

        obj_view = content.viewManager.CreateContainerView(content.rootFolder,[vim.Datacenter],True)
        
        dc_list = obj_view.view
        obj_view.Destroy()

        datacenters = []

        for dc in dc_list:
            datacenters.append({'name' : dc.name, 'moId' : dc._moId})
        
    except vmodl.MethodFault, e:
        print "Caught vmodl fault: %s" % e.msg
        return 1

    except Exception, e:
        print "Caught exception: %s" % str(e)
        return 1

    return datacenters
