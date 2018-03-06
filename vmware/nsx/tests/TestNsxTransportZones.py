# tests/TestNsxLogicalSwitches.py
import unittest
import sys
sys.path.append("../utils/nsx/")
from transportzone import *
from pprint import pprint


class NsxTransportZoneCreateDeleteTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_createTransportZone(self):
        name = "TZ-TEST"
        clusters = [{'objectId' : 'domain-c444'}]
        description = "Transport Zone Create Test"
        controlPlaneMode = "HYBRID_MODE"

        response = createTz(name, clusters, description, controlPlaneMode)
        self.assertEqual("<Response [201]>", str(response))

    def test_deleteTransportZone(self):
        name = "TZ-TEST"
        response = deleteTzByName(name)
        self.assertEqual("<Response [200]>", str(response))
        


class NsxTransportZoneTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        name = "TZ-TEST"
        clusters = [{'objectId' : 'domain-c444'}]
        description = "Transport Zone Create Test"
        controlPlaneMode = "HYBRID_MODE"

        createTz(name, clusters, description, controlPlaneMode)

    @classmethod
    def tearDownClass(cls):
        name = "TZ-TEST-NEW"
        deleteTzByName(name)

    def test_getAllTransportZones(self):
        tzones = getAllTzId()
        self.assertTrue(tzones is not None)
    
    def test_getTransportZoneByName(self):
        name = "TZ-TEST"

        tzName, tzId = getTzIdByName(name)
        self.assertEqual(name, tzName)
        self.assertTrue(tzId is not None)

    @unittest.skip("")
    def test_getTransportZoneById(self):
        pass

    def test_updateTransportZone(self):
        name = "TZ-TEST"
        newName = "TZ-TEST-NEW"
        clusters = [{'objectId' : 'domain-c444'}]
       
        updateTzByName(name, clusters, newName)

        tzName, tzId = getTzIdByName(newName)
        self.assertEqual(tzName, newName)

  
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxTransportZoneCreateDeleteTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxTransportZoneTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

