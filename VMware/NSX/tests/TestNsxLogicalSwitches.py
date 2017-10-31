# tests/TestNsxLogicalSwitches.py
import unittest
import sys
sys.path.append("../utils/nsx/")
from logicalswitch import *


class NsxLogicalSwitchesTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_02_getLogicalSwitchIdByName(self):
        ls_name = 
        tzone = "GLOBAL-TZ-LAB"
        vw_name, vw_id = getLogicalSwitchIdByName(ls_name, tzone)

        self.assertEqual(ls_name, vw_name)
        self.asserTrue(vw_id is not None)

    def test_01_createLogicalSwitch(self):
        tzone = "GLOBAL-TZ-LAB"
        name = "LS-TEST"
        controlPlaneMode = "HYBRID_MODE"

        createLogicalSwitch(tzone, name, controlPlaneMode=controlPlaneMode)

        vw_name, vw_id = getLogicalSwitchIdByName(name, tzone)

        self.assertEqual(ls_name, vw_name)
        self.asserTrue(vw_id is not None)

    def test_03_updateLogicalSwitch(self):
        pass
    
    def test_04_deleteLogicalSwitch(self):
        pass



if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxLogicalSwitchesTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
