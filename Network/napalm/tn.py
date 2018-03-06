# Sample script to demonstrate loading a config for a device.
#
# Note: this script is as simple as possible: it assumes that you have
# followed the lab setup in the quickstart tutorial, and so hardcodes
# the device IP and password.  You should also have the
# 'new_good.conf' configuration saved to disk.
from __future__ import print_function

from netmiko import ConnectHandler

import sys
import os


def main():
    """Transition"""

    # # Use the appropriate network driver to connect to the device:
    # driver = napalm.get_network_driver('ios')

    # # Connect:
    # device = driver(hostname='10.120.80.56', username='lab',
    #                 password='lab123', timeout=180, optional_args={'port': 22, 'keepalive': 45, 'global_delay_factor': 2,})

    # #print('Opening ...')
    # device.open()

    # #print('sending dir')
    # output = device._send_command("dir")

    # # Note that the changes have not been applied yet. Before applying
    # # the configuration you can check the changes:
    # print( output )

    # # close the session with the device.
    # device.close()
    # print('Done.')


    my_device = {
        'host': "10.120.80.56",
        'username': 'lab',
        'password': 'lab123',
        'device_type': 'cisco_ios',
        # Increase (essentially) all sleeps by a factor of 2
        'global_delay_factor': 2,
    }

    net_connect = ConnectHandler(**my_device)
    # Increase the sleeps for just send_command by a factor of 2
    output = net_connect.send_command("dir")
    print(output)
    net_connect.disconnect()


if __name__ == '__main__':
    main()