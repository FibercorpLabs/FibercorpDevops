import yaml
import urllib2
import ssl
import socket
import re
import sys
import logging
import argparse
from termcolor import colored


def check_server(address, port):
    # Create a TCP socket
    s = socket.socket()
    logging.debug("Attempting to connect to %s on port %s" % (address, port))
    try:
        s.connect((address, port))
        logging.debug( "Connected to %s on port %s" % (address, port))
        print colored("Service: UP", 'green')
        return True

    except socket.error, e:
        logging.debug("Connection to %s on port %s failed: %s" % (address, port, e))
        print colored("Service: DOWN",'red')
        return False

def get_args():
    """ Get arguments from CLI """
    parser = argparse.ArgumentParser(description='Check vRA Status')
    
    parser.add_argument('-d', '--debug', dest='debug', required=False, action='store_true', help='debug')
    parser.add_argument('-f', '--file', required=True, help='YAML file with vRA infra')
    args = parser.parse_args()

    return args





# This restores the same behavior as before.
context = ssl._create_unverified_context()


args = get_args()

if args.debug:
	logging.basicConfig(level=logging.DEBUG)
else:
	logging.basicConfig(level=logging.INFO)



with open(args.file, 'r') as f:
    cfg = yaml.load(f)



for section in cfg:
	for service in cfg[section]:
		print "Checking service:",service
		print "VM:", cfg[section][service]["vmname"], ", ip: ", cfg[section][service]["ip"], ", port: ", cfg[section][service]["port"]

		if "url" in cfg[section][service]: 
			print "Checking URL:", cfg[section][service]["url"]
			logging.debug("Expected value in response: %s", cfg[section][service]["expected"])

			req = urllib2.Request(cfg[section][service]["url"])

			try:
			    resp = urllib2.urlopen(req, context=context)
			
			except urllib2.HTTPError as e:
				print colored("Status: ERROR",'red')
				logging.debug(e)
			
			except urllib2.URLError as e:
				print colored("Status: ERROR",'red')
				logging.debug(e)
			
			else:
			    # 200 OK
			    print colored("Service: UP",'green')
			    body = resp.read()
			    logging.debug("Body response: %s", body)

			    if cfg[section][service]["expected"] in body:
			    	print colored("Status: OK",'green')
			    else:
			    	print colored("Status: ERROR",'red')
		else:
			check_server(cfg[section][service]["ip"], cfg[section][service]["port"])
		print "===================================================================="









