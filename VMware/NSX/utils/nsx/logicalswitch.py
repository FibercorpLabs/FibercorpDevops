from nsx_rest import *
import json
import sys

sys.path.append("../utils/common/")
from jinja import render
from commonfunctions import removeEmptyParams


# Example: createLS("some","GLOBAL-TZ-LAB")
def createLogicalSwitch(tzone, name, tenantId=None, description=None, controlPlaneMode=None, guestVlanAllowed=None):

  jinja_vars = {"name": name,
                "tenantId" : tenantId,
                "description" : description,
                "controlPlaneMode" : controlPlaneMode,
                "guestVlanAllowed" : guestVlanAllowed}

  jinja_vars = removeOptionalParams(jinja_vars)

  dir = os.path.dirname(__file__)
  nsx_ls_xml = os.path.join(dir, '../templates/nsx_logicalswitch_create.j2')

  data = render(nsx_ls_xml, jinja_vars)

  vdnScope = getTzIdByName(tzone)

  nsxPost("/api/2.0/vdn/scopes/" + vdnScope + "/virtualwires", data)

# TODO:
def getLogicalSwitchById(virtualwireId):
  pass

def getLogicalSwitchIdByName(name, tzone):
  vdnScope = getTzIdByName(tzone)
  r = nsxGet("/api/2.0/vdn/scopes/" + vdnScope + "/virtualwires")

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


def updateLogicalSwitchByName(name):
  pass


def deleteLogicalSwitchByName(name, tzone):
  virtualwireId = getLogicalSwitchIdByName(name, tzone)
  nsxDelete("/api/2.0/vdn/virtualwires/" + virtualwireId)

def deleteLogicalSwitchById(virtualwireId):
  nsxDelete("/api/2.0/vdn/virtualwires/" + virtualwireId)



