from nsx_rest import *
import json
import sys

sys.path.append("../utils/common/")
from jinja import render

from edge import *

from pprint import pprint


def getFirewallConfig(edge_name):
  edgeId = getNsxEdgeIdByName(edge_name)
  r =  nsxGet("/api/4.0/edges/"+ edgeId + "/firewall/config")

  return json.loads(r)

def getRuleIdByName(edge_name, rule_name):

  edgeConfig = getFirewallConfig(edge_name)

  firewallRules = edgeConfig['firewallRules']['firewallRules']

  for firewallRule in firewallRules:
    if firewallRule['name'] == rule_name:
      return firewallRule['ruleId']

  return None

def createRule(edge_name, jinja_vars):

  edgeId = getNsxEdgeIdByName(edge_name)

  dir = os.path.dirname(__file__)
  nsx_rules_xml = os.path.join(dir, '../../templates/edge_firewall/nsx_edge_firewall_rules.j2')
  data = render(nsx_rules_xml, jinja_vars) 

  return nsxPost("/api/4.0/edges/" + edgeId +"/firewall/config/rules", data), data


def updateGlobalConfig(edge_name, jinja_vars):

  edgeId = getNsxEdgeIdByName(edge_name)

  dir = os.path.dirname(__file__)
  nsx_globalconfig_xml = os.path.join(dir, '../../templates/edge_firewall/nsx_edge_firewall_globalconfig.j2')
  data = render(nsx_globalconfig_xml, jinja_vars) 

  return nsxPut("/api/4.0/edges/" + edgeId + "/firewall/config/global", data)

def updateDefaultPolicy(edge_name, jinja_vars):

  edgeId = getNsxEdgeIdByName(edge_name)

  dir = os.path.dirname(__file__)
  nsx_defaultpolicy_xml = os.path.join(dir, '../../templates/edge_firewall/nsx_edge_firewall_defaultpolicy.j2')
  data = render(nsx_defaultpolicy_xml, jinja_vars) 

  return nsxPut("/api/4.0/edges/" + edgeId + "/firewall/config/defaultpolicy", data)

def updateRule(edge_name, rule_name, jinja_vars):
  edgeId = getNsxEdgeIdByName(edge_name)
  ruleId = getRuleIdByName(edge_name, rule_name)

  dir = os.path.dirname(__file__)
  nsx_rule_xml = os.path.join(dir, '../../templates/edge_firewall/nsx_edge_firewall_rule.j2')
  data = render(nsx_rule_xml, jinja_vars) 

  return nsxPut("/api/4.0/edges/"+ edgeId + "/firewall/config/rules/" + ruleId, data)

def deleteRule(edge_name, rule_name):
  edgeId = getNsxEdgeIdByName(edge_name)
  ruleId = getRuleIdByName(edge_name, rule_name)

  return nsxDelete("/api/4.0/edges/"+ edgeId + "/firewall/config/rules/" + ruleId)


# pprint(getFirewallConfig("PGW01"))
# pprint(getRuleIdByName("PGW01", "firewall"))