# tests/TestNsxLogicalSwitches.py
import unittest



class NsxLogicalSwitchesTestCase(unittest.TestCase):
    def __init__(self):
        self.lsId = ""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_createLogicalSwitch(self):
        pass

    def test_getLogicalSwitch(self):
        pass

    def test_updateLogicalSwitch(self):
        pass
    
    def test_deleteLogicalSwitch(self):
        pass






if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxLogicalSwitchesTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
