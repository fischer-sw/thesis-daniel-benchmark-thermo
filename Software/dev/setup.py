#!/usr/bin/python

import os
import sys
import zipfile
import subprocess
import unittest

import test_database
import test_model
import test_comp

def install_packages():

    # upgrade pip
    os.system("pip install --upgrade pip")
    os.system("pip install -r requirements.txt")

def setup_dirs(dirs):

    base_path = os.path.join(sys.path[0], '..','..')

    for element in dirs:

        path = os.path.join(base_path, element)
        
        if not os.path.isdir(path):
            os.mkdir(path)


def run_tests():

    path = os.path.join(sys.path[0], '..','..', 'Datenbank','Experimente')

    files = os.listdir(path)

    if len(files) == 0:
        database_tests = unittest.TestLoader().loadTestsFromModule(test_database)
        unittest.TextTestRunner(verbosity=2).run(database_tests)
    
    model_tests = unittest.TestLoader().loadTestsFromModule(test_model)
    unittest.TextTestRunner(verbosity=2).run(model_tests)

    comp_tests = unittest.TestLoader().loadTestsFromModule(test_comp)
    unittest.TextTestRunner(verbosity=2).run(comp_tests)
    
    

def unzip():
    
    base_path = os.path.join(sys.path[0], '..','..')
    dll_zip_path = os.path.join(sys.path[0], "TREND_FIT_DLL.zip")
    trend_path = os.path.join(sys.path[0],'..','..','TREND 4.0')


    if not os.path.isfile(os.path.join(sys.path[0],'TREND_FIT_DLL.dll')):

        with zipfile.ZipFile(dll_zip_path) as zip_file:
            zip_file.extractall(sys.path[0])


    if not os.path.isdir(trend_path):
        with zipfile.ZipFile(os.path.join(base_path, "TREND 4.0.zip")) as zip_file:
            zip_file.extractall(base_path)


if __name__ == "__main__":
    
    directorys = ['Datenbank', 'Datenbank/Modelle', 'Datenbank/Experimente', 'Ergebnisse']
    
    # install_packages()
    # setup_dirs(directorys)
    # unzip()
    run_tests()

