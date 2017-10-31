# tests/TestNsxEdges.py
import unittest
import sys
sys.path.append("../utils/nsx/")
from edge import *


class NsxEdgeTestCase(unittest.TestCase):
    def __init__(self):
        self.edgeId = ""

#todo create Edge
    def setUp(self):
        #self.widget = Widget('The widget')
        #create NSX Edge
        pass

    def tearDown(self):
        # self.widget.dispose()
        # self.widget = None
        pass

    def test_createNsxEdge(self):
        #todo save edgeId at class level 
        datacenterMoid = "datacenter-2"
        name = "test-edge"
        applianceSize = "xlarge"
        resourcePoolId = "resgroup-457"
        datastoreId = "datastore-16"
        index = "0"
        vnicName = "uplink"
        vnicType = "Uplink"
        portgroupId = "dvportgroup-450"
        primaryAddress = "192.168.0.1"
        subnetMask = "255.255.255.0"
        mtu = "1500"
        isConnected = "true"
        user = "admin"
        password = "T3stC@s3NSx"
        remoteAccess = "true"


        createNsxEdge(datacenterMoid,
               name,
               "",
               applianceSize,
               resourcePoolId,
               datastoreId,
               index,
               vnicName,
               vnicType,
               portgroupId,
               primaryAddress,
               subnetMask,
               mtu,
               isConnected,
               user,
               password,
               remoteAccess)

        pass

    def test_addNic(self):
        #some
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













    def test_deleteNsxEdge(self):
        pass



if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(NsxEdgeTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
