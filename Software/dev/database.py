#!/usr/bin/python

import logging
import math
import os
import json
import re
import sys

import pandas as pd
import numpy as np
import openpyxl

class Database:

    def __init__(self, data_file, output_dir, logger=None):
        """ 
        Constructor of database class

        Arguments:
            data_file (str): Path to data_file relative from folder position
            output_dir (str): Path to folder to put data for each system
            logger (object): logging object

        """
        if logger == None:
            self.log = logging.getLogger(__file__)
        else:
            self.log = logger
        self.path = data_file
        self.log.info('DATA FILE {}'.format(self.path))
        self.output_dir = output_dir
        self.log.info('OUTPUT DIR {}'.format(self.output_dir))
        self.create_folders()
        self.components = {}
        self.data = self.get_data()
        self.component_keys = [ 'CAS', 'InChiKey', 'Critical temperature / K', 'Critical pressure / bar', 'Acentric factor' ]
        self.special_props = [ 'critical point', 'three-phase line']
        self.sheets = self.get_sheets()
        self.systems = self.get_systems()
        self.components = self.get_components()
        self.write_components_file("database_components")
        
        

    def get_data(self):
        """
        Function that reades Excel File
        """
        
        file = pd.read_excel(self.path, sheet_name=None)

        return file


    def create_folders(self):
        """
        Function that creates Database Folder
        """
        # create Datenbank folder
        path = os.path.join(sys.path[0],'..', '..', 'Datenbank', 'Experimente')
        os.makedirs(path, exist_ok=True)
        path = os.path.join(sys.path[0],'..', '..', 'Datenbank', 'Modelle')
        os.makedirs(path, exist_ok=True)


    def get_components(self):
        """
        Function that returns all components in Database

        Returns:
            dict: dict of all different components in Database with their CAS number
        """

        components = {}

        filepath = os.path.join(os.path.dirname(self.path), "database_components.json")
        if os.path.exists(filepath) == False:

            file = pd.read_excel(self.path, sheet_name=None, nrows=5)

            for system in self.systems.keys():
                
                sheet = self.systems[system]["sheet"]
                
                data = file[sheet].values

                for i in range(2):

                    ele = file[sheet].columns[i+1]

                    if ele in components.keys():
                        continue
                    
                    ele_cas = data[0][i+1]
                    components[ele] = {}
                    components[ele]['CAS'] = ele_cas
                    self.log.info("{}, CAS = {}".format(ele, ele_cas))
            
        else:
            with open(filepath) as f:
                components = json.loads(f.read())

        return components

    def write_components_file(self, filename):

        """
        Function that writes components to file

        Arguments:
            filename (str) : name of output file

        """
        
        def merge_dicts(d1, d2):
        
            res = {}

            size_d1 = count_keys(d1)
            size_d2 = count_keys(d2)


            if size_d1 >= size_d2:
                res = {**d2, **d1}

            else:
                res = {**d1, **d2}

            return res

        def count_keys(dict_, counter=0):
            for each_key in dict_:
                if isinstance(dict_[each_key], dict):
                    # Recursive call
                    counter = count_keys(dict_[each_key], counter + 1)
                else:
                    counter += 1
            return counter

        filepath = os.path.join(os.path.dirname(self.path), filename + ".json")

        if os.path.exists(filepath) == True:
            with open(filepath) as g:
                old_data = json.loads(g.read())


            data = merge_dicts(old_data, self.components)

        else:
            data = self.components

        with open(filepath, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)



    def get_systems(self):
        """ 
        Method to get all systems available including their BAC value and sheet_name

        Returns:
            dict: dictionary with key for each system containing BAC value and sheet_name

        """
        systems = {}
        file = self.data["ReadMe"]
        data = file.values
        # Identify BAC Colums
        bac = {}
        for row in range(len(data)):
            line = data[row]
            for col in range(len(line)):
                column = line[col]
                # Check if value is numeric
                if isinstance(column, (int, float, complex)) and math.isnan(column):
                    continue
                m = re.match(r'BAC=(\d+)\s+\((\d+)\s+binary\s+systems\)', column)
                if not m:
                    continue
                bac[int(m.group(1))] = { 'num': int(m.group(2)), 'row':row, 'col':col }
        #self.log.debug(bac)
        for n, val in bac.items():
            for i in range(val['row'] + 2, val['row'] + 2 + val['num']):
                comp1 = data[i][val['col']]
                comp2 = data[i][val['col']+1]
                sheet = data[i][val['col']+2]
                systems[(comp1,comp2)] = { "sheet": sheet, "BAC": n }
        return systems

    def parse_sheets(self):
        """ 
        Method to parse all sheets from available systems
        """
        counter = 0
        progress_old = 0
        max_count = len(self.systems.items())
        for sys, val in self.systems.items():
            self.log.info('parsing sheet {}'.format(sys))
            self.parse_sheet(sys)
            self.write_sheet(sys)
            progress = round(counter/max_count*100,1)
            if progress - progress_old > 5:
                self.log.info('progress = {} %'.format(progress))
                progress_old = progress
            counter += 1

        self.write_components_file("database_components")

        return

    def parse_sheet(self, sheet_name):
        """ 
        Parse a single system's data

        Arguments:

            sheet_name (tuple(str,str)) : spreadsheet to parse

        """

        system = self.systems[sheet_name]["sheet"]
        self.log.debug('SHEET {}'.format(system))
        file = self.data[system]
        data = file.values
        if not sheet_name[0] in self.components.keys():
            self.components[sheet_name[0]] = {}
        if not sheet_name[1] in self.components.keys():
            self.components[sheet_name[1]] = {}
        marker = []
        for i in range(len(data)):
            line = data[i]
            if not type(line[0]) == type(''):
                continue

            if line[0] in self.component_keys:
                self.components[sheet_name[0]][line[0]] = line[1]
                self.components[sheet_name[1]][line[0]] = line[2]
            if line[0].startswith('-----'):
                marker.append(i)
        marker += [ len(data) - 2, len(data) - 2 ]
        self.log.debug(self.components[sheet_name[0]])
        self.log.debug(marker)
        self.parse_component_mix(sheet_name, data, marker)

    def parse_component_mix(self, sheet_name, data, marker):
        """
        Function to parse mixture data and write results to self.systems

        Arguments:
            sheet_name (str): name of sheet to process
            data (list): sheet data to process
            marker (list): list with all marker positions (all lines with ------)
        """
        for i in range(0, len(marker) - 2, 2):
            pos = marker[i] + 1
            comp_mix = data[pos][0]
            self.systems[sheet_name][comp_mix] = []
            pos += 2

            while pos < marker[i+2]:
                self.log.debug('pos {} {}'.format(pos, data[pos]))
                dataset = {
                    'reference': data[pos][0],
                    'params': {},
                    'measurements' : []
                }
                azeoset = {
                    'reference': data[pos][0],
                    'params': {},
                    'measurements' : []
                }
                pos += 1
                if not comp_mix.lower() in self.special_props:
                    for j in range(4):
                        if '=' in data[pos+j][0]:
                            if type(data[pos+j][1]) == type(""):
                                value = float(re.findall(r"\((.*?)\)", data[pos+j][1])[0])
                            else:
                                value = data[pos+j][1]
                            dataset['params'][data[pos+j][0].replace(' =', '')] = value
                            azeoset['params'][data[pos+j][0].replace(' =', '')] = value
                        else:
                            break
                    pos += j
                n = 1
                while type(data[pos][n]) == type(''):
                    n += 1

                dataset['measurements'].append(list(data[pos][:n]))
                azeoset['measurements'].append(list(data[pos][1:n]))
                pos += 1
                while not type(data[pos][0]) == type('') and not math.isnan(data[pos][0]):
                    # check for azeotropic point
                    if comp_mix.lower() in ["isobaric phase equilibrium data", "isothermal phase equilibrium data"]:
                        if data[pos][3] == "AZEO":
                            azeoset['measurements'].append(list(data[pos][1:n]))
                            for ele in ['T / K ', 'P / bar ']:
                                if ele not in azeoset['params'].keys():
                                    azeoset['params'][ele] = data[pos][0]

                            
                            
                    dataset['measurements'].append(list(data[pos][:n]))
                    pos += 1
                pos += 1
                self.log.debug('dataset {}'.format(dataset))

                
                # check if x1 and y1 data is in azeoset
                if len(azeoset["measurements"]) == 2:
                    if not "Azeotropic point" in self.systems[sheet_name].keys():
                        self.systems[sheet_name]["Azeotropic point"] = []
                        
                    self.systems[sheet_name]["Azeotropic point"].append(azeoset)
                # reset azeoset
                azeoset = {
                    'reference': data[pos][0],
                    'params': {},
                    'measurements' : []
                }

                self.systems[sheet_name][comp_mix].append(dataset)

    def write(self):
        """
        Function to write all systems to .json file in output dir 
        """
        for sys, val in self.systems.items():
            self.log.info('writing sheet {}'.format(sys))
            filename = os.path.join(self.output_dir, sys[0] + '_' + sys[1] + '.json')
            with open(filename, 'w') as outfile:
                json.dump(val, outfile, ensure_ascii=False, indent=2, sort_keys=True)

    def write_sheet(self, sheet_name):
        """
        Function to write a specific system to .json file in output dir

        Arguments:
            sheet_name (str): Name of system to write to file
        """
        filename = os.path.join(self.output_dir, sheet_name[0] + '_' + sheet_name[1] + '.json')
        with open(filename, 'w') as outfile:
            json.dump(self.systems[sheet_name], outfile, default=str, indent=2, sort_keys=True)

    def get_sheets(self):
        """ 
        Method to get all sheets from excel file

        Returns:

            list: list with all spreadsheet names

        """

        data = self.data

        sheets = []
        for table, values in data.items():
            sheets.append(table)
        return sheets

    def get_param_systems(self, param, amount=[]):
        """
        Method to get systems that contain specific parameter

        Arguments:
            param (str): Parameter to search for
            amount (list): systems to get e.g [0, 10] gets first ten systems
        """
        files = os.listdir(self.output_dir)
        counter = 0
        res = []
        for element in files:
            path = os.path.join(self.output_dir, element)
            with open(path , 'r') as f:
                data = json.loads(f.read())
                test = param in data.keys()
            if test == True:
                if counter in amount or amount == []:
                    system = element.split('.json')[0]
                    res.append(system)
                    counter += 1
            if amount != [] and counter == amount[-1]:
                break
            


        self.log.info('systems with {} = {}'.format(param,res))

        return res