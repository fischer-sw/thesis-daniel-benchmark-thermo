#!/usr/bin/python

import os
import sys


def setup(dirs):

    base_path = os.path.join(sys.path[0], '..','..')

    for element in dirs:

        path = os.path.join(base_path, element)
        
        if not os.path.isdir(path):
            os.mkdir(path)


if __name__ == "__main__":
    directorys = ['Datenbank', 'Datenbank/Modelle', 'Datenbank/Experimente', 'Ergebnisse']
    setup(directorys)