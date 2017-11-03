from nsx_rest import *
import json
import sys

sys.path.append("../utils/common/")
from jinja import render

sys.path.append("../vcenter/")


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



def getNsxEdgeIdByName(name):
  r = nsxGet("/api/4.0/edges")

  r_dict = json.loads(r)
    
  allEdges = r_dict['edgePage']['data']

  for edge in allEdges:
    if edge['name'] == name:
      return edge['id']

  return ""

def getNsxEdge(edgeId):
  r = nsxGet("/api/4.0/edges/" + edgeId)
  r_dict = json.loads(r)
  return r_dict


def createNsxEdge(jinja_vars):

  dir = os.path.dirname(__file__)
  nsx_edge_xml = os.path.join(dir, '../../templates/edge/nsx_edge_create.j2')
  data = render(nsx_edge_xml, jinja_vars) 
  
  return nsxPost("/api/4.0/edges", data)


def deleteNsxEdgeByName(edge_name):
  edgeId = getNsxEdgeIdByName(edge_name)
  return nsxDelete("/api/4.0/edges/" + edgeId)


def deleteNsxEdgeById(edgeId):
  return nsxDelete("/api/4.0/edges/" + edgeId)


def getRemoteAcessStatus(edgeId):
  r = getNsxEdge(edgeId)
  return r["cliSettings"]["remoteAccess"]


def enableRemoteAccess(edgeId):
  return nsxPost("/api/4.0/edges/" + edgeId + "cliSettings?enable=True")

def disableRemoteAccess(edgeId):
  return nsxPost("/api/4.0/edges/" + edgeId + "cliSettings?enable=False")




