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
        self.components = {}
        self.component_keys = [ 'CAS', 'InChiKey', 'Critical temperature / K', 'Critical pressure / bar', 'Acentric factor' ]
        self.special_props = [ 'critical point', 'three-phase line']
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
                systems[(comp1,comp2)] = { "sheet": sheet, "BAC": n }
        return systems

    def parse_sheets(self):
        """ Method to parse all sheets from available systems

        """
        counter = 0
        progress_old = 0
        max_count = len(self.systems.items())
        for sys, val in self.systems.items():
            self.log.info('parsing sheet {}'.format(sys))
            self.parse_sheet(sys)
            self.write_sheet(sys)
            progress = round(counter/max_count,0)
            if progress - progress_old > 1:
                self.log.info('progress = {} %'.format(progress))
                progress = progress_old
            counter += 1
        return

    def parse_sheet(self, sheet_name):
        """ Parse a single system's data

        Arguments:

            sheet_name (tuple(str,str)) : spreadsheet to parse

        """

        system = self.systems[sheet_name]["sheet"]
        self.log.debug('SHEET {}'.format(system))
        file = pd.read_excel(self.path, sheet_name=system)
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
                pos += 1
                if not comp_mix.lower() in self.special_props:
                    for j in range(4):
                        if '=' in data[pos+j][0]:
                            dataset['params'][data[pos+j][0].replace(' =', '')] = data[pos+j][1]
                        else:
                            break
                    pos += j
                n = 1
                while type(data[pos][n]) == type(''):
                    n += 1
                dataset['measurements'].append(list(data[pos][:n]))
                pos += 1
                while not type(data[pos][0]) == type('') and not math.isnan(data[pos][0]):
                    dataset['measurements'].append(list(data[pos][:n]))
                    pos += 1
                pos += 1
                self.log.debug('dataset {}'.format(dataset))
                self.systems[sheet_name][comp_mix].append(dataset)

    def write(self):
        for sys, val in self.systems.items():
            self.log.info('writing sheet {}'.format(sys))
            filename = os.path.join(self.output_dir, sys[0] + '_' + sys[1] + '.json')
            with open(filename, 'w') as outfile:
                json.dump(val, outfile, ensure_ascii=False, indent=2, sort_keys=True)

    def write_sheet(self, sheet_name):
        filename = os.path.join(self.output_dir, sheet_name[0] + '_' + sheet_name[1] + '.json')
        with open(filename, 'w') as outfile:
            json.dump(self.systems[sheet_name], outfile, default=str, indent=2, sort_keys=True)

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