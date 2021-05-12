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

class database:
    
    def __init__(self, data_file, output_dir, logger=None):
        """ Constructor of database class

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
        self.sheets = self.get_sheets()
        self.systems = self.get_systems()

    def get_systems(self):
        """ Method to get all systems available including their BAC value and sheet_name

        Returns:
            dict: dictionary with key for each system containing BAC value and sheet_name

        """
        systems = {}
        file = pd.read_excel(self.path, sheet_name="ReadMe")
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
                systems[comp1+"_"+comp2] = { "sheet": sheet, "BAC": n }
        return systems

    def parse_sheets(self):
        """ Method to parse all sheets from available systems

        """
        for sys, val in self.systems.items():
            self.parse_sheet(sys)
        return

    def parse_sheet(self, sheet_name):
        """ Parse a single system's data

        Arguments:

            sheet_name (str) : spreadsheet to parse

        """

        system = self.systems[sheet_name]["sheet"]
        file = pd.read_excel(self.path, sheet_name=system)
        data = file.values

        return
    

    def get_system_data(self, system):
        """ Method to return all data available for a specific system

        Arguments:

            system (str): system to get all data from

        Returns:

            dict: returns dict with all data that was on spreadsheet

        """

        def check_for_dict(dic):
            if dic not in self.systems[system]:
                self.systems[system][dic] = {}

        needed_dicts = ["Isothermal phase equilibrium data", \
                        "Isobaric phase equilibrium data", \
                        "Enthalpy of mixing", \
                        "Critical point", \
                        "Heat capacity of mixing", \
                        "Three-phase line",\
                    ]

        for dic in needed_dicts:
            check_for_dict(dic)
                    
        if "Isothermal phase equilibrium data" not in self.systems[system]:
            self.systems[system]["Isothermal phase equilibrium data"] = {}

        sheet = self.systems[system]["sheet"]

        file = pd.read_excel(self.path, sheet_name=None)
        data = file[sheet].values
        row_limit = len(data)
        # Search for Isothermal phase equilibrium


        for line in data:
            for column in line:
                
                # Check if value is numeric
                if isinstance(column, (int, float, complex)):
                    
                    # Check if value is empty cell
                    if math.isnan(column):
                        continue

                    else:
                        column = str(column)
                
                Isoth_eq = re.match('Isothermal phase equilibrium data',column)
                Isobar_eq = re.match('Isobaric phase equilibrium data',column)
                h_mix = re.match('Enthalpy of mixing',column)
                p_crit = re.match('Critical point',column)
                c_p = re.match('Heat capacity of mixing',column)
                three_pha_l = re.match('Three-phase line',column)
                

                if Isobar_eq  is not None:
                    row = int(np.where(data == line)[0][0])
                    col = int(np.where(line == column)[0][0])
                   
                    stop = False
                    counter = row
                    datasets = 0
                    data_set = []

                    while stop == False:
                        
                        counter += 1
                        value = data[counter][col]

                        if counter + 1 == row_limit:
                            self.systems[system][column][str(pressure)] = data_set
                            stop = True
                            continue
                        
                        if isinstance(value, (int, float, complex)):
                            
                            if math.isnan(value):
                                self.systems[system][column][str(pressure)] = data_set
                                continue
                            else:
                                temp = data[counter][col]
                                y1 = data[counter][col+1]

                                data_set.append([temp, y1])

                        else:
                            new_dataset_test = re.match('P / bar = ',value)
                            stop_cond = re.match('-----------',value)

                            if stop_cond is not None and bool(self.systems[system]["Isobaric phase equilibrium data"]) != False:
                                stop = True
                        
                            if new_dataset_test is not None:
                                pressure = data[counter][col+1]
                            
                                # Add temperature to dataset
                                data_set = []
                                data_set.append(['temperature [K]','y_1'])

                if Isoth_eq  is not None:
                    row = int(np.where(data == line)[0][0])
                    col = int(np.where(line == column)[0][0])
                   
                    stop = False
                    counter = row
                    datasets = 0
                    data_set = []

                    while stop == False:
                        
                        if counter + 1 == row_limit:
                            stop = True
                            self.systems[system][column][str(temperature)] = data_set
                            continue

                        counter += 1
                        value = data[counter][col]
                                          
                        if isinstance(value, (int, float, complex)):
                            
                            if math.isnan(value):
                                self.systems[system][column][str(temperature)] = data_set
                                continue
                            else:
                                pres = data[counter][col]
                                x1 = data[counter][col+1]
                                y1 = data[counter][col+2]

                                data_set.append([pres, x1, y1])

                        else:
                            new_dataset_test = re.match('T / K = ',value)
                            stop_cond = re.match('-----------',value)

                            if stop_cond is not None and bool(self.systems[system]["Isothermal phase equilibrium data"]) != False:
                                stop = True
                        
                            if new_dataset_test is not None:
                                temperature = data[counter][col+1]
                            
                                # Add temperature to dataset
                                data_set = []
                                data_set.append(['pressure [bar]','x_1','y_1'])
                
                if h_mix  is not None:
                    row = int(np.where(data == line)[0][0])
                    col = int(np.where(line == column)[0][0])
                   
                    stop = False
                    counter = row
                    data_set = []

                    while stop == False:
                        
                        if counter + 2 == row_limit:
                            stop = True
                            self.systems[system][column][str(temperature) + "_" + str(pressure)] = data_set
                            continue
                        
                        counter += 1
                        value1 = data[counter][col]
                        value2 = data[counter+1][col]

                        if isinstance(value1, (int, float, complex)):
                            
                            if math.isnan(value1):
                                self.systems[system][column][str(temperature) + "_" + str(pressure)] = data_set
                                continue
                            else:
                                h_m = data[counter][col]
                                x1 = data[counter][col+1]
                                
                                data_set.append([h_m, x1])

                        else:
                            new_dataset_test1 = re.match('T / K = ',value1)

                            if not isinstance(value2, (int, float, complex)):
                                new_dataset_test2 = re.match('P / bar = ',value2)

                            stop_cond = re.match('-----------',value1)

                            if stop_cond is not None and bool(self.systems[system]["Enthalpy of mixing"]) != False:
                                stop = True
                        
                            if new_dataset_test1 is not None and new_dataset_test2 is not None:
                                temperature = data[counter][col+1]
                                pressure = data[counter+1][col+1]
                            
                                # Add temperature to dataset
                                data_set = []
                                data_set.append(['h_m [J/mol]','x_1'])
                
                if p_crit  is not None:
                    row = int(np.where(data == line)[0][0])
                    col = int(np.where(line == column)[0][0])
                   
                    stop = False
                    counter = row
                    
                    data_set = []
                    data_set.append(['T [K]','p [bar]','x_1'])

                    while stop == False:
                    
                        if counter + 1 == row_limit:
                            stop = True
                            self.systems[system][column] = data_set
                            continue

                        counter += 1
                        value = data[counter][col]
                        
                        if isinstance(value, (int, float, complex)):
                            
                            if math.isnan(value):                 
                                continue

                            else:
                                T = data[counter][col]
                                p = data[counter][col+1]
                                x1 = data[counter][col+2]

                                data_set.append([T, p, x1])

                        else:
                            stop_cond = re.match('-----------',value)

                            if stop_cond is not None and bool(self.systems[system]["Critical point"]) != False:
                                self.systems[system][column] = data_set
                                stop = True


                if three_pha_l is not None:
                    row = int(np.where(data == line)[0][0])
                    col = int(np.where(line == column)[0][0])
                   
                    stop = False
                    counter = row
                    
                    data_set = []
                    data_set.append(['T [K]','p [bar]','x_1_alpha', 'x_1_beta','y1'])

                    while stop == False:
                    
                        if counter + 1 == row_limit:
                            stop = True
                            self.systems[system][column] = data_set
                            continue

                        counter += 1
                        value = data[counter][col]
                        
                        if isinstance(value, (int, float, complex)):
                            
                            if math.isnan(value):                 
                                continue

                            else:
                                T = data[counter][col]
                                p = data[counter][col+1]
                                x1_alpha = data[counter][col+2]
                                x1_beta = data[counter][col+3]
                                y1 = data[counter][col+4]

                                data_set.append([T, p, x1_alpha, x1_beta,y1])

                        else:
                            stop_cond = re.match('-----------',value)

                            if stop_cond is not None and bool(self.systems[system]["Three-phase line"]) != False:
                                self.systems[system][column] = data_set
                                stop = True         
                
                if c_p  is not None:
                    row = int(np.where(data == line)[0][0])
                    col = int(np.where(line == column)[0][0])
                   
                    stop = False
                    counter = row
                    data_set = []

                    while stop == False:
                        
                        if counter + 2 == row_limit:
                            stop = True
                            self.systems[system][column][str(temperature) + "_" + str(pressure)] = data_set
                            continue
                        
                        counter += 1
                        value1 = data[counter][col]
                        value2 = data[counter+1][col]

                        if isinstance(value1, (int, float, complex)):
                            
                            if math.isnan(value1):
                                self.systems[system][column][str(temperature) + "_" + str(pressure)] = data_set
                                continue
                            else:
                                cp_m = data[counter][col]
                                x1 = data[counter][col+1]
                                
                                data_set.append([cp_m, x1])

                        else:
                            new_dataset_test1 = re.match('T / K = ',value1)

                            if not isinstance(value2, (int, float, complex)):
                                new_dataset_test2 = re.match('P / bar = ',value2)

                            stop_cond = re.match('-----------',value1)

                            if stop_cond is not None and bool(self.systems[system]["Heat capacity of mixing"]) != False:
                                stop = True
                        
                            if new_dataset_test1 is not None and new_dataset_test2 is not None:
                                temperature = data[counter][col+1]
                                pressure = data[counter+1][col+1]
                            
                                # Add temperature to dataset
                                data_set = []
                                data_set.append(['cp_m [J/mol]','x_1'])



    def get_sheets(self):
        """ Method to get all sheets from excel file

        Returns:

            list: list with all spreadsheet names

        """

        data = pd.read_excel(self.path, sheet_name=None)
        
        sheets = []
        for table, values in data.items():
            sheets.append(table)
        return sheets

    def get_all_data(self):
        """ Method to check if system is parsed and if so continue with next. Also prints progress to console to see what is going on.

        """


        for key, value in self.systems.items():
            # check for existing file
            name = key + ".json"
            existing_files = os.listdir(self.output_dir)
            if name in existing_files:
                continue
            else:
                self.get_system_data(key)
                self.write_data(key)

                print("Fortschritt....."+str(round(len(existing_files)/len(self.sheets)*100,3))+ "%")


    def write_data(self,system):
        """ Method to write data to json file

        Arguments:

            system (str): system to write data to file in output folder

        """
        name = system
        path = self.output_dir + "/" + name + ".json"

        with open(path, 'w') as outfile:
            json.dump(self.systems[system], outfile, ensure_ascii=False, indent=4)