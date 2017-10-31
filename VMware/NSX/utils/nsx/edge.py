from nsx_rest import *
import json
import sys

sys.path.append("../common/")
from jinja import render

sys.path.append("../vcenter/")
from GetPortgroups import *

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

print(getAllPortgroups())

