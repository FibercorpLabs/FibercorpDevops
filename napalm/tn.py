from __future__ import print_function

from netmiko import ConnectHandler

import sys
import os
import argparse
import getpass
import time


def main():
    parser = argparse.ArgumentParser(description='Configure Loop Protection')
    parser.add_argument('-u', '--user', help='User', required=True)
    parser.add_argument('-p', '--passw', help='User Pass', required=False)
    parser.add_argument('-d', '--host', help='Host', required=True)
    args = parser.parse_args()
    if not args.passw:
        args.passw = getpass.getpass(prompt='Enter password')

    my_device = {
        'host': args.host,
        'username': args.user,
        'password': args.passw,
        'device_type': 'cisco_ios',
        'global_delay_factor': 1,
    }

    uplink_description = "FC-UPLINK-PORT"

    try:
        file_output = open("output.txt", 'a')
    except IOError:
        file_output = open("output.txt", 'w')

    initial_config = open('initial_config.txt', 'r').read().splitlines()
    
    trunk_native_config = ['switchport trunk native vlan 4000',
                           'switchport trunk allowed vlan add 4000',
                           'switchport trunk allowed vlan remove 1',
                           'exit']

    hybrid_native_config = ['switchport hybrid native vlan 4000',
                            'switchport hybrid allowed vlan remove 1',
                            'switchport hybrid allowed vlan add 4000',
                            'exit']

    net_connect = ConnectHandler(**my_device)

    #Write output into file
    localtime = time.asctime( time.localtime(time.time()) )
    file_output.write("IP:" + args.host + '\n')
    file_output.write("Time:" + localtime + '\n')

    #Setting initial config
    print("** Setting global config **")
    output = net_connect.send_config_set(initial_config)
    print (output)
    file_output.write(output)


    #Setting GigabitEthernet ports config
    print("** Setting GigabitEthernet ports config **")
    for num in range(1,25):
        interface_name = "GigabitEthernet 1/" + str(num)
        command = "sh interface " + interface_name + " switchport"
        output = net_connect.send_command(command)
        lines = output.splitlines()
        mode = lines[1].split("Administrative mode: ",1)[1]
        native_vlan = ""
        config = ""
        if mode == "trunk":
            native_vlan = lines[3].split("Trunk Native Mode VLAN: ", 1)[1]
            if native_vlan == "1":
                config = trunk_native_config.copy()
                config.insert(0,"interface " + interface_name)
            else:
                config = ["interface " + interface_name,
                         "switchport trunk allowed vlan add " + native_vlan,
                         'exit']
            output = net_connect.send_config_set(config)
            print (output)
            file_output.write(output)
        if mode == "hybrid":
            native_vlan = lines[12].split("Hybrid Native Mode VLAN: ", 1)[1]
            if native_vlan == "1":
                config = hybrid_native_config.copy()
                config.insert(0,"interface " + interface_name)
            else:
                config = ["interface " + interface_name,
                         "switchport hybrid allowed vlan add " + native_vlan,
                         'exit']
            output = net_connect.send_config_set(config)
            print (output)
            file_output.write(output)

    print("** Setting 10GigabitEthernet ports config **")

    for num in range(1,3):
        interface_name = "10GigabitEthernet 1/" + str(num)
        #Obtaining interface description
        command = "sh run interface " + interface_name + " | include description"
        output = net_connect.send_command(command)
        if output:
            description = output.split()[1]
        else:
            description = ""

        if description != uplink_description:
            command = "sh interface " + interface_name + " switchport"
            output = net_connect.send_command(command)
            lines = output.splitlines()
            mode = lines[1].split("Administrative mode: ",1)[1]
            native_vlan = ""

            if mode == "trunk":
                native_vlan = lines[3].split("Trunk Native Mode VLAN: ", 1)[1]
                if native_vlan == "1":
                    config = trunk_native_config.copy()
                    config.insert(0,"interface " + interface_name)
                else:
                    config = ["interface " + interface_name,
                             "switchport trunk allowed vlan add " + native_vlan,
                             "no spanning-tree",
                             "loop-protect",
                             "loop-protect action log shutdown",
                             'exit']
                output = net_connect.send_config_set(config)
                print (output)
                file_output.write(output)

            if mode == "hybrid":
                native_vlan = lines[12].split("Hybrid Native Mode VLAN: ", 1)[1]
                if native_vlan == "1":
                    config = hybrid_native_config.copy()
                    config.insert(0,"interface " + interface_name)
                else:
                    config = ["interface " + interface_name,
                             "switchport hybrid allowed vlan add " + native_vlan,
                             "no spanning-tree",
                             "loop-protect",
                             "loop-protect action log shutdown",
                             'exit']
                output = net_connect.send_config_set(config)
                print (output)
                file_output.write(output)
        else:
            print(interface_name + " is " + description)

    print("** Saving config **")
    output = net_connect.send_command_expect("copy run start")
    print(output)
    file_output.write(output)

    print("** Closing connection **")

    #Clossing connection    
    net_connect.disconnect()

if __name__ == '__main__':
    main()