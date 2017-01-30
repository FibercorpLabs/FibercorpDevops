import argparse

from conf import *
from nsxramlclient.client import NsxClient
from CreateReadDelete import CreateLS, CreateEdge, ReadEdge


def get_args():

    """ Get arguments from CLI """
    parser = argparse.ArgumentParser(description='Configure Edge Interfaces')
    parser.add_argument('-h','--hub', help='HUB',type=str,required=True)
    parser.add_argument('-cp','--controlPlane', help='Logical switch control plane mode.',type=str,required=True)
  	parser.add_argument('-dcp','--description', help='Logical switch description.',type=str,required=False)
  	parser.add_argument('-lsn','--logicalSwitchName', help='Logical switch name.',type=str,required=True)
   	parser.add_argument('-tid','--tenantId', help='Openstack Tenant ID',type=str,required=False)

   	parser.add_argument('-u','--username', help='Edge CLI username', type=str, required=True)
   	parser.add_argument('-p','--password', help='Edge CLI password', type=str, required=True)
   	parser.add_argument('-dc','--datacenterId', help='Datacenter object ID.',type=str,required=True)
   	parser.add_argument('-ds','--datastoreId', help='Datastore object ID',type=str,required=True)
   	parser.add_argument('-rp','--resourceId', help='Resource pool object ID',type=str,required=True)
   	parser.add_argument('-ds','--datastoreId', help='Datastore object ID',type=str,required=True)
   	parser.add_argument('-ho','--hostId', help='Host object ID',type=str,required=True)
   	parser.add_argument('-pg','--portgroupId', help='Portgroup object ID',type=str,required=True)
   	parser.add_argument('-ds','--datastoreId', help='Datastore object ID',type=str,required=True)
   	parser.add_argument('-upl','--uplink', help='Uplink IP.',type=str,required=True)
   	parser.add_argument('-i','--internal', help='Internal IP.',type=str,required=True)
   	parser.add_argument('-unet','--uplink', help='Uplink netmask.',type=str,required=True)
   	parser.add_argument('-inet','--netmask', help='Internal netmask.',type=str,required=True)
   	parser.add_argument('-m','--mtu', help='MTU',type=str,required=True)
   	parser.add_argument('-app','--applianceSize', help='Edge appliance size.',type=str,required=True)
   	parser.add_argument('-t','--edgeType', help='Edge type.',type=str,required=True)
   	parser.add_argument('-ui','--uplinkIndex', help='Uplink vnic index.',type=str,required=True)
   	parser.add_argument('-un','--uplinkName', help='Uplink vnic name.',type=str,required=True)
   	
   	
   	
   	
   	
   	
   	


    args = parser.parse_args()
    
    return args

def main():

	args = get_args()



if __name__ = '__main__':
	exit(main())