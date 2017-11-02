# tests/TestNsxEdges.py
import unittest
import sys
sys.path.append("../utils/nsx/")
from edge import *
from edge_firewall import *



class NsxEdgeCreateRuleTestCase(unittest.TestCase):
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

    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxEdgeCreateRuleTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxEdgeFirewallTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

