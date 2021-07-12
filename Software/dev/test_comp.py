#!/usr/bin/python

import logging
import os
import re
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

# @unittest.skip("Skipping Test01")
class Test01(unittest.TestCase):

    def setUp(self):
        global comp
        self.comp = comp

    def test_constructor(self):
        self.comp = comp
        self.assertIsNotNone(self.comp)
        self.assertIsNotNone(self.comp.model)

# @unittest.skip("Skipping Test03")
class Test03(unittest.TestCase):

    def setUp(self):
        global comp
        self.comp = comp

    def test_create_sys_results(self):
        erg = self.comp.create_sys_results()
        self.assertIsNotNone(erg)
        self.comp.write_results_file(erg)

# @unittest.skip("Skipping Test04")
class Test04(unittest.TestCase):

    def setUp(self):
        global comp
        self.comp = comp

    def test_create_bac_results(self):
        erg = self.comp.calc_bac_results()
        self.assertIsNotNone(erg["BAC1"]["group_res"]["mark_h_mix"])
        self.comp.write_results_file(erg)

    def test_create_group_results(self):
        erg = self.comp.calc_group_results()
        self.assertIsNotNone(erg["group_res"]["mark_NA"]["mark_h_mix"])
        self.comp.write_results_file(erg)

    def test_create_model_results(self):
        erg = self.comp.calc_model_results()
        self.assertIsNotNone(erg["model_res"]["mark_h_mix"])
        self.comp.write_results_file(erg)


if __name__ == '__main__':
    unittest.main(verbosity=2)