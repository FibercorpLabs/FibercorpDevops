import os
import configparser as ConfigParser
from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.utils.inventory import get_inventory

from pprint import pprint

config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'connection.cfg'))

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

print("SLO ISLA VIEJA")

print("Number of Blades: %d" %len(blades))

for blade in blades:
	# print(blade.model, blade.serial, blade.dn, blade.total_memory, blade.num_of_cpus)

	total_slo_old_memory += int(blade.total_memory)
	total_slo_old_num_of_cpus += int(blade.num_of_cpus)

print(total_slo_old_memory, total_slo_old_num_of_cpus)

total_slo_num_of_cores = 0

inventory = get_inventory(handle, component="cpu")

cpu_list = inventory[hostname]['cpu']

for cpu in cpu_list:
	total_slo_num_of_cores += int(cpu['cores'])

handle.logout()

host = "ucs_slo_new"

hostname = config.get(host, "hostname")
username = config.get(host, "username")
password = config.get(host, "password")

handle = UcsHandle(hostname, username, password)
handle.login(auto_refresh=True, force=True)

blades = handle.query_classid("computeBlade")

total_slo_new_memory = 0
total_slo_new_num_of_cpus = 0

print("")
print("SLO ISLA NUEVA")

print("Number of Blades: %d" % len(blades))

for blade in blades:
	# print(blade.model, blade.serial, blade.dn, blade.total_memory, blade.num_of_cpus)

	total_slo_new_memory += int(blade.total_memory)
	total_slo_new_num_of_cpus += int(blade.num_of_cpus)

print(total_slo_new_memory, total_slo_new_num_of_cpus)

total_slo_memory = total_slo_old_memory + total_slo_new_memory
total_slo_num_of_cpus = total_slo_old_num_of_cpus + total_slo_new_num_of_cpus

print(total_slo_memory, total_slo_num_of_cpus)

inventory = get_inventory(handle, component="cpu")

cpu_list = inventory[hostname]['cpu']

for cpu in cpu_list:
	total_slo_num_of_cores += int(cpu['cores'])

print("Total Number of Cores: %d" % total_slo_num_of_cores)

handle.logout()

""" FIBERCORP DC - HORNOS """

host = "ucs_hor_old"

hostname = config.get(host, "hostname")
username = config.get(host, "username")
password = config.get(host, "password")

handle = UcsHandle(hostname, username, password)
handle.login(auto_refresh=True, force=True)

blades = handle.query_classid("computeBlade")

total_slo_old_memory = 0
total_slo_old_num_of_cpus = 0

print("HOR ISLA VIEJA")

print("Number of Blades: %d" %len(blades))

for blade in blades:
	# print(blade.model, blade.serial, blade.dn, blade.total_memory, blade.num_of_cpus)

	total_slo_old_memory += int(blade.total_memory)
	total_slo_old_num_of_cpus += int(blade.num_of_cpus)

print(total_slo_old_memory, total_slo_old_num_of_cpus)

total_hor_num_of_cores = 0

inventory = get_inventory(handle, component="cpu")

# pprint(inventory)

cpu_list = inventory[hostname]['cpu']

for cpu in cpu_list:
	if(int(cpu['cores'] != 'unspecified')):
		total_hor_num_of_cores += int(cpu['cores'])

handle.logout()

host = "ucs_hor_new"

hostname = config.get(host, "hostname")
username = config.get(host, "username")
password = config.get(host, "password")

handle = UcsHandle(hostname, username, password)
handle.login(auto_refresh=True, force=True)

blades = handle.query_classid("computeBlade")

total_slo_new_memory = 0
total_slo_new_num_of_cpus = 0

print("")
print("HOR ISLA NUEVA")

print("Number of Blades: %d" % len(blades))

for blade in blades:
	# print(blade.model, blade.serial, blade.dn, blade.total_memory, blade.num_of_cpus)

	total_slo_new_memory += int(blade.total_memory)
	total_slo_new_num_of_cpus += int(blade.num_of_cpus)

print(total_slo_new_memory, total_slo_new_num_of_cpus)

total_slo_memory = total_slo_old_memory + total_slo_new_memory
total_slo_num_of_cpus = total_slo_old_num_of_cpus + total_slo_new_num_of_cpus

print(total_slo_memory, total_slo_num_of_cpus)

inventory = get_inventory(handle, component="cpu")

cpu_list = inventory[hostname]['cpu']

for cpu in cpu_list:
	total_hor_num_of_cores += int(cpu['cores'])

print("Total Number of Cores: %d" % total_hor_num_of_cores)

handle.logout()