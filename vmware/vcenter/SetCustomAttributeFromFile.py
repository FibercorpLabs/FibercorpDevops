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
import csv

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

def set_vm_attributes(virtual_machine, key_name, attr_value):
    """
    Set VM custom attributes
    """
    virtual_machine.setCustomValue(key_name,attr_value)

def main():

    parser = argparse.ArgumentParser(description='Set Fibercorp Type & Category custom attribute')
    parser.add_argument('-u', '--user', help='VC User', required=False)
    parser.add_argument('-p', '--passw', help='VC User Pass', required=False)
    parser.add_argument('-v', '--vm', help='VM Name', required=False)
    parser.add_argument('-t', '--type', help='Type', required=False)
    parser.add_argument('-c', '--category', help='Category', required=False)
    parser.add_argument('--os', help='OS', required=False)
    parser.add_argument('--app', help='Application', required=False)
    parser.add_argument('--file', help='CSV File (vm name,application,os)', required=False)

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

        except IOError, e:
            pass
            atexit.register(Disconnect, si)

        content = si.RetrieveContent()
        with open('names.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row['name'], row['app'], row['os'] )
                vm = get_obj(content, [vim.VirtualMachine], row['name'])
                if vm is not None:
                   # vm.setCustomValue("Fibercorp.Type.Names",args.type)
                   # vm.setCustomValue("Fibercorp.Category.Names",args.category)
                    vm.setCustomValue("Fibercorp.OS.Names",row['os'])
                    vm.setCustomValue("Fibercorp.Application.Names",row['app'])

    except vmodl.MethodFault, e:
        print "Caught vmodl fault: %s" % e.msg
        return 1

    except Exception, e:
        print "Caught exception: %s" % str(e)
        return 1


# Start program
if __name__ == "__main__":
    main()


