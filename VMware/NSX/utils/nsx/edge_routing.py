import sys
sys.path.append("../utils/common/")

from nsx_rest import *
from jinja import render

import json

# BGP_ROUTING
# TODO: definir que parametros de bgp se quieren tocar
def getNsxEdgeBGP(edgeId):
	r = nsxGet("/api/4.0/edges/" + edgeId + "/routing/config/bgp")
	return json.loads(r)

def updateNsxEdgeBGP(edgeId, jinja_vars):
	dir = os.path.dirname(__file__)
	nsx_bgp_xml = os.path.join(dir, '../../templates/edge_routing/nsx_edge_routing_bgp.j2')
	data = render(nsx_bgp_xml, jinja_vars) 

	return nsxPost("/api/4.0/edges/" + edgeId + "/routing/config/bgp", data)

def deleteNsxEdgeBGP(edgeId):
	return nsxDelete("/api/4.0/edges/" + edgeId + "/routing/config/bgp")

# OSPF_ROUTING
# TODO: definir que parametros de ospf se quieren tocar
def getNsxEdgeOSPF(edgeId):
	r = nsxGet("/api/4.0/edges/" + edgeId + "/routing/config/ospf")
	return json.loads(r)

def updateNsxEdgeOSPF(edgeId, jinja_vars):
	dir = os.path.dirname(__file__)
	nsx_ospf_xml = os.path.join(dir, '../../templates/edge_routing/nsx_edge_routing_ospf.j2')
	data = render(nsx_ospf_xml, jinja_vars) 

	return nsxPost("/api/4.0/edges/" + edgeId + "/routing/config/ospf", data)

def deleteNsxEdgeOSPF(edgeId):
	return nsxDelete("/api/4.0/edges/" + edgeId + "/routing/config/ospf")

# STATIC_ROUTING
def getNsxEdgeStatic(edgeId):
	r = nsxGet("/api/4.0/edges/" + edgeId + "/routing/config/static")
	return json.loads(r)

def updateNsxEdgeStatic(edgeId, jinja_vars):
	dir = os.path.dirname(__file__)
	nsx_static_xml = os.path.join(dir, '../../templates/edge_routing/nsx_edge_routing_static.j2')
	data = render(nsx_static_xml, jinja_vars) 

	return nsxPost("/api/4.0/edges/" + edgeId + "/routing/config/static", data)

def deleteNsxEdgeStatic(edgeId):
	return nsxDelete("/api/4.0/edges/" + edgeId + "/routing/config/static")

def NsxEdgeAddStaticRoute(edgeId,
						  description,
						  vnic,
						  network,
						  nextHop,
						  mtu,
						  defaultRouteDescription,
						  defaultRouteVnic,
						  gatewayAddress,
						  defaultRouteMtu):

	jinja_vars = {'staticRouting' : {'staticRoutes' : {'route' : {'description' : description,
																  'vnic' : vnic,
																  'network' : network,
																  'nextHop' : nextHop,
																  'mtu' : mtu}},
									 'defaultRoute' : {'description': defaultRouteDescription,
									 				   'vnic' : defaultRouteVnic,
									 				   'gatewayAddress' : gatewayAddress,
									 				   'mtu' : defaultRouteMtu}}}

	return updateNsxEdgeStatic(edgeId, jinja_vars)



