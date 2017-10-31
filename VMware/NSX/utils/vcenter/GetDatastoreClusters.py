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

def getDSClusterId(name):

    ds_cluster_list = GetAllDatastoreClusters()
    # print ds_cluster_list

    for ds_cluster in ds_cluster_list:
        if ds_cluster['name'] == name:
            return ds_cluster['moId']

    return ""



def GetAllDatastoreClusters():

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

        content = si.RetrieveContent()

        obj_view = content.viewManager.CreateContainerView(content.rootFolder,[vim.StoragePod],True)
        
        ds_cluster_list = obj_view.view
        obj_view.Destroy()

        datastore_clusters = []

        for ds_cluster in ds_cluster_list:
            print(ds_cluster.name)
            datastore_clusters.append({'name' : ds_cluster.name, 'moId' : ds_cluster._moId})
        
    except vmodl.MethodFault as e:
        print("Caught vmodl fault: %s" % e.msg)
        return 1

    except Exception as e:
        print("Caught exception: %s" % str(e))
        return 1

    return datastore_clusters
