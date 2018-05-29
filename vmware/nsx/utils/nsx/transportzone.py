import json
import sys

from .nsx_rest import * 
from ..common.jinja import *

def get_tz_all():
  r = nsxGet("/api/2.0/vdn/scopes", "json")

  r_dict = json.loads(r)
  
  tzones = {"transportzones" : []}

  scopes = r_dict['allScopes']
  for scope in scopes:
    tzones["transportzones"].append({'name' : scope['name'], 'id' : scope['id']})

  return tzones

def get_tz_id_by_name(name):
  r = nsxGet("/api/2.0/vdn/scopes", "json")

  r_dict = json.loads(r)
  
  allScopes = r_dict['allScopes']
  for elem in allScopes:
    if name == elem['name']:
        return  elem['name'], elem['id']
  return None, None

# Example: getTZbyId("")
def get_tz_by_id(tzId):
  r = nsxGet("/api/2.0/vdn/scopes/" + tzId, "json")
  return json.loads(r)


# EXAMPLE:
# clusters is a list
# clusters = [{'objectId' : 'domain-c123'}, {'objectId' : 'domain-c321'}]
def createTz(name, clusters, description="", controlPlaneMode="HYBRID_MODE"):

  jinja_vars = {'name' : name,
                'description' : description,
                'clusters' : clusters,
                'controlPlaneMode' : controlPlaneMode}

  dir = os.path.dirname(__file__)
  nsx_tz_xml = os.path.join(dir, '../../templates/nsx_transportzone_create.j2')
  data = render(nsx_tz_xml, jinja_vars)

  return nsxPost("/api/2.0/vdn/scopes", data)


def updateTzByName(currName, clusters, newName=None, description=None, controlPlaneMode=None):

  jinja_vars = {'objectId' : "",
                'name' : newName,
                'description' : description,
                'clusters' : clusters,
                'controlPlaneMode' : controlPlaneMode}

  tzName, tzId = getTzIdByName(currName)
  jinja_vars['objectId'] = tzId

  jinja_vars = removeEmptyParams(jinja_vars)

  dir = os.path.dirname(__file__)
  nsx_tz_xml = os.path.join(dir, '../../templates/nsx_transportzone_update.j2')
  data = render(nsx_tz_xml, jinja_vars)

  #print(data)
 
  nsxPut("/api/2.0/vdn/scopes/" + tzId + "/attributes", data)

def deleteTzByName(name):
  tzName, tzId = getTzIdByName(name)
  return nsxDelete("/api/2.0/vdn/scopes/" + tzId)

def deleteTzById(tzId):
  nsxDelete("/api/2.0/vdn/scopes/" + tzId)