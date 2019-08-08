from pyVim.task import WaitForTask
import atexit
import ssl
import requests
import argparse
from VMWConfigFile import *
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim

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


# # find your cluster, I'm going to cheat for brevity
# cluster = si.content.rootFolder.childEntity[0].hostFolder.childEntity[0]
# get the VMs you are interested in
vms = [cluster.host[0].vm[0], cluster.host[1].vm[0]]
# spec ref: https://www.vmware.com/support/developer/vc-sdk/visdk41pubs/ApiReference/vim.cluster.AffinityRuleSpec.html
# extends: https://www.vmware.com/support/developer/vc-sdk/visdk41pubs/ApiReference/vim.cluster.RuleInfo.html
# Note that you need to set a name.
rule = vim.cluster.AffinityRuleSpec(vm=vms, enabled=True, mandatory=True,
                                    name='affinity-between-2-vms')
ruleSpec = vim.cluster.RuleSpec(info=rule, operation='add')
configSpec = vim.cluster.ConfigSpecEx(rulesSpec=[ruleSpec])
WaitForTask(cluster.ReconfigureEx(configSpec, modify=True))


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

        except IOError, e:
            pass
            atexit.register(Disconnect, si)

        content = si.RetrieveContent()

        # Load JSON in dict

        # Iterate all VMs

        # if VM matches custom attribute in dict
        if vm matches:
            # Find Cluster for the VM
            cluster = get_obj(
                content, [vim.ClusterComputeResource], args.cluster)

            # Find affinity rule
            rule = get_obj(
                content, [vim.cluster.AffinityRuleSpec], affinityRule)

            # create rule spec & config spec
            ruleSpec = vim.cluster.RuleSpec(info=rule, operation='add')
            configSpec = vim.cluster.ConfigSpecEx(rulesSpec=[ruleSpec])

            # apply AR
            WaitForTask(cluster.ReconfigureEx(configSpec, modify=True))

    except vmodl.MethodFault, e:
        print "Caught vmodl fault: %s" % e.msg
        return 1

    except Exception, e:
        print "Caught exception: %s" % str(e)
        return 1


# Start program
if __name__ == "__main__":
    main()
