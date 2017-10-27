# tests/TestVC.py
import unittest



class VcenterTestCase(unittest.TestCase):
    def setUp(self):
        #self.widget = Widget('The widget')
        #create NSX Edge
        pass

    def tearDown(self):
        # self.widget.dispose()
        # self.widget = None
        pass

    def test_getPortgroupByName(self):
        #some
        pass






    # runTest defined on subclass
    #def runTest(self):
        #self do something
        #self.assertEqual(SOME REST RETURN, 200)






if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(VcenterTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
