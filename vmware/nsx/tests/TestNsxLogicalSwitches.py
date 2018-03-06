# tests/TestNsxLogicalSwitches.py
import unittest
import sys
sys.path.append("../utils/nsx/")
from logicalswitch import *


class NsxLogicalSwitchCreateDeleteTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_createLogicalSwitch(self):
        tzone = "GLOBAL-TZ-LAB"
        name = "LS-TEST"
        controlPlaneMode = "HYBRID_MODE"

        response = createLogicalSwitch(tzone, name, controlPlaneMode=controlPlaneMode)

        self.assertEqual(str(response), "<Response [201]>")

    def test_deleteLogicalSwitch(self):
        name = "LS-TEST"
        tzone = "GLOBAL-TZ-LAB"

        response = deleteLogicalSwitchByName(name, tzone)

        self.assertEqual(str(response), "<Response [200]>")


class NsxLogicalSwitchesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tzone = "GLOBAL-TZ-LAB"
        name = "LS-TEST"
        controlPlaneMode = "HYBRID_MODE"
        createLogicalSwitch(tzone, name, controlPlaneMode=controlPlaneMode)
        
    @classmethod
    def tearDownClass(cls):
        name = "LS-TEST-NEW"
        tzone = "GLOBAL-TZ-LAB"
        deleteLogicalSwitchByName(name, tzone)

    def test_getLogicalSwitchIdByName(self):
        ls_name = "LS-TEST"
        tzone = "GLOBAL-TZ-LAB"
        vw_name, vw_id = getLogicalSwitchIdByName(ls_name, tzone)

        self.assertEqual(ls_name, vw_name)
        self.assertTrue(vw_id is not None)

    def test_updateLogicalSwitch(self):
        ls_name = "LS-TEST"
        tzone = "GLOBAL-TZ-LAB"

        ls_newName = "LS-TEST-NEW"

        updateLogicalSwitchByName(ls_name, tzone, ls_newName)

        vw_name, vw_id = getLogicalSwitchIdByName(ls_newName, tzone)

        self.assertEqual(ls_newName, vw_name)
        self.assertTrue(vw_id is not None)


    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxLogicalSwitchCreateDeleteTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxLogicalSwitchesTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
