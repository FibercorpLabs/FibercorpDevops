from nsx_rest import *
import json
import sys

sys.path.append("../utils/common/")
from jinja import render
from commonfunctions import removeEmptyParams

from transportzone import *

# Example: createLS("GLOBAL-TZ-LAB", "EDGE-NAME-01")
def createLogicalSwitch(tzone, name, tenantId=None, description=None, controlPlaneMode=None, guestVlanAllowed=None):

  jinja_vars = {"name": name,
                "tenantId" : tenantId,
                "description" : description,
                "controlPlaneMode" : controlPlaneMode,
                "guestVlanAllowed" : guestVlanAllowed}

  jinja_vars = removeEmptyParams(jinja_vars)

  dir = os.path.dirname(__file__)
  nsx_ls_xml = os.path.join(dir, '../../templates/nsx_logicalswitch_create.j2')

  data = render(nsx_ls_xml, jinja_vars)

  vdnScopeName, vdnScopeId = getTzIdByName(tzone)

  return nsxPost("/api/2.0/vdn/scopes/" + vdnScopeId + "/virtualwires", data)


# TODO:
def getLogicalSwitchById(virtualwireId):
  pass

def getLogicalSwitchIdByName(name, tzone):
  tzName, tzId = getTzIdByName(tzone)
  r = nsxGet("/api/2.0/vdn/scopes/" + tzId + "/virtualwires")

  r_dict = json.loads(r)

  vws = r_dict['dataPage']['data']

  for vw in vws:
    if vw['name'] == name:
      return vw['name'], vw['objectId']

  return None

def getAllLogicalSwitchesId():
  r = nsxGet("/api/2.0/vdn/virtualwires")
  r_dict = json.loads(r)

  vws = r_dict['dataPage']['data']

  virtualwires = []

  for vw in vws:
    virtualwires.append({'name' : vw['name'], 'id' : vw['objectId']})

  return virtualwires

def updateLogicalSwitchByName(name, tzone, newName=None, description=None, tenantId=None, controlPlaneMode=None):
      
  jinja_vars = {'name' : newName,
                'description' : description,
                'tenantId' : tenantId,
                'controlPlaneMode' : controlPlaneMode}

  jinja_vars = removeEmptyParams(jinja_vars)



  vw_name, vw_id = getLogicalSwitchIdByName(name, tzone)

  dir = os.path.dirname(__file__)
  nsx_tz_xml = os.path.join(dir, '../../templates/nsx_logicalswitch_update.j2')
  data = render(nsx_tz_xml, jinja_vars)

  print(data)
 
  nsxPut("/api/2.0/vdn/virtualwires/" + vw_id, data)


def deleteLogicalSwitchByName(name, tzone):
  virtualwireName, virtualwireId = getLogicalSwitchIdByName(name, tzone)
  return nsxDelete("/api/2.0/vdn/virtualwires/" + virtualwireId)

def deleteLogicalSwitchById(virtualwireId):
  return nsxDelete("/api/2.0/vdn/virtualwires/" + virtualwireId)



