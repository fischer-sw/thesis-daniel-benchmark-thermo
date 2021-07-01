#!/usr/bin/python

from datetime import date
import logging
import math
import os
import json
import re
import sys

import pandas as pd
import numpy as np
import openpyxl

from fluid import *

class Model:

    def __init__(self, model_name, logger=None):
        
        """ 
        Constructor of database class

        """
        if logger == None:
            self.log = logging.getLogger(__file__)
        else:
            self.log = logger
        self.data_dir = os.path.join(sys.path[0], '../..', 'Datenbank', 'Experimente')
        self.systems = self.get_systems()
        self.model_name = model_name
        self.ceate_model_dir()

    def get_systems(self):
        
        """
        Function that returns all available experimental systems

        Returns:
            list: list of systems e.g [[<Comp1>,<Comp2>],[...],...]
        """
        systems = []
        
        data = os.listdir(self.data_dir)

        for element in data:
            # split systems into components
            components = element.split('.json')[0].split('_')
            systems.append(components)


        return systems

    def calc_model_results(self):
        for element in self.systems:
            res = self.calc_system_results(element)
            sys_file_name = '_'.join(element) + '.json'

            if res != {}:
                self.write_results(sys_file_name, res)


    def calc_system_results(self, system):

        """
        Function that calculates model results for a system

        Arguments:
            system (list): list of components

        Returns:
            dict: dictionary containing all model data 

        """
        results = {}

        calc_vars = ['Enthalpy of mixing']

        self.log.info('Calculating {} {}'.format(system[0], system[1]))

        # get experimental data
        sys_file_name = '_'.join(system) + '.json'

        with open(os.path.join(self.data_dir, sys_file_name)) as file:
            exp_data = json.loads(file.read())


        sys_keys = exp_data.keys()

        for element in calc_vars:
            if element not in sys_keys:
                continue

            if "BAC" not in results.keys():
                results["BAC"] = exp_data["BAC"]

            if element == 'Enthalpy of mixing':
                #add key to dict
                if not element in results.keys():
                    results[element] = []

                # loop through all measurements
                for i in range(len(exp_data[element])):
                    
                    data_set = exp_data[element][i]
                    
                    Press = data_set["params"]["P / bar "]
                    Temp = data_set["params"]["T / K "]
                    
                    results[element].append({})  
                    results[element][i]['measurements'] = [exp_data[element][i]['measurements'][0]]
                    results[element][i]['params'] = exp_data[element][i]['params']


                    for k in range(1,len(exp_data[element][i]['measurements'])):
                        
                        x = exp_data[element][i]['measurements'][k][1]

                        # calculate value here
                        erg = 10

                        # if no error accured
                        if erg > 0:
                            results[element][i]['measurements'].append([erg, x])

            if element == "blabla":
                pass


        return results

    def write_results(self, filename, results):
        
        path = os.path.join(self.data_dir,'../Modelle', self.model_name, filename)
        with open(path, 'w') as outfile:
            json.dump(results, outfile, default=str, indent=2, sort_keys=True)

    def ceate_model_dir(self):

        path = os.path.join(self.data_dir,'../Modelle', self.model_name)

        if os.path.isdir(path) == False:
            os.mkdir(path)