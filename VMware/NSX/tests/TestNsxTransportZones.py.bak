# tests/TestNsxLogicalSwitches.py
import unittest
import sys
sys.path.append("../utils/nsx/")
from transportzone import *
from pprint import pprint

class NsxTransportZoneTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_01_getAllTransportZones(self):
        tzones = getAllTzId()
        self.assertTrue(tzones is not None)
    
    def test_02_getTransportZoneByName(self):
        name = "GLOBAL-TZ-LAB"

        tzName, tzId = getTzIdByName(name)
        self.assertEqual(name, tzName)
        self.assertTrue(tzId is not None)
        print tzName, tzId

    @unittest.skip("")
    def test_03_getTransportZoneById(self):
        pass

    def test_04_createTransportZone(self):
        name = "TZ-TEST"
        clusters = [{'objectId' : 'domain-c444'}]
        description = "Transport Zone Create Test"
        controlPlaneMode = "HYBRID_MODE"

        createTZ(name, clusters, description, controlPlaneMode)

        tzName, tzId = getTzIdByName(name)

        self.assertEqual(name, tzName)
        self.assertTrue(tzId is not None)  

    def test_05_updateTransportZone(self):
        name = "TZ-TEST"
        newName = "TZ-TEST-NEW"
        clusters = [{'objectId' : 'domain-c444'}]
       
        updateTzByName(name, clusters, newName)

        tzName, tzId = getTzIdByName(newName)
        self.assertEqual(tzName, newName)

    
    def test_06_deleteTransportZone(self):
        name = "TZ-TEST-NEW"
        deleteTzByName(name)

        tzName, tzId = getTzIdByName(name)
        
        self.assertEqual(tzName, None)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxTransportZoneTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
