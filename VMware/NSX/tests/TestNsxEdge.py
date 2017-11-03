# tests/TestNsxEdges.py
import unittest
import sys
sys.path.append("../utils/nsx/")
from edge import *



class NsxEdgeCreateDeleteTestCase(unittest.TestCase):
    def test_createNsxEdge(self):
        jinja_vars = {  "datacenterMoid" : 'datacenter-2',
                        "name" : 'Edge-Test',
                        "description" : None,
                        "appliances" : {    "applianceSize" : 'xlarge',
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

        response = createNsxEdge(jinja_vars)

        self.assertEqual(response.status_code, 201)

    def test_deleteNsxEdge(self):
        name = "test-create-edge"
        self.assertEqual(deleteNsxEdge(getNsxEdgeIdByName(name)).status_code, 204)



class NsxEdgeTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        jinja_vars = {  "datacenterMoid" : 'datacenter-2',
                "name" : 'Edge-Test',
                "description" : None,
                "appliances" : {    "applianceSize" : 'xlarge',
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
        deleteNsxEdge(getNsxEdgeIdByName("class-edge-00"))


    def test_addNic(self):
        pass

    def test_deleteNic(self):
        pass

    def test_enableBGP(self):
        pass

    def test_configureRouterID(self):
        pass

    def test_enableRouting(self):
        pass

    def test_enableHA(self):
        pass

    def test_resizeEdge(self):
        pass

    def test_getNsxEdgeByName(self):
        name = "class-edge-00"
        response = deleteNsxEdge(getNsxEdgeIdByName(name))
        self.assertEqual(response.status_code, 200)




    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxEdgeCreateDeleteTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
