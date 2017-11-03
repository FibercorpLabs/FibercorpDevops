# tests/TestNsxEdges.py
import unittest
import sys
sys.path.append("../utils/nsx/")
from edge import *
from edge_firewall import *



class NsxEdgeCreateRuleTestCase(unittest.TestCase):
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

    r = createRule("Edge-Test", jinja_vars)
    self.assertEqual(r.status_code, 200)

  def test_delete(self):
    r = deleteRule('Edge-Test', 'test-rule')
    self.assertEqual(r.status_code, 200)  


class NsxEdgeFirewallTestCase(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
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

    createRule("Edge-Test", jinja_vars)

  @classmethod
  def tearDownClass(cls):
    deleteRule('Edge-Test', 'test-rule')


  def test_updateGlobalConfig(self):
    


    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxEdgeCreateRuleTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxEdgeFirewallTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

