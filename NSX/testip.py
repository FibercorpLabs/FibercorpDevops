import ipaddress

net = ipaddress.ip_network('192.168.0.0/24')

print type(str(net))