#!/usr/bin/python

import logging
import os
import sys
import unittest
import json

from compare import Comparison

# --- logging setup ---
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])
log.setLevel(logging.DEBUG)

comp = None

def setUpModule():
    global comp
    comp = Comparison(os.path.join(sys.path[0],'..', '..', 'Datenbank'), os.path.join(sys.path[0],'..', '..', 'Ergebnisse'), 'Test_Modell', 'Test', logger=log)
    return

def tearDownModule():

    global comp
    return

@unittest.skip("Skipping Test01")
class Test01(unittest.TestCase):

    def setUp(self):
        global comp
        self.comp = comp

    def test_constructor(self):
        self.comp = comp
        self.assertIsNotNone(self.comp)
        self.assertIsNotNone(self.comp.model)

@unittest.skip("Skipping Test02")
class Test02(unittest.TestCase):

    def setUp(self):
        global comp
        self.comp = comp

    def test_create_sys_results(self):
        erg = self.comp.create_sys_results()
        self.assertIsNotNone(erg)
        self.comp.write_results_file(erg)

        

@unittest.skip("Skipping Test03")
class Test03(unittest.TestCase):

    def setUp(self):
        global comp
        self.comp = comp

    def test_create_bac_results(self):
        erg = self.comp.calc_bac_results()
        self.assertIsNotNone(erg["BAC1"]["group_res"]["mark_h_mix"])
        self.comp.write_results_file(erg)

@unittest.skip("Skipping Test04")
class Test04(unittest.TestCase):

    def setUp(self):
        global comp
        self.comp = comp

    def test_create_group_results(self):
        erg = self.comp.calc_group_results()
        self.assertIsNotNone(erg["class_res"]["mark_NA"])
        self.comp.write_results_file(erg)

# @unittest.skip("Skipping Test05")
class Test05(unittest.TestCase):

    def setUp(self):
        global comp
        self.comp = comp

    def test_create_model_results(self):
        erg = self.comp.calc_model_results()
        self.assertIsNotNone(erg["model_res"])
        self.comp.write_results_file(erg)

@unittest.skip("Skipping Test06")
class Test06(unittest.TestCase):

    def setUp(self):
        global comp
        self.comp = comp

    def test_system_results(self):

        res_path = os.path.join(self.comp.result_dir, self.comp.model, self.comp.test_name +'.json')
        path = os.path.join(sys.path[0],'..', '..', 'Datenbank', 'Modelle', self.comp.model)

        with open(res_path, 'r') as file:
            res = json.loads(file.read())

        system = 'WATER_n-BUTANE'

        erg = self.comp.calc_sys_results(system, res)
        self.assertIsNotNone(erg)
        


if __name__ == '__main__':
    unittest.main(verbosity=2)