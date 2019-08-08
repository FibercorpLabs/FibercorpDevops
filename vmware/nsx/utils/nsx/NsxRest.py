import requests
import os
import ssl


class NsxRest(object):
    def __init__(self, manager, username, password):
        self._manager = manager
        self._auth = (username, password)
        
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_NONE
        
        def nsxGet(url, headers = frozenset({'Accept': 'application/json'})):
            return requests.get(manager + url, auth=self._auth, verify=False, headers=headers)
            
        def nsxPost(url, data, headers = frozenset({'Accept': 'application/json'})):
            return requests.post(manager + url, data=data, auth=self._auth, verify=False, headers=headers)
        
        def nsxPut(url, data, headers = frozenset({'Accept': 'application/json'})):
            return requests.put(manager + url, data=data, auth=self._auth, verify=False, headers=headers)
        
        def nsxDelete(url, headers = frozenset({'Accept': 'application/json'})):
            return requests.delete(manager + url, auth=self._auth, verify=False, headers=headers)
