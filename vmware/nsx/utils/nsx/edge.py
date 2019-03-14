from .nsx_rest import *
from ..common.jinja import render

# from nsx_rest import *

import json

from pprint import pprint

# READ_NSX_EDGE
def nsx_edge_get_all():
	r = nsxGet("/api/4.0/edges", "json")

	r_dict = json.loads(r)
	allEdges = r_dict['edgePage']['data']

	edges = {"edges" : []}

	for edge in allEdges:
		edges["edges"].append({'name' : edge['name'], 'id' : edge['id']})

	return edges

def nsx_edge_get_id_by_name(name):
	r = nsxGet("/api/4.0/edges", "json")

	r_dict = json.loads(r)
	
	allEdges = r_dict['edgePage']['data']

	for edge in allEdges:
		if edge['name'] == name:
			return edge['id']

	return ""

def nsx_edge_get_by_name(edge_name):
	edgeId = nsx_edge_get_id_by_name(edge_name)

	return nsx_edge_get_by_id(edgeId)

def nsx_edge_get_by_id(edgeId):
	r = nsxGet("/api/4.0/edges/" + edgeId, "json")
	r_dict = json.loads(r)
	return r_dict

# NSX_EDGE_CREATION_DELETION
def nsx_edge_create(jinja_vars):
	dir = os.path.dirname(__file__)
	nsx_edge_xml = os.path.join(dir, '../../templates/edge/nsx_edge_create.j2')
	data = render(nsx_edge_xml, jinja_vars) 
  	
	result= nsxPost("/api/4.0/edges", data, "xml")
	print (result)
	return result

def nsx_edge_delete_by_id(edgeId):
	return nsxDelete("/api/4.0/edges/" + edgeId, "xml")

def nsx_edge_delete_by_name(edge_name):
	edgeId = nsx_edge_get_id_by_name(edge_name)
	return nsx_edge_delete_by_id(edgeId)

# NSX_EDGE_UPDATE
def nsx_edge_update(edgeId, jinja_vars):
	data = json.dumps(jinja_vars)
	return nsxPut("/api/4.0/edges/" + edgeId, data, "xml")

def nsx_edge_rename(edgeId, name):
	jinja_vars = get_nsx_edge(edgeId)
	jinja_vars['name'] = name

	return update_nsx_edge(edgeId, jinja_vars)

def nsx_edge_resize(edgeId, applianceSize):
	jinja_vars = get_nsx_edge(edgeId)
	jinja_vars['appliances']['applianceSize'] = applianceSize
	data = json.dumps(jinja_vars)

	return update_nsx_edge(edgeId, jinja_vars)

# TODO: definir que parametros se quiere tocar
def nsx_edge_add_vnic(edgeId, index, type, portgroupId, primaryAddress, secondaryAddress, mtu, isConnected):
	jinja_vars = {}

	return nsx_edge_update(edgeId, jinja_vars)

# CLI_SETTINGS

def nsx_edge_get_cli_settings(edgeId):
	r = get_nsx_edge(edgeId)
	return r['cliSettings']

def nsx_edge_update_cli_settings(edgeId, query_params):
	data = json.dumps(query_params)
	return nsxPut("/api/4.0/edges/" + edgeId + "/clisettings", data, "xml")

def nsx_edge_set_user_and_password(edgeId, new_user, new_password):
	query_params = get_cli_settings(edgeId)
	query_params['userName'] = new_user
	query_params['password'] = new_password

	return update_cli_settings(edgeId, query_params)

def nsx_edge_set_ssh_login_banner(edgeId, banner):
	query_params = get_cli_settings(edgeId)
	query_params['sshLoginBannerText'] = banner
	
	return nsx_edge_update_cli_settings(edgeId, query_params)

def get_remote_access_status(edgeId):
	clisettings = nsx_edge_get_cli_settings(edgeId)
		
	return clisettings['remoteAccess']


def enable_remote_access(edgeId):
	return nsxPost("/api/4.0/edges/" + edgeId + "/cliremoteaccess?enable=True","", "xml")


def disable_remote_access(edgeId):
	return nsxPost("/api/4.0/edges/" + edgeId + "/cliremoteaccess?enable=False", "", "xml")

# DNS_CLIENT
def get_dns_client(edgeId):
	r = nsxGet("/api/4.0/edges/" + edgeId + "/dnsclient", "xml")
	return json.loads(r)

def update_dns_client(edgeId, jinja_vars):
	dir = os.path.dirname(__file__)
	nsx_dns_xml = os.path.join(dir, '../../templates/edge/nsx_edge_dnsclient.j2')
	data = render(nsx_dns_xml, jinja_vars) 

	return nsxPost("/api/4.0/edges/" + edgeId + "/dnsclient", data, "xml")

def update_primary_dns(edgeId, primaryDns):
	jinja_vars = {'dnsClient' : {'primaryDns' : primaryDns}}

	return update_dns_client(edgeId, jinja_vars)

def update_secondary_dns(edgeId, secondaryDns, domainName):
	jinja_vars = {'dnsClient' : {'secondaryDns' : secondaryDns, 'domainName' : domainName}}

	return update_dns_client(edgeId, jinja_vars)

# NAT
def get_nsx_edge_nat(edgeId):
	r = nsxGet("/api/4.0/edges/" + edgeId + "/nat/config", "xml")
	return json.loads(r)

def update_nsx_edge_nat(edgeId, jinja_vars):
	dir = os.path.dirname(__file__)
	nsx_nat_xml = os.path.join(dir, '../../templates/edge_routing/nsx_edge_routing_nat.j2')
	data = render(nsx_nat_xml, jinja_vars)

	return nsxPost("/api/4.0/edges/" + edgeId + "/nat/config", data, "xml")

def delete_nsx_edge_nat(edgeId):
	return nsxDelete("/api/4.0/edges/" + edgeId + "/nat/config", "xml")

# TODO: 
def create_nat_rule(edgeId):
	jinja_vars = {}
	return update_nsx_edge_nat(edgeId, jinja_vars)