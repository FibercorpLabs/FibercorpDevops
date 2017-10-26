from nsx_rest import *

import os
import json
import jinja2

from pprint import pprint

#nsxGet('/api/2.0/services/vcconfig')

#TODO RETURN LIST as json
def getAllTZ():
  r = nsxGet("/api/2.0/vdn/scopes")

  # r_dict = json.loads(r)
  # # pprint(r_dict)
  
  # allScopes = r_dict['allScopes']
  # for elem in allScopes:
  #   print elem['id'] + " " + elem['name']

  return r


#Return VDNScope for a give TZ name
#Example: getTZ("GLOBAL-TZ-LAB")
def getTZ(name):
  r = nsxGet("/api/2.0/vdn/scopes")

  r_dict = json.loads(r)
  # pprint(r_dict)
  
  allScopes = r_dict['allScopes']
  for elem in allScopes:
    if name ==elem['name']:
    	print  elem['id']
    	return  elem['id']

  return ""


#TODO: def createTZ(name)

#Example: createLS("some","GLOBAL-TZ-LAB")
def createLS(name,tzone, tenantId=""):
  xml_LS = "<virtualWireCreateSpec> \
  <name>" + name + "</name>\
  <tenantId>" + tenantId + "</tenantId>\
  </virtualWireCreateSpec>"

  vdnScope = getTZ(tzone)
  nsxPost("/api/2.0/vdn/scopes/" + vdnScope + "/virtualwires",xml_LS)


def getLS(tzone):
  vdnScope = getTZ(tzone)
  return nsxGet("/api/2.0/vdn/scopes/" + vdnScope + "/virtualwires")


def getAllEdges():
    r = nsxGet("/api/4.0/edges")

    r_dict = json.loads(r)
    allEdges = r_dict['edgePage']['data']

    #pprint(allEdges)
    for edge in allEdges:
      print edge['id'] + " >> " + edge['name']


def getEdge(name):
  r = nsxGet("/api/4.0/edges")

  r_dict = json.loads(r)
    
  allEdges = r_dict['edgePage']['data']

  for edge in allEdges:
    if edge['name'] == name:
      return edge['id']

  return ""


def createEdge(datacenterMoid,
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
  nsx_edge_xml = os.path.join(dir, '../templates/nsx_edge.j2')

  print jinja2.render(nsx_edge_xml, jinja_vars)



createEdge("data1", "some1", "descriptIOnN", "xL", "rs-1", "ds-1", "idx99", "vnicSome", "UPLINK",
  "pg0101", "192.168.0.1", "255.255.255.0", "1500", "True", "user01", "jaja123", "True")


