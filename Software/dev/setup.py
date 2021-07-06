#!/usr/bin/python

import os
import sys

directorys = ['Datenbank', 'Datenbank/Modelle', 'Datenbank/Experimente', 'Ergebnisse']

def setup(dirs):

    base_path = os.path.join(sys.path[0], '../..')

    for element in dirs:

        os.mkdir(os.path.join(base_path, element))