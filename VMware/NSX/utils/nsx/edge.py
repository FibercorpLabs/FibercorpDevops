import sys
sys.path.append("../utils/common/")
sys.path.append("../common/")

from nsx_rest import *
from jinja import render

import json

from pprint import pprint

# READ_NSX_EDGE

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

def getNsxEdgeByName(edge_name):
	edgeId = getNsxEdgeIdByName(edge_name)

	return getNsxEdge(edgeId)

def getNsxEdge(edgeId):
	r = nsxGet("/api/4.0/edges/" + edgeId)
	r_dict = json.loads(r)
	return r_dict

# NSX_EDGE_CREATION_DELETION
def createNsxEdge(jinja_vars):
	dir = os.path.dirname(__file__)
	nsx_edge_xml = os.path.join(dir, '../../templates/edge/nsx_edge_create.j2')
	data = render(nsx_edge_xml, jinja_vars) 
  
	return nsxPost("/api/4.0/edges", data)

def deleteNsxEdgeById(edgeId):
	return nsxDelete("/api/4.0/edges/" + edgeId)

def deleteNsxEdgeByName(edge_name):
	edgeId = getNsxEdgeIdByName(edge_name)
	return deleteNsxEdgeById(edgeId)

# NSX_EDGE_UPDATE
def updateNsxEdge(edgeId, jinja_vars):
	data = json.dumps(jinja_vars)
	return nsxPutAsJson("/api/4.0/edges/" + edgeId, data)

def NsxEdgeRename(edgeId, name):
	jinja_vars = getNsxEdge(edgeId)
	jinja_vars['name'] = name

	return updateNsxEdge(edgeId, jinja_vars)

def NsxEdgeResize(edgeId, applianceSize):
	jinja_vars = getNsxEdge(edgeId)
	jinja_vars['appliances']['applianceSize'] = applianceSize
	data = json.dumps(jinja_vars)

	return updateNsxEdge(edgeId, jinja_vars)

# TODO: definir que parametros se quiere tocar
def NsxEdgeAddVnic(edgeId, index, type, portgroupId, primaryAddress, secondaryAddress, mtu, isConnected):
	jinja_vars = {}

	return updateNsxEdge(edgeId, jinja_vars)

# CLI_SETTINGS

def getCliSettings(edgeId):
	r = getNsxEdge(edgeId)
	return r['cliSettings']

def updateCliSettings(edgeId, query_params):
	data = json.dumps(query_params)
	return nsxPutAsJson("/api/4.0/edges/" + edgeId + "/clisettings", data)

def changeUserAndPassword(edgeId, new_user, new_password):
	query_params = getCliSettings(edgeId)
	query_params['userName'] = new_user
	query_params['password'] = new_password

	return updateCliSettings(edgeId, query_params)

def updateSshLoginBannerText(edgeId, banner):
	query_params = getCliSettings(edgeId)
	query_params['sshLoginBannerText'] = banner
	
	return updateCliSettings(edgeId, query_params)

def getRemoteAccessStatus(edgeId):
	clisettings = getCliSettings(edgeId)
		
	return clisettings['remoteAccess']


def enableRemoteAccess(edgeId):
	return nsxPost("/api/4.0/edges/" + edgeId + "/cliremoteaccess?enable=True","")


def disableRemoteAccess(edgeId):
	return nsxPost("/api/4.0/edges/" + edgeId + "/cliremoteaccess?enable=False", "")

# DNS_CLIENT
def getDnsClient(edgeId):
	r = nsxGet("/api/4.0/edges/" + edgeId + "/dnsclient")
	return json.loads(r)

def updateDnsClient(edgeId, jinja_vars):
	dir = os.path.dirname(__file__)
	nsx_dns_xml = os.path.join(dir, '../../templates/edge/nsx_edge_dnsclient.j2')
	data = render(nsx_dns_xml, jinja_vars) 

	return nsxPost("/api/4.0/edges/" + edgeId + "/dnsclient", data)

def updatePrimaryDns(edgeId, primaryDns):
	jinja_vars = {'dnsClient' : {'primaryDns' : primaryDns}}

	return updateDnsClient(edgeId, jinja_vars)

def updateSecondaryDns(edgeId, secondaryDns, domainName):
	jinja_vars = {'dnsClient' : {'secondaryDns' : secondaryDns, 'domainName' : domainName}}

	return updateDnsClient(edgeId, jinja_vars)

# NAT
def getNsxEdgeNat(edgeId):
	r = nsxGet("/api/4.0/edges/" + edgeId + "/nat/config")
	return json.loads(r)

def updateNsxEdgeNat(edgeId, jinja_vars):
	dir = os.path.dirname(__file__)
	nsx_nat_xml = os.path.join(dir, '../../templates/edge_routing/nsx_edge_routing_nat.j2')
	data = render(nsx_nat_xml, jinja_vars)

	return nsxPost("/api/4.0/edges/" + edgeId + "/nat/config", data)

def deleteNsxEdgeNat(edgeId):
	return nsxDelete("/api/4.0/edges/" + edgeId + "/nat/config")

# TODO: 
def createNatRule(edgeId):
	jinja_vars = {}
	return updateNsxEdgeNat(edgeId, jinja_vars)

