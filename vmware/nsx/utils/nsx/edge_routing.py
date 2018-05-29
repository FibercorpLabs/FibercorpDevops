import sys
import json

# from pprint import pprint
# sys.path.append("../common")
# from jinja import render
# from nsx_rest import *



from pprint import pprint
from .nsx_rest import *
from ..common.jinja import render

# BGP_ROUTING
# TODO: definir que parametros de bgp se quieren tocar
def get_nsx_edge_bgp(edgeId):
	r = nsxGet("/api/4.0/edges/" + edgeId + "/routing/config/bgp")
	return json.loads(r)

def update_nsx_edge_bgp(edgeId, jinja_vars):
	dir = os.path.dirname(__file__)
	nsx_bgp_xml = os.path.join(dir, '../../templates/edge_routing/nsx_edge_routing_bgp.j2')
	data = render(nsx_bgp_xml, jinja_vars) 

	return nsxPost("/api/4.0/edges/" + edgeId + "/routing/config/bgp", data)

def delete_nsx_edge_bgp(edgeId):
	return nsxDelete("/api/4.0/edges/" + edgeId + "/routing/config/bgp")

# OSPF_ROUTING
# TODO: definir que parametros de ospf se quieren tocar
def get_nsx_edge_ospf(edgeId):
	r = nsxGet("/api/4.0/edges/" + edgeId + "/routing/config/ospf")
	return json.loads(r)

def update_nsx_edge_ospf(edgeId, jinja_vars):
	dir = os.path.dirname(__file__)
	nsx_ospf_xml = os.path.join(dir, '../../templates/edge_routing/nsx_edge_routing_ospf.j2')
	data = render(nsx_ospf_xml, jinja_vars) 

	return nsxPost("/api/4.0/edges/" + edgeId + "/routing/config/ospf", data)

def delete_nsx_edge_ospf(edgeId):
	return nsxDelete("/api/4.0/edges/" + edgeId + "/routing/config/ospf")

# STATIC_ROUTING
def get_nsx_edge_static(edgeId):
	r = nsxGet("/api/4.0/edges/" + edgeId + "/routing/config/static")
	return json.loads(r)

def update_nsx_edge_static(edgeId, jinja_vars):
	dir = os.path.dirname(__file__)
	nsx_static_xml = os.path.join(dir, '../../templates/edge_routing/nsx_edge_routing_static.j2')
	data = render(nsx_static_xml, jinja_vars) 

	return nsxPut("/api/4.0/edges/" + edgeId + "/routing/config/static", data)

def update_nsx_edge_static_json(edgeId, jinja_vars):
	dir = os.path.dirname(__file__)
	nsx_static_json = os.path.join(dir, '../../templates/edge_routing/nsx_edge_routing_static.j2')
	data = render(nsx_static_json, jinja_vars) 

	return nsxPut("/api/4.0/edges/" + edgeId + "/routing/config/static", data, "json")

def delete_nsx_edge_static(edgeId):
	return nsxDelete("/api/4.0/edges/" + edgeId + "/routing/config/static")

def nsx_edge_add_static_route(edgeId, vnic, network, nextHop, mtu="1500", description="description"):

	jinja_vars = {'staticRouting' : {'staticRoutes' : {'route' : {'description' : description,
																  'vnic' : vnic,
																  'network' : network,
																  'nextHop' : nextHop,
																  'mtu' : mtu}}}}

	return update_nsx_edge_static(edgeId, jinja_vars)


def nsx_edge_add_gateway(edgeId, defaultRouteVnic, gatewayAddress, defaultRouteMtu, defaultRouteDescription="description"):
	jinja_vars = {'defaultRoute' : {'description': defaultRouteDescription,
								 				   'vnic' : defaultRouteVnic,
								 				   'gatewayAddress' : gatewayAddress,
								 				   'mtu' : defaultRouteMtu}}

	return update_nsx_edge_static_json(edgeId, jinja_vars)