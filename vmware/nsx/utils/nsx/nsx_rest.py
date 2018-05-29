import requests
import os
import ssl

# Disabling urllib3 ssl warnings
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
 
# Disabling SSL certificate verification
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.verify_mode = ssl.CERT_NONE


MANAGER = 'https://10.120.110.9'
USER = 'admin'
PASS = 'F1b3rC*rp'

# NSX GET Operation - Example
# nsxGet('/api/2.0/services/vcconfig')
def nsxGet(url, format):
  rheaders = {'Accept': 'application/%s' % format}
  r = requests.get(MANAGER + url, auth = (USER, PASS), verify = False, headers = rheaders)
  return r.text


def nsxPost(url, data, format):
  rheaders = {'Content-Type': 'application/%s' % format}
  r = requests.post(MANAGER + url, data = data, auth = (USER, PASS), verify = False, headers = rheaders)
  return r

# def nsxPostAsJson(url, data):
#   rheaders = {'Content-Type': 'application/json'}
#   r = requests.post(MANAGER + url, data = data, auth = (USER, PASS), verify = False, headers = rheaders)
#   return r


def nsxPut(url, data, format):
  rheaders = {'Content-Type': 'application/%s' % format}
  r = requests.put(MANAGER + url, data = data, auth = (USER, PASS), verify = False, headers = rheaders)
  return r

# def nsxPutAsJson(url, data):
#   rheaders = {'Content-Type': 'application/json'}
#   r = requests.put(MANAGER + url, data = data, auth = (USER, PASS), verify = False, headers = rheaders)
#   return r


def nsxDelete(url, format):
  rheaders = {'Content-Type': 'application/%s' % format}
  r = requests.delete(MANAGER + url, auth = (USER, PASS), verify = False, headers = rheaders)
  return r




