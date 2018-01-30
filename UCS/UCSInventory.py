import os
import json
import configparser as ConfigParser
from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.utils.inventory import get_inventory

from pprint import pprint

config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'connection.cfg'))

total_slo_num_of_blades = 0

""" FIBERCORP DC - SAN LORENZO """

host = "ucs_slo_old"

hostname = config.get(host, "hostname")
username = config.get(host, "username")
password = config.get(host, "password")

handle = UcsHandle(hostname, username, password)
handle.login(auto_refresh=True, force=True)

blades = handle.query_classid("computeBlade")

total_slo_old_memory = 0
total_slo_old_num_of_cpus = 0
slo_old_blades = []

""" SLO ISLA VIEJA """

total_slo_num_of_blades += len(blades)

for blade in blades:
	blade_dict = {'model' : blade.model,
				  'serial' : blade.serial,
				  'memory' : blade.total_memory,
				  'num_of_cpus' : blade.num_of_cpus,
				  'slot_id' : blade.slot_id,
				  'chassis_id' : blade.chassis_id,
				  'usr_lbl' : blade.usr_lbl}

	slo_old_blades.append(blade_dict)

	del blade_dict

	total_slo_old_memory += int(blade.total_memory)
	total_slo_old_num_of_cpus += int(blade.num_of_cpus)

total_slo_num_of_cores = 0

inventory = get_inventory(handle, component="cpu")

cpu_list = inventory[hostname]['cpu']

for cpu in cpu_list:
	total_slo_num_of_cores += int(cpu['cores'])

handle.logout()

""" SLO ISLA NUEVA """

host = "ucs_slo_new"

hostname = config.get(host, "hostname")
username = config.get(host, "username")
password = config.get(host, "password")

handle = UcsHandle(hostname, username, password)
handle.login(auto_refresh=True, force=True)

blades = handle.query_classid("computeBlade")

total_slo_new_memory = 0
total_slo_new_num_of_cpus = 0
slo_new_blades = []

total_slo_num_of_blades += len(blades)

for blade in blades:
	blade_dict = {'model' : blade.model,
				  'serial' : blade.serial,
				  'memory' : blade.total_memory,
				  'num_of_cpus' : blade.num_of_cpus,
				  'slot_id' : blade.slot_id,
				  'chassis_id' : blade.chassis_id,
				  'usr_lbl' : blade.usr_lbl}

	slo_new_blades.append(blade_dict)
	
	del blade_dict

	total_slo_new_memory += int(blade.total_memory)
	total_slo_new_num_of_cpus += int(blade.num_of_cpus)

total_slo_memory = total_slo_old_memory + total_slo_new_memory
total_slo_num_of_cpus = total_slo_old_num_of_cpus + total_slo_new_num_of_cpus

inventory = get_inventory(handle, component="cpu")

cpu_list = inventory[hostname]['cpu']

for cpu in cpu_list:
	total_slo_num_of_cores += int(cpu['cores'])

handle.logout()

#############################################################################################################

total_hor_num_of_blades = 0

""" FIBERCORP DC - HORNOS """

""" HOR ISLA VIEJA """

host = "ucs_hor_old"

hostname = config.get(host, "hostname")
username = config.get(host, "username")
password = config.get(host, "password")

handle = UcsHandle(hostname, username, password)
handle.login(auto_refresh=True, force=True)

blades = handle.query_classid("computeBlade")

total_hor_old_memory = 0
total_hor_old_num_of_cpus = 0
hor_old_blades = []

total_hor_num_of_blades += len(blades)

for blade in blades:
	blade_dict = {'model' : blade.model,
				  'serial' : blade.serial,
				  'memory' : blade.total_memory,
				  'num_of_cpus' : blade.num_of_cpus,
				  'slot_id' : blade.slot_id,
				  'chassis_id' : blade.chassis_id,
				  'usr_lbl' : blade.usr_lbl}

	hor_old_blades.append(blade_dict)

	del blade_dict

	total_hor_old_memory += int(blade.total_memory)
	total_hor_old_num_of_cpus += int(blade.num_of_cpus)

total_hor_num_of_cores = 0

inventory = get_inventory(handle, component="cpu")

cpu_list = inventory[hostname]['cpu']

for cpu in cpu_list:
	if(int(cpu['cores'] != 'unspecified')):
		total_hor_num_of_cores += int(cpu['cores'])

handle.logout()

""" HOR ISLA NUEVA """

host = "ucs_hor_new"

hostname = config.get(host, "hostname")
username = config.get(host, "username")
password = config.get(host, "password")

handle = UcsHandle(hostname, username, password)
handle.login(auto_refresh=True, force=True)

blades = handle.query_classid("computeBlade")


total_hor_new_memory = 0
total_hor_new_num_of_cpus = 0
hor_new_blades = []

total_hor_num_of_blades += len(blades)

for blade in blades:
	blade_dict = {'model' : blade.model,
				  'serial' : blade.serial,
				  'memory' : blade.total_memory,
				  'num_of_cpus' : blade.num_of_cpus,
				  'slot_id' : blade.slot_id,
				  'chassis_id' : blade.chassis_id,
				  'usr_lbl' : blade.usr_lbl}

	hor_new_blades.append(blade_dict)

	del blade_dict

	total_hor_new_memory += int(blade.total_memory)
	total_hor_new_num_of_cpus += int(blade.num_of_cpus)

total_hor_memory = total_hor_old_memory + total_hor_new_memory
total_hor_num_of_cpus = total_hor_old_num_of_cpus + total_hor_new_num_of_cpus

inventory = get_inventory(handle, component="cpu")

cpu_list = inventory[hostname]['cpu']

for cpu in cpu_list:
	total_hor_num_of_cores += int(cpu['cores'])

handle.logout()


ucs_inventory = {'san_lorenzo' : {'num_of_blades' : total_slo_num_of_blades,
								  'num_of_sockets' : total_slo_num_of_cpus,
								  'num_of_cores' : total_slo_num_of_cores,
								  'total_memory' : total_slo_memory,
								  'slo_old_isle' : {'blades' : slo_old_blades},
								  'slo_new_isle' : {'blades' : slo_new_blades}},
				 'hornos' : {'num_of_blades' : total_hor_num_of_blades,
							 'num_of_sockets' : total_hor_num_of_cpus,
							 'num_of_cores' : total_hor_num_of_cores,
							 'total_memory' : total_hor_memory,
							 'hor_old_isle' : {'blades' : hor_old_blades},
							 'hor_new_isle' : {'blades' : hor_new_blades}}}

ucs_inventory_json = json.dumps(ucs_inventory,sort_keys=True, indent=4)

pprint(ucs_inventory_json)