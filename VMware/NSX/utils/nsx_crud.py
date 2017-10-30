from nsx_rest import *

import os
import json
import jinja2

from pprint import pprint

def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)

    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)



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
  # # pprint(r_dict)
  
  allScopes = r_dict['allScopes']
  for elem in allScopes:
    if name ==elem['name']:
    	print  elem['id']
    	return  elem['id']

  return ""


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

# Done
# Output : list_of_edges w/ name & id  
def getAllNsxEdges():
    r = nsxGet("/api/4.0/edges")

    r_dict = json.loads(r)
    allEdges = r_dict['edgePage']['data']

    edges = []

    for edge in allEdges:
      edges.append({'name' : edge['name'], 'id' : edge['id']})

    return edges


# Done
# Output : edge_id  
def getNsxEdge(name):
  r = nsxGet("/api/4.0/edges")

  r_dict = json.loads(r)
    
  allEdges = r_dict['edgePage']['data']

  for edge in allEdges:
    if edge['name'] == name:
      return edge['id']

  return ""

# TODO:
def createNsxEdge(datacenterMoid,
               name,
               description,
               applianceSize,
               resourcePoolId,
               datastoreId,
               index,
               vnicName,
               vnicType,
               portgroupId,
               primaryAddress,
               subnetMask,
               mtu,
               isConnected,
               user,
               password,
               remoteAccess):
 
  jinja_vars = {"datacenterMoid" : datacenterMoid,
                "name" : name,
                "description" : description,
                "appliances" : {"applianceSize" : applianceSize,
                                "appliance" : {"resourcePoolId" : resourcePoolId,
                                               "datastoreId" : datastoreId
                                              }},
                "vnics" : [{"index" : index,
                            "name" : vnicName,
                            "type" : vnicType,
                            "portgroupId" : portgroupId,
                            "primaryAddress" : primaryAddress,
                            "subnetMask" : subnetMask,
                            "mtu" : mtu,
                            "isConnected" : isConnected
                           }],
                "cliSettings" : {"user" : user,
                                 "password" : password,
                                 "remoteAccess" : remoteAccess}
                }

  dir = os.path.dirname(__file__)
  nsx_edge_xml = os.path.join(dir, '../templates/nsx_edge_create.j2')

  #nsxPost("/api/4.0/edges", nsx_edge_xml)

  return nsx_edge_xml, jinja_vars



createLS("GLOBAL-TZ-LAB", "ls_test01", "", "description01", "HYBRID_MODE")