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
        self.data_dir = os.path.join(sys.path[0], '..','..', 'Datenbank', 'Experimente')
        self.systems = self.get_systems()
        self.model_name = model_name
        self.ceate_model_dir()
        self.trend_path = os.path.join(sys.path[0],'..','..','TREND 4.0')
        self.dll_path = os.path.join(sys.path[0],'TREND_FIT_DLL.dll')

        self.COSMOparam = (ct.c_double * COSMO_length)()
        self.COSMOparam[0] = 6525.69 * 4184.0
        self.COSMOparam[1] = 1.4859 * 10**8 * 4184.0
        self.COSMOparam[2] = 4013.78 * 4184.0
        self.COSMOparam[3] = 932.31 * 4184.0 
        self.COSMOparam[4] = 3016.43 * 4184.0
        self.COSMOparam[5] = 115.7023
        self.COSMOparam[6] = 117.4650
        self.COSMOparam[7] = 66.0691
        self.COSMOparam[8] = 95.6184
        self.COSMOparam[9] = -11.0549
        self.COSMOparam[10] = 15.4901
        self.COSMOparam[11] = 84.6268
        self.COSMOparam[12] = 109.6621
        self.COSMOparam[13] = 52.9318
        self.COSMOparam[14] = 104.2534
        self.COSMOparam[15] = 19.3477
        self.COSMOparam[16] = 141.1709
        self.COSMOparam[17] = 58.3301
        self.COSMOparam[18] = 115.70
        self.COSMOparam[19] = 76.89
        self.COSMOparam[20] = 85.37 

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


        bacs = [1]

        for element in self.systems:

            sys_file_name = '_'.join(element) + '.json'

            # check for bac code
            with open(os.path.join(self.data_dir, sys_file_name)) as file:
                system = json.loads(file.read())

            if not system["BAC"] in bacs:
                continue

            res = self.calc_system_results(element)
            

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

                        hE , hE_error = self.calc_heat_capa(system, Temp, Press, x)

                        # if no error accured
                        if hE_error.value != -7878:
                            results[element][i]['measurements'].append([hE, x])

            if element == "blabla":
                pass
        
        # check all keys for model values
        for element in calc_vars:
            
            check = False

            if element not in list(results.keys()):
                continue
            
            n_measure = len(results[element])
            
            for i in range(n_measure):
                # check if only header is in measurements
                if len(results[element][i]["measurements"]) > 1:
                    check = True
            
            if check == False:
                results.pop(element, None)

        # if nothing could be calculated delete dict
        if list(results.keys()) == ["BAC"]:
            results = {}
        return results

    def write_results(self, filename, results):
        
        path = os.path.join(self.data_dir,'../Modelle', self.model_name, filename)
        with open(path, 'w') as outfile:
            json.dump(results, outfile, default=str, indent=2, sort_keys=True)

    def ceate_model_dir(self):

        path = os.path.join(self.data_dir,'../Modelle', self.model_name)

        if os.path.isdir(path) == False:
            os.mkdir(path)


    def calc_heat_capa(self, system, temp, press, x):
        
        fldmix = None
        fld1 = None
        fld2 = None
        hE = None
        h_mix = None
        h_fld1 = None
        h_fld2 = None
        errmix = None

        fld1_name = system[0].lower()
        fld2_name = system[1].lower()

        press = press/10  # MPa

        # self.fldmix1 = Fluid('TP','HE',['methane','ethane'],[0.6,0.4],[1,1],1,self.trend_path,'molar',self.dll_path)
        fldmix = Fluid('TP','H',[fld1_name, fld2_name],[x, 1-x],[1,1],1,self.trend_path,'molar',self.dll_path)
        
        fld1 = Fluid('TP','H',[fld1_name, fld2_name],[0.99999999,0.00000001],[1,1],1,self.trend_path,'molar',self.dll_path)
        fld2 = Fluid('TP','H',[fld2_name, fld1_name],[0.99999999,0.00000001],[1,1],1,self.trend_path,'molar',self.dll_path)        
        
        # fldmix = Fluid('TP','H',['methane','ethane'],[0.6,0.4],[1,1],1,self.trend_path,'molar',self.dll_path)
        # fld1 = Fluid('TP','H',['methane','ethane'],[0.99999999,0.00000001],[1,1],1,self.trend_path,'molar',self.dll_path)
        # fld2 = Fluid('TP','H',['ethane','methane'],[0.99999999,0.00000001],[1,1],1,self.trend_path,'molar',self.dll_path)

        h_mix, errmix = fldmix.TREND_EOS_FIT(temp, press, self.COSMOparam)
        h_fld1, errmix = fld1.TREND_EOS_FIT(temp, press, self.COSMOparam)
        h_fld2, errmix = fld2.TREND_EOS_FIT(temp, press, self.COSMOparam)
        hE = h_mix - x * h_fld1 - (1-x) * h_fld2
        
        if errmix.value != -7878:
            self.log.info("{}, x = {}, hE = {} J/(mol*K)".format(system,x,hE))

        else:
            self.log.info("{} hE calculation not possible".format(system))


        return hE, errmix
