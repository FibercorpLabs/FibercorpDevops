import requests
import os
import ssl

# Disabling urllib3 ssl warnings
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
 
# Disabling SSL certificate verification
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.verify_mode = ssl.CERT_NONE


MANAGER = 'https://10.120.80.21'
USER = 'admin'
PASS = 'F1b3rc0rp'

# NSX GET Operation - Example
# nsxGet('/api/2.0/services/vcconfig')
def nsxGet(url):
  rheaders = {'Accept': 'application/json'}
  r = requests.get(MANAGER + url, auth = (USER, PASS), verify = False, headers = rheaders)
  return r.text


def nsxPost(url, data):
  rheaders = {'Content-Type': 'application/xml'}
  r = requests.post(MANAGER + url, data = data, auth = (USER, PASS), verify = False, headers = rheaders)
  return r

def nsxPostAsJson(url, data):
  rheaders = {'Content-Type': 'application/json'}
  r = requests.post(MANAGER + url, data = data, auth = (USER, PASS), verify = False, headers = rheaders)
  return r


def nsxPut(url, data):
  rheaders = {'Content-Type': 'application/xml'}
  r = requests.put(MANAGER + url, data = data, auth = (USER, PASS), verify = False, headers = rheaders)
  return r

def nsxPutAsJson(url, data):
  rheaders = {'Content-Type': 'application/json'}
  r = requests.put(MANAGER + url, data = data, auth = (USER, PASS), verify = False, headers = rheaders)
  return r


def nsxDelete(url):
  rheaders = {'Content-Type': 'application/xml'}
  r = requests.delete(MANAGER + url, auth = (USER, PASS), verify = False, headers = rheaders)
  return r




