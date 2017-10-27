# tests/TestNsxEdges.py
import unittest



class NsxEdgeTestCase(unittest.TestCase):

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
