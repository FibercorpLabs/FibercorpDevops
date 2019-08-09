# TODO: Need to fix urllib library
import urllib
import yaml
import ssl
import socket
import logging
import argparse
from termcolor import colored


def check_server(address, port):
    s = socket.socket()
    logging.debug("Attempting to connect to %s on port %s" % (address, port))
    try:
        s.connect((address, port))
        logging.debug("Connected to %s on port %s" % (address, port))
        print(colored("Service: UP", 'green'))
        return True
    
    except socket.error as e:
        logging.debug("Connection to %s on port %s failed: %s" % (address, port, e))
        print(colored("Service: DOWN", 'red'))
        return False


def get_args():
    parser = argparse.ArgumentParser(description='Check vRA Status')
    parser.add_argument('-d', '--debug', dest='debug', required=False, action='store_true', help='debug')
    parser.add_argument('-f', '--file', required=True, help='YAML file with vRA infra')
    return parser.parse_args()

# TODO: Should not call private method
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
        print("Checking service:", service)
        print("VM:", cfg[section][service]["vmname"], ", ip: ", cfg[section][service]["ip"], ", port: ",
              cfg[section][service]["port"])
        
        if "url" in cfg[section][service]:
            print("Checking URL:", cfg[section][service]["url"])
            logging.debug("Expected value in response: %s", cfg[section][service]["expected"])
            
            req = urllib.request.Request.Request(cfg[section][service]["url"])
    
            try:
                resp = urllib3.request.RequestMethods.urlopen(req, context=context)
            
            except urllib.request.Request.HTTPError as e:
                print(colored("Status: ERROR", 'red'))
                logging.debug(e)
            
            except urllib.request.Request.URLError as e:
                print(colored("Status: ERROR", 'red'))
                logging.debug(e)
            
            else:
                # 200 OK
                print(colored("Service: UP", 'green'))
                body = resp.read()
                logging.debug("Body response: %s", body)
                
                if cfg[section][service]["expected"] in body:
                    print(colored("Status: OK", 'green'))
                else:
                    print(colored("Status: ERROR", 'red'))
        else:
            check_server(cfg[section][service]["ip"], cfg[section][service]["port"])
            print("====================================================================")
