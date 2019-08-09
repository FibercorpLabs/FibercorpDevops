#SetCustomAttribute.py
#!/usr/bin/env python
# Copyright 2016 Ariel Liguori
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Python program for listing the vms on an ESX / vCenter host
"""

import atexit
import ssl
import requests
import argparse
from VMWConfigFile import *
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
import getpass




# Disabling urllib3 ssl warnings
requests.packages.urllib3.disable_warnings()
 
# Disabling SSL certificate verification
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
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


def recursiveSet(virtual_machine):
    """
    Set VM custom attributes  (recursive)
    """
    if attr1.get(virtual_machine.summary.config.name) is not None:
        virtual_machine.setCustomValue("Fibercorp.Category.Names",attr1[virtual_machine.summary.config.name])
        # print "setted attr1"
    if attr2.get(virtual_machine.summary.config.name) is not None:
        virtual_machine.setCustomValue("Fibercorp.Type.Names",attr2[virtual_machine.summary.config.name])
        # print "setted attr2"



def set_vm_attributes(virtual_machine, key_name, attr_value):
    """
    Set VM custom attributes
    """
    virtual_machine.setCustomValue(key_name,attr_value)
    # print("vm:", summary.config.name, "key:", key_name, ", value:", attr_value)



def main():

    parser = argparse.ArgumentParser(description='Set Fibercorp Type & Category custom attribute')
    parser.add_argument('-u', '--user', help='VC User', required=True)
    parser.add_argument('-p', '--passw', help='VC User Pass', required=False)
    parser.add_argument('-v', '--vm', help='VM Name', required=False)
    parser.add_argument('-t', '--type', help='Type', required=False)
    parser.add_argument('-c', '--category', help='Category', required=False)



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
        
        vm = get_obj(content, [vim.VirtualMachine], args.vm)
        vm.setCustomValue("Fibercorp.Type.Names",args.type)
        vm.setCustomValue("Fibercorp.Category.Names",args.category)



 

    except vmodl.MethodFault, e:
        print "Caught vmodl fault: %s" % e.msg
        return 1

    except Exception, e:
        print "Caught exception: %s" % str(e)
        return 1


# Start program
if __name__ == "__main__":
    main()


