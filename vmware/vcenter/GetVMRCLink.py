#GetVMRCLink.py
#https://10.120.78.190:9443/vsphere-client/webconsole.html?vmId=vm-347&vmName=ldap01&serverGuid=7e17f3f6-bf06-4a33-a6e5-bd4197a9bf2f&host=FC-vcenter60-lab.lab.fibercorp.com.ar:443&sessionTicket=cst-VCT-5209a659-97f1-51e6-dcdc-579dcb219717--tp-65-F8-B9-0E-0F-BE-0D-77-83-23-23-E8-D4-D3-E9-14-26-39-64-7C&thumbprint=65:F8:B9:0E:0F:BE:0D:77:83:23:23:E8:D4:D3:E9:14:26:39:64:7C
# Copyright (c) 2015 Christian Gerbrandt <derchris@derchris.eu>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Python port of William Lam's generateHTML5VMConsole.pl
Also ported SHA fingerprint fetching to Python OpenSSL library
"""
from VMWConfigFile import *
import atexit
import OpenSSL
import ssl
import sys
import time
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import getpass
import argparse
import requests



# Disabling urllib3 ssl warnings
requests.packages.urllib3.disable_warnings()
 
# Disabling SSL certificate verification
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.verify_mode = ssl.CERT_NONE



def get_vm(content, name):
    try:
        name = unicode(name, 'utf-8')
    except TypeError:
        pass

    vm = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.VirtualMachine], True)

    for c in container.view:
        if c.name == name:
            vm = c
            break
    return vm


def get_args():

    """ Get arguments from CLI """
    parser = argparse.ArgumentParser(description='Get a VMRC Link to a given VM')
    
    parser.add_argument('-u', '--user', help='VC User', required=True)
    
    parser.add_argument('-p', '--passw', help='VC User Pass', required=True)

    parser.add_argument('-n', '--name',
                        required=True,
                        help='Name of Virtual Machine.')

    args = parser.parse_args()

    if not args.passw:
        args.passw = getpass.getpass(prompt='Enter password')

    return args


def main():
    """
    Simple command-line program to generate a URL
    to open HTML5 Console in Web browser
    """

    args = get_args()

    try:
        si = SmartConnect(host=vc_settings["vcenter"],
                          user=args.user,
                          pwd=args.passw,
                          port=443,
                          sslContext=context)
    except Exception as e:
        print 'Could not connect to vCenter host'
        print repr(e)
        sys.exit(1)

    atexit.register(Disconnect, si)

    content = si.RetrieveContent()

    vm = get_vm(content, args.name)
    vm_moid = vm._moId

    vcenter_data = content.setting
    vcenter_settings = vcenter_data.setting
    console_port = '9443'
    vCenter_port = '443'

    for item in vcenter_settings:
        key = getattr(item, 'key')
        if key == 'VirtualCenter.FQDN':
            vcenter_fqdn = getattr(item, 'value')

    session_manager = content.sessionManager
    session = session_manager.AcquireCloneTicket()

    vc_cert = ssl.get_server_certificate((vc_settings["vcenter"], int(443)))
    vc_pem = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
                                             vc_cert)
    vc_fingerprint = vc_pem.digest('sha1')

    #serverGuid = "7e17f3f6-bf06-4a33-a6e5-bd4197a9bf2"
    serverGuid = content.about.instanceUuid
#ToDo: ServerGUID is hardcoded now

#https://10.120.78.190:9443/vsphere-client/webconsole.html?vmId=vm-347&vmName=ldap01&serverGuid=
#7e17f3f6-bf06-4a33-a6e5-bd4197a9bf2f&host=FC-vcenter60-lab.lab.fibercorp.com.ar:443&sessionTicket=
#cst-VCT-5209a659-97f1-51e6-dcdc-579dcb219717--tp-65-F8-B9-0E-0F-BE-0D-77-83-23-23-E8-D4-D3-E9-14-26-39-64-7C&thumbprint=65:F8:B9:0E:0F:BE:0D:77:83:23:23:E8:D4:D3:E9:14:26:39:64:7C
#
    # print "Open the following URL in your browser to access the " \
    #       "Remote Console.\n" \
    #       "You have 60 seconds to open the URL, or the session" \
    #       "will be terminated.\n\n"
    print "https://" + vc_settings["vcenter"] + ":" + console_port + "/vsphere-client/webconsole.html?vmId=" \
          + str(vm_moid) + "&vmName=" + args.name + "&serverGuid=" + serverGuid + "&host=" + vc_settings["vcenter"] + ":" + vCenter_port \
          + "&sessionTicket=" + session + "&thumbprint=" + vc_fingerprint
    # print "\n\nWaiting for 60 seconds, then exit"
    #time.sleep(60)

# Start program
if __name__ == "__main__":
    main()