import atexit
import os
import argparse
import time

from lib.vcenter import *
from lib.nsx import *
from utils import *
import configparser

import click

from pprint import pprint

@click.group(chain=True)
@click.pass_context
def cli(ctx):
    click.echo('VMware CLI')
    ctx.ensure_object(dict)

    ctx.obj['CONN'] = None

    config = configparser.ConfigParser()
    config.read('conf/conf.cfg')

    ctx.obj['CONFIG'] = config

@cli.command('vcenter')
@click.pass_context
def vcenter(ctx):
    ctx.obj['CONN'] = vcenter_conn(ctx.obj['CONFIG'])
    click.echo(ctx.obj['CONN'])

@cli.command('nsx')
@click.pass_context
def nsx(ctx):
    ctx.obj['CONN'] = nsx_conn(ctx.obj['CONFIG']) 
    click.echo(ctx.obj['CONN'])

@cli.command('fetch')
@click.pass_context
def fetch(ctx):
    pass

@cli.command('virtual-machines')
@click.pass_context
def fetch_virtual_machines(ctx):
    pass

if __name__ == '__main__':
    cli(obj={})









# def main(*args, **kwargs):
#     parser = argparse.ArgumentParser(description='VMware CLI by FibercorpLabs')
#     parser.add_argument('product', nargs='?', choices=['vcenter', 'nsx'])
#     parser.add_argument('action', nargs='*', choices=['create', 'fetch'])
#     parser.add_argument('-vm', '--virtual-machine', help='Create Virtual machine', action='store_true')
#     parser.add_argument('--vm-name', help='Virtual machine name', required=False)
#     parser.add_argument('--vms', '--virtual-machines-all', help='Fetch all virtual machines', action='store_true')
#     parser.add_argument('--edges', '--nsx-edge-service-gateway', help='Fetch all NSX Edges', action='store_true')


#     args = parser.parse_args()

#     conn = conn_method(config, args.product)

#     if conn.__class__.__name__ == 'dict':

#         if args.action[0] == 'fetch':
#             if args.edges:
#                 edges = get_all_edges(conn)
#                 pprint(edges)




#     elif conn.__class__.__name__ == 'vim.ServiceInstance':

#         if args.action[0] == 'fetch':
#             if args.vms:
#                 vms = get_all_vms(conn)
#                 pprint(vms)






    # else:
    #     print("Connection failed.")
