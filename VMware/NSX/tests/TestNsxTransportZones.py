# tests/TestNsxLogicalSwitches.py
import unittest
import sys
sys.path.append("../utils/")
from transportzone import *
from pprint import pprint



class NsxTransportZoneTestCase(unittest.TestCase):
    def __init__(self):
        self.tzId = ""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_getAllTransportZones(self):
        tzones = getAllTZ()
        self.assertTrue(tzones is not None)
        pprint(tzones)

    
    def test_getTransportZoneByName(self):
        name = "GLOBAL-TZ-LAB"
        tzName, tzId = getTZ(name)
        self.assertEqual(name, tzName)
        self.assertTrue(tzId is not None)

    @unittest.skip("Skipped")
    def test_createTransportZone(self):
        pass


    @unittest.skip("Skipped")
    def test_updateTransportZone(self):
        pass

    @unittest.skip("Skipped")
    def test_deleteTransportZone(self):
        pass


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxLogicalSwitchesTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
