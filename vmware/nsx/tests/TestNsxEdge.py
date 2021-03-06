# tests/TestNsxEdges.py
import unittest
import sys
sys.path.append("../utils/nsx/")
from edge import *

class NsxEdgeCreateDeleteTestCase(unittest.TestCase):
    def test_createNsxEdge(self):
        jinja_vars = {  "datacenterMoid" : 'datacenter-2',
                        "name" : 'Edge-Test',
                        "description" : "",
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
        name = "Edge-Test"
        self.assertEqual(deleteNsxEdgeByName(name).status_code, 204)



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
        deleteNsxEdgeByName("Edge-Test")

    @unittest.skip("")
    def test_getNsxEdgeByName(self):
        name = "Edge-Test"
        r_config = getNsxEdgeByName(name)
        self.assertNotEqual(None, r_config)

    @unittest.skip("")
    def test_NsxEdgeRename(self):
        edgeId = getNsxEdgeIdByName("Edge-Test")
        r = NsxEdgeRename(edgeId, "Edge-Test-NewName")
        self.assertEqual(r.status_code, 204)
        r = NsxEdgeRename(edgeId, "Edge-Test")
        self.assertEqual(r.status_code, 204)

    @unittest.skip("")
    def test_NsxEdgeResize(self):
        edgeId = getNsxEdgeIdByName("Edge-Test")
        r = NsxEdgeResize(edgeId, "large")
        self.assertEqual(r.status_code, 204)

    # @unittest.skip("")
    def test_changeUserAndPassword(self):
        edgeId = getNsxEdgeIdByName("Edge-Test")
        r = changeUserAndPassword(edgeId, "josemaria", "T3stC@s3NSx!")
        self.assertEqual(r.status_code, 204)

    # @unittest.skip("")
    def test_updateSshLoginBannerText(self):
        edgeId = getNsxEdgeIdByName("Edge-Test")
        r = updateSshLoginBannerText(edgeId, "\n***************************************************************************\nNOTICE TO USERS\n\n\nThis computer system is the private property of its owner, whether\nindividual, corporate or government.  It is for authorized use only.\nUsers (authorized or unauthorized) have no explicit or implicit\nexpectation of privacy.\n\nAny or all uses of this system and all files on this system may be\nintercepted, monitored, recorded, copied, audited, inspected, and\ndisclosed to your employer, to authorized site, government, and law\nenforcement personnel, as well as authorized officials of government\nagencies, both domestic and foreign.\n\nBy using this system, the user consents to such interception, monitoring,\nrecording, copying, auditing, inspection, and disclosure at the\ndiscretion of such personnel or officials.  Unauthorized or improper use\nof this system may result in civil and criminal penalties and\nadministrative or disciplinary action, as appropriate. By continuing to\nuse this system you indicate your awareness of and consent to these terms\nand conditions of use. LOG OFF IMMEDIATELY if you do not agree to the\nconditions stated in this warning.\n\n****************************************************************************")
        self.assertEqual(r.status_code, 204)

    @unittest.skip("")
    def test_getRemoteAccessStatus(self):
        edgeId = getNsxEdgeIdByName("Edge-Test")
        r = getRemoteAccessStatus(edgeId)
        self.assertEqual((r == True or r == False))

    @unittest.skip("")
    def test_enableRemoteAccess(self):
        edgeId = getNsxEdgeIdByName("Edge-Test")
        r = enableRemoteAccess(edgeId)
        self.assertEqual(r.status_code, 204)

    @unittest.skip("")
    def test_disableRemoteAccess(self):
        edgeId = getNsxEdgeIdByName("Edge-Test")
        r = disableRemoteAccess(edgeId)
        self.assertEqual(r.status_code, 204)

    @unittest.skip("")
    def test_updatePrimaryDns(self):
        edgeId = getNsxEdgeIdByName("Edge-Test")
        r = updatePrimaryDns(edgeId, "8.8.8.8")
        self.assertEqual(r.status_code, 204)

    @unittest.skip("")
    def test_updateSecondaryDns(self):
        edgeId = getNsxEdgeIdByName("Edge-Test")
        r = updateSecondaryDns(edgeId, "8.8.4.4", "dns.google.com")
        self.assertEqual(r.status_code, 204)

    @unittest.skip("")
    def test_createNatRule(self):
        pass

    @unittest.skip("")
    def test_NsxEdgeAddVnic(self):
        pass


    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    # suite = unittest.TestLoader().loadTestsFromTestCase(NsxEdgeCreateDeleteTestCase)
    # unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxEdgeTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
