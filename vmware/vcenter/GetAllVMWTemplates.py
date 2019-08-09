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
import getpass


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


def get_vim_objects_from_folder(content, folder, vim_type):
    '''Get vim objects of a given type.'''
    return [item for item in content.viewManager.CreateContainerView(
        folder, [vim_type], recursive=True
    ).view]



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



def main():

    parser = argparse.ArgumentParser(description='Create VMW portgroup on DVS')
    parser.add_argument('-u', '--user', help='VC User', required=True)
    parser.add_argument('-p', '--passw', help='VC User Pass', required=False)
    parser.add_argument('-f', '--folder', help='VC User Pass', required=False, default="Templates")

    args = parser.parse_args()
    if not args.passw:
        args.passw = getpass.getpass(prompt='Enter password')

    try:
        si = None
        try:
            
            # print "Trying to connect to VCENTER SERVER . . ."

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
        


        if args.folder:
            destfolder = get_obj(content, [vim.Folder], args.folder)
        else:
            destfolder = content.rootFolder

        #print content.about.instanceUuid


        for vm in get_vim_objects_from_folder(content, destfolder, vim.VirtualMachine):
        	if not vm.config == None:
        	    if vm.config.template:
        		    print vm.name

 

    except vmodl.MethodFault, e:
        print "Caught vmodl fault: %s" % e.msg
        return 1

    except Exception, e:
        print "Caught exception: %s" % str(e)
        return 1




# Start program
if __name__ == "__main__":
    main()
    