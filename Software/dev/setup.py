#!/usr/bin/python

import os
import sys
import zipfile
import subprocess

def install_packages():

    # upgrade pip
    os.system("pip install --upgrade pip")
    os.system("pip install -r requirements.txt")

def setup(dirs):

    base_path = os.path.join(sys.path[0], '..','..')

    for element in dirs:

        path = os.path.join(base_path, element)
        
        if not os.path.isdir(path):
            os.mkdir(path)


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
    setup(directorys)
    unzip()

