#!/usr/bin/python

import logging
import os
import unittest

from model_srk import SRK

# --- logging setup ---
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])
log.setLevel(logging.DEBUG)

model = None

def setUpModule():
    global model
    model = SRK('SRK_Test_Modell', 'mappings_srk', 2, 22, logger=log)
    return

def tearDownModule():
    global model
    return

# @unittest.skip("Skipping Test01")
class Test01(unittest.TestCase):
    
    def setUp(self):
        global model
        self.model = model

    def test_constructor(self):
        self.assertIsNotNone(self.model)

@unittest.skip("Skipping Test02")
class Test02(unittest.TestCase):
    
    def setUp(self):
        global model
        self.model = model
        

    def test_model_results(self):
        self.model.calc_model_results()
       

@unittest.skip("Skipping Test03")
class Test03(unittest.TestCase):
    
    def setUp(self):
        global model
        self.model = model
        

    def test_model_results(self):
        res, exp_res , model_res = self.model.check_possible_calculations()
        self.assertIsNotNone(exp_res)
        self.assertIsNotNone(model_res)
        self.assertIsNotNone(res)

# @unittest.skip("Skipping Test04")
class Test04(unittest.TestCase):
    
    def setUp(self):
        global model
        self.model = model
        

    def test_sys_diag(self):

        # create diags again if true
        self.model.delete_diags = False

        system = ['CARBON DISULFIDE', 'ACETONE']
        self.model.create_system_diags(system)

        system = ['WATER', 'ACETONE']
        self.model.create_system_diags(system)

        system = ['CARBON DIOXIDE', 'ETHANE']
        self.model.create_system_diags(system)
        
        system = ['CHLORODIFLUOROMETHANE','CARBON DIOXIDE']
        self.model.create_system_diags(system)
        
        system = ['ETHANE','PROPANE']
        self.model.create_system_diags(system)


# @unittest.skip("Skipping Test05")
class Test05(unittest.TestCase):
    
    def setUp(self):
        global model
        self.model = model
        

    def test_diag(self):
        
        # create diags again if true
        self.model.delete_diags = False

        self.model.create_diags()


@unittest.skip("Skipping Test06")
class Test06(unittest.TestCase):
    
    def setUp(self):
        global model
        self.model = model
        

    def test_system_results(self):

        res = {}

        system = ['ACETONE', 'N-PENTANE']

        sys_file_name = '_'.join(system) + '.json'


        res = self.model.calc_system_results(system)
        if res != {}:
            self.model.write_results(sys_file_name, res)

        self.model.create_system_diags(system)

    
@unittest.skip("Skipping Test07")
class Test07(unittest.TestCase):
    
    def setUp(self):
        global model
        self.model = model
        

    def test_model_backup(self):
        self.model.do_model_backup()


if __name__ == '__main__':
    unittest.main(verbosity=2)