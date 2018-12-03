import atexit
import os
import argparse
import time

from lib.vcenter import *
from lib.nsx import *
from utils import *
import configparser

from pprint import pprint

config = configparser.ConfigParser()
config.read('conf/conf.cfg')

def main(*args, **kwargs):
    parser = argparse.ArgumentParser(description='VMware CLI by FibercorpLabs')
    parser.add_argument('product', nargs='?', choices=['vcenter', 'nsx'])
    parser.add_argument('action', nargs='*', choices=['create', 'fetch'])
    parser.add_argument('-vm', '--virtual-machine', help='Create Virtual machine', action='store_true')
    parser.add_argument('--vm-name', help='Virtual machine name', required=False)
    parser.add_argument('--vms', '--virtual-machines-all', help='Fetch all virtual machines', action='store_true')
    parser.add_argument('--edges', '--nsx-edge-service-gateway', help='Fetch all NSX Edges', action='store_true')


    args = parser.parse_args()

    conn = conn_method(config, args.product)

    if conn.__class__.__name__ == 'dict':
        
        if args.action[0] == 'fetch':
            if args.edges:
                edges = get_all_edges(conn)
                pprint(edges)




    elif conn.__class__.__name__ == 'vim.ServiceInstance':

        if args.action[0] == 'fetch':
            if args.vms:
                vms = get_all_vms(conn)
                pprint(vms)






    else:
        print("Connection failed.")



# Start program
if __name__ == "__main__":
    main()