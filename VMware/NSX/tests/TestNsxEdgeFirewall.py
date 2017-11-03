# tests/TestNsxEdges.py
import unittest
import sys
sys.path.append("../utils/nsx/")
sys.path.append("../utils/common/")
from edge import *
from edge_firewall import *
from commonfunctions import *



class NsxEdgeCreateDeleteRuleTestCase(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    jinja_vars = {"datacenterMoid" : 'datacenter-2',
                  "name" : 'Edge-Test',
                  "description" : None,
                  "appliances" : {"applianceSize" : 'xlarge',
                                  "appliance" : {"resourcePoolId" : "resgroup-457",
                                                 "datastoreId" : "datastore-16"
                                                }},
                  "vnics" : [{"index" : "0",
                              "name" : "uplink",
                              "type" : "Uplink",
                              "portgroupId" : "dvportgroup-450",
                              "primaryAddress" : "192.168.0.1",
                              "subnetMask" : "255.255.255.0",
                              "mtu" : "1500",
                              "isConnected" : "true"
                             }],
                  "cliSettings" : {"userName" : "admin",
                                   "password" : "T3stC@s3NSx!",
                                   "remoteAccess" : "true"}
                  }

    createNsxEdge(jinja_vars)

  @classmethod
  def tearDownClass(cls):
    deleteNsxEdgeByName('Edge-Test')

  def test_createRule(self):
    jinja_vars = {'firewallRules' : [{'ruleTag' : 'test-tag',
                                    'name' : 'test-rule',
                                    'source' : {'ipAddress' : '100.64.0.1'},
                                    'destination' :  {'ipAddress' : '100.64.1.1'},
                                    'application' : {'service' : {'protocol' : "any",
                                                                  'port' : "any",
                                                                  'sourcePort' : "any"
                                                                  }
                                                    },
                                    'action' : 'accept',
                                    'enabled' : 'true',
                                    'description' : 'test' }]}
               
                   

    r, data = createRule("Edge-Test", jinja_vars)
    print(data)
    self.assertEqual(r.status_code, 200)

  def test_delete(self):
    r = deleteRule('Edge-Test', 'test-rule')
    self.assertEqual(r.status_code, 200)  


class NsxEdgeFirewallTestCase(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    jinja_vars = {"datacenterMoid" : 'datacenter-2',
              "name" : 'Edge-Test',
              "description" : None,
              "appliances" : {"applianceSize" : 'xlarge',
                              "appliance" : {"resourcePoolId" : "resgroup-457",
                                             "datastoreId" : "datastore-16"
                                            }},
              "vnics" : [{"index" : "0",
                          "name" : "uplink",
                          "type" : "Uplink",
                          "portgroupId" : "dvportgroup-450",
                          "primaryAddress" : "192.168.0.1",
                          "subnetMask" : "255.255.255.0",
                          "mtu" : "1500",
                          "isConnected" : "true"
                         }],
              "cliSettings" : {"userName" : "admin",
                               "password" : "T3stC@s3NSx!",
                               "remoteAccess" : "true"}
              }

    jinja_vars = removeEmptyParams(jinja_vars)

    createNsxEdge(jinja_vars)

    jinja_vars = {'firewallRule': {'ruleTag' : '88',
                           'name' : 'test-rule',
                           'source' : {'ipAddress' : '100.64.0.1',
                                       'groupingObjectId' : None,
                                       'vnicGroupId' : None
                                      },
                           'destination' :  {'ipAddress' : '100.64.1.1',
                                            'groupingObjectId' : None,
                                            'vnicGroupId' : None
                                            },
                            'application' : {'applicationId' : None,
                                             'service' : {'protocol' : None,
                                                          'port' : None,
                                                          'sourcePort' : None
                                                          }
                                            },
                            'matchTranslated' : None,
                            'direction' : None,
                            'action' : None,
                            'enabled' : None,
                            'loggingEnabled' : None,
                            'description' : None                             
                          }
          }

    jinja_vars = removeEmptyParams(jinja_vars)

    createRule("Edge-Test", jinja_vars)

  @classmethod
  def tearDownClass(cls):
    deleteRule('Edge-Test', 'test-rule')


    def test_updateGlobalConfig(self):
        jinja_vars = {'udpTimeOut' : "15"}

        r = updateGlobalConfig(jinja_vars)
        self.assertEqual(r.status_code, 200)

    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxEdgeCreateDeleteRuleTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxEdgeFirewallTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

