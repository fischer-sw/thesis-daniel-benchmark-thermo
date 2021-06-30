#!/usr/bin/python

import logging
import os
import re
import sys
import unittest

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

    def test_create_results(self):
        erg = self.comp.create_results()
        self.assertIsNotNone(erg)
        self.comp.write_results_file(erg)

@unittest.skip("Skipping Test03")
class Test03(unittest.TestCase):

    def setUp(self):
        global comp
        self.comp = comp

    def test_sys_results(self):
        erg = self.comp.calc_sys_result('ETHANE_N-HEPTANE')
        self.comp.write_results_file(erg)
        self.assertIsNotNone(erg)
        erg = self.comp.calc_sys_result('METHANE_N-HEXANE')
        self.comp.write_results_file(erg)
        self.assertIsNotNone(erg)
        erg = self.comp.calc_sys_result('ETHANOL_BENZENE')
        self.comp.write_results_file(erg)
        self.assertIsNotNone(erg)



if __name__ == '__main__':
    unittest.main(verbosity=2)