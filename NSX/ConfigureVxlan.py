from conf import *
from nsxramlclient.client import NsxClient

session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=True)

nwfabric = session.extract_resource_body_example('nwfabricConfig','create')
session.view_body_dict(nwfabric)

rscConf = nwfabric['nwFabricFeatureConfig']['resourceConfig']

rscConf['configSpec']['ipPoolId'] = ''
rscConf['configSpec']['switch'] = 'dvs-37'
rscConf['configSpec']['vlanId'] = ''
rscConf['configSpec']['vmknicCount'] = ''

rscConf['resourceId'] = 'domain-c29'