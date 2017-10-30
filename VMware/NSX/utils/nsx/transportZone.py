from nsx_rest import *
import json
import sys

sys.path.append("../common/")
from jinja import render

# Done
# Output : tzones_list w/ name & id
def getAllTZ():
  r = nsxGet("/api/2.0/vdn/scopes")

  r_dict = json.loads(r)
  # pprint(r_dict)
  
  tzones = []

  scopes = r_dict['allScopes']
  for scope in scopes:
    tzones.append({'name' : scope['name'], 'id' : scope['id']})

  return tzones


# Done
# Output : transportzone_id (for a given name)
# Example: getTZ("GLOBAL-TZ-LAB")
def getTZ(name):
  r = nsxGet("/api/2.0/vdn/scopes")

  r_dict = json.loads(r)
  
  allScopes = r_dict['allScopes']
  for elem in allScopes:
    if name ==elem['name']:
        return  elem['name'], elem['id']

  return ""
