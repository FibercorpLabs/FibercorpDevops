from conf import *
from nsxramlclient.client import NsxClient


session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

vdnScopes = session.read('vdnScopes','read')
#session.view_body_dict(vdnScopes['body'])

print len(vdnScopes)
print vdnScopes['body']['vdnScopes']['vdnScope']['name'] + ' -- ' + vdnScopes['body']['vdnScopes']['vdnScope']['objectId']


