import requests
import os
import ssl

# Disabling urllib3 ssl warnings
requests.packages.urllib3.disable_warnings()
 
# Disabling SSL certificate verification
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.verify_mode = ssl.CERT_NONE


MANAGER = 'https://10.120.80.21'
USER = 'admin'
PASS = 'F1b3rc0rp'

# NSX GET Operation - Example
# nsxGet('/api/2.0/services/vcconfig')
def nsxGet(url, fileName=None):
  rheaders = {'Accept': 'application/json'}
  r = requests.get(MANAGER + url, auth = (USER, PASS), verify = False, headers = rheaders)
  if fileName == None:
    #print r.text
    return r.text
  else:
    #print(('REST %s is in file %s.' % (url, fileName)))
    with open(fileName, 'w') as newFile:
      #print(r.text, file=newFile)
      return r.text

def nsxPost(url, data):
  rheaders = {'Content-Type': 'application/xml'}
  r = requests.post(MANAGER + url, data = data, auth = (USER, PASS), verify = False, headers = rheaders)
  #print(r.text)
  return r


def nsxPut(url, data):
  rheaders = {'Content-Type': 'application/xml'}
  r = requests.put(MANAGER + url, data = data, auth = (USER, PASS), verify = False, headers = rheaders)
  #print(r.text)
  return r


def nsxDelete(url):
  rheaders = {'Content-Type': 'application/xml'}
  r = requests.delete(MANAGER + url, auth = (USER, PASS), verify = False, headers = rheaders)
  #print(r.text)
  return r




