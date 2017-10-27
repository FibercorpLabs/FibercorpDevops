# tests/TestNsxLogicalSwitches.py
import unittest



class NsxLogicalSwitchesTestCase(unittest.TestCase):
    def setUp(self):
        #self.widget = Widget('The widget')
        #create NSX Edge
        pass

    def tearDown(self):
        # self.widget.dispose()
        # self.widget = None
        pass

    def test_getLogicalSwitch(self):
        #some
        pass

    def test_createLogicalSwitch(self):
        pass

    def test_deleteLogicalSwitch(self):
        pass

    def test_updateLogicalSwitch(self):
        pass






if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxLogicalSwitchesTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
