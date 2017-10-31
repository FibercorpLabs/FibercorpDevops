from nsx_rest import *
import json
import sys

sys.path.append("../common/")
from jinja import render



# TODO: def createTZ(name)
# Example: createLS("some","GLOBAL-TZ-LAB")
def createLS(tzone, name, tenantId="", description="", controlPlaneMode="", guestVlanAllowed=False):

  jinja_vars = {"name": name,
                "tenantId" : tenantId,
                "description" : description,
                "controlPlaneMode" : controlPlaneMode,
                "guestVlanAllowed" : guestVlanAllowed}

  dir = os.path.dirname(__file__)
  nsx_ls_xml = os.path.join(dir, '../templates/nsx_logicalswitch_create.j2')

  data = render(nsx_ls_xml, jinja_vars)
  print type(data)

  vdnScope = getTZ(tzone)

  nsxPost("/api/2.0/vdn/scopes/" + vdnScope + "/virtualwires", data)

# Done
# Output : logicalswitch_id
def getLS(name, tzone=None):
  if tzone is None:
    r = nsxGet("/api/2.0/vdn/virtualwires")
    r_dict = json.loads(r)

    vws = r_dict['dataPage']['data']
    virtualwires = []

    for vw in vws:
      virtualwires.append({'name' : vw['name'], 'id' : vw['objectId']})

    return virtualwires

  else:
    vdnScope = getTZ(tzone)
    r = nsxGet("/api/2.0/vdn/scopes/" + vdnScope + "/virtualwires")

    r_dict = json.loads(r)

    vws = r_dict['dataPage']['data']

    for vw in vws:
      if vw['name'] == name:
        return vw['objectId']

