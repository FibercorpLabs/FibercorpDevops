#GetAllVMWPortgroups.py
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
	return [item for item in content.viewManager.CreateContainerView(content.rootFolder, [vim_type], recursive=True).view]

def getPortgroupId(name):

	pg_list = getAllPortgroups()
	#print pg_list

	for pg in pg_list:
		if pg['name'] == name:
			return pg['moId']

	return ""

def getAllPortgroups():

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
		#dv_switch = get_obj(content, [vim.DistributedVirtualSwitch], vc_settings["dvs"])

		portgroups = []

		for pg in get_vim_objects(content, vim.dvs.DistributedVirtualPortgroup):
			if not pg.config == None:
				# if args.vlan: print pg.name + "|" + str(pg.config.defaultPortConfig.vlan.vlanId)
				# if not args.vlan: 
				portgroups.append({'name' : pg.name, 'moId' : pg._moId}) 


	except vmodl.MethodFault as e:
		print("Caught vmodl fault: %s" % e.msg)
		return 1

	except Exception as e:
		print("Caught exception: %s" % str(e))
		return 1

	return portgroups