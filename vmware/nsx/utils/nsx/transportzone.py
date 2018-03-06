import json
import sys

from nsx_rest import * 
sys.path.append("../utils/common/")

from jinja import render
from commonfunctions import removeEmptyParams
from pprint import pprint 

def getAllTzId():
  r = nsxGet("/api/2.0/vdn/scopes")

  r_dict = json.loads(r)
  
  tzones = []

  scopes = r_dict['allScopes']
  for scope in scopes:
    tzones.append({'name' : scope['name'], 'id' : scope['id']})

  return tzones


# Example: getTZbyName("GLOBAL-TZ-LAB")
def getTzIdByName(name):
  r = nsxGet("/api/2.0/vdn/scopes")

  r_dict = json.loads(r)
  
  allScopes = r_dict['allScopes']
  for elem in allScopes:
    if name == elem['name']:
        return  elem['name'], elem['id']

  return None, None

# Example: getTZbyId("")
def getTzById(tzId):
  r = nsxGet("/api/2.0/vdn/scopes/" + tzId)
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