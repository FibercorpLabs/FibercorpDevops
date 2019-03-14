from __future__ import print_function

from netmiko import ConnectHandler

import sys
import os
import argparse
import getpass
import time
from texttable import Texttable


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
    }

    try:
        file_output = open("report.txt", 'a')
    except IOError:
        file_output = open("report.txt", 'w')


    net_connect = ConnectHandler(**my_device)
    output = net_connect.send_command("sh int * status")

    #Write output into file
    localtime = time.asctime( time.localtime(time.time()) )
    file_output.write("IP:" + args.host + '\n')
    file_output.write("Time:" + localtime + '\n')
    file_output.write(output + '\n')
    file_output.write('\n')

    #Generatin down interfaces report
    lines = output.splitlines()
    del lines[0:2]
    
    interfaces_down = 0
    interfaces_up = 0

    for line in lines:
        status = line.split()[7]
        if status == 'Down':
            interfaces_down += 1
        else:
            interfaces_up += 1

    output = net_connect.send_command("sh mac address-table")
    file_output.write(output + '\n')
    file_output.write('\n')
    
    lines = output.splitlines()
    del lines[0]
    vlans = {}
    for line in lines:
        vlan_id = line.split()[1]
        if vlan_id in vlans:
            vlans[vlan_id] += 1
        else:
            vlans[vlan_id] = 1

    print("Interfaces down:" + str(interfaces_down))
    print("Interfaces up:" + str(interfaces_up))
    print("")

    tab = Texttable()
    headings = ['VID','MAC Counting']
    tab.header(headings)
    vlans_ids = vlans.keys()
    macs = vlans.values() 

    for row in zip(vlans_ids,macs):
        tab.add_row(row)
    s = tab.draw()
    print(s)
    print("")
    output = net_connect.send_command("sh mac address-table count")
    print (output)


    #Clossing connection    
    net_connect.disconnect()

if __name__ == '__main__':
    main()