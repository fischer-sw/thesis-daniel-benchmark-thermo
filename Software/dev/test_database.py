#!/usr/bin/python

import logging
import os
import sys
import re
import unittest

from database import Database

# --- logging setup ---
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])
log.setLevel(logging.INFO)

db = None

def setUpModule():
    global db
    db = Database(os.path.join(sys.path[0],'..', '..', 'Daten', 'ie0c01734_si_001.xlsx'), os.path.join(sys.path[0],'..', '..', 'Datenbank', 'Experimente'), logger=log)
    return

def tearDownModule():
    global db
    return

@unittest.skip("Skipping Test01")
class Test01(unittest.TestCase):

    def setUp(self):
        global db
        self.db = db

    def test_constructor(self):
        self.db = db
        self.assertIsNotNone(self.db)
        self.assertIsNotNone(self.db.sheets)
        self.assertGreater(len(self.db.sheets), 0)

@unittest.skip("Skipping Test02")
class Test02(unittest.TestCase):

    def setUp(self):
        global db
        self.db = db

    def test_systems(self):
        self.assertIsNotNone(self.db.systems)
        self.assertGreater(len(self.db.systems), 0)
        val = list(self.db.systems.values())[0]
        self.assertTrue('BAC' in val.keys())
        self.assertTrue('sheet' in val.keys())

@unittest.skip("Skipping Test03")
class Test03(unittest.TestCase):

    def setUp(self):
        global db
        self.db = db

    def test_sheet1(self):
        comp1 = '2-METHYL-2-PROPANOL'
        comp2 = '1-BUTANOL'
        self.db.parse_sheet((comp1, comp2))
        self.db.write_sheet((comp1, comp2))
        self.assertTrue(comp1 in self.db.components.keys())
        self.assertTrue('CAS' in self.db.components[comp1].keys())
        self.assertEqual(self.db.components[comp1]['CAS'], '75-65-0')

    def test_sheet2(self):
        comp1 = 'NITROGEN'
        comp2 = 'ETHANE'
        self.db.parse_sheet((comp1, comp2))
        self.db.write_sheet((comp1, comp2))
        self.assertTrue(comp1 in self.db.components.keys())
        self.assertTrue('CAS' in self.db.components[comp1].keys())
        self.assertEqual(self.db.components[comp1]['CAS'], '7727-37-9')

    def test_sheet3(self):
        comp1 = 'WATER'
        comp2 = 'ACETONITRILE'
        self.db.parse_sheet((comp1, comp2))
        self.db.write_sheet((comp1, comp2))
        self.assertTrue(comp1 in self.db.components.keys())
        self.assertTrue('CAS' in self.db.components[comp1].keys())
        self.assertEqual(self.db.components[comp1]['CAS'], '7732-18-5')

    def test_sheet4(self):
        comp1 = 'ETHANOL'
        comp2 = 'BENZENE'
        self.db.parse_sheet((comp1, comp2))
        self.db.write_sheet((comp1, comp2))
        self.assertTrue(comp1 in self.db.components.keys())
        self.assertTrue('CAS' in self.db.components[comp1].keys())
        self.assertEqual(self.db.components[comp1]['CAS'], '64-17-5')

@unittest.skip("Skipping Test04")
class Test04(unittest.TestCase):

    def setUp(self):
        global db
        self.db = db

    def test_sheets(self):
        self.db.parse_sheets()

#@unittest.skip("Skipping Test05")
class Test05(unittest.TestCase):

    def setUp(self):
        global db
        self.db = db

    def test_sheets(self):
        self.assertIsNotNone(self.db.get_param_systems('Azeotropic point',list(range(10))))

if __name__ == '__main__':
    unittest.main(verbosity=2)
