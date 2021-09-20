#!/usr/bin/python

from datetime import date
import logging
import math
import os
import json
import re
import sys
import shutil
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)

import zipfile
import pandas as pd
import numpy as np
import openpyxl

from fluid import *
from srk_fld_file import *

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
        self.model_dir = os.path.join(sys.path[0], '..','..', 'Datenbank', 'Modelle', model_name)

        self.systems = self.get_systems()
        self.model_name = model_name

        self.model = "SRK"
        
        self.ceate_model_dir()
        # self.reset_model()

        self.bacs = list(range(1,10))
        
        self.trend_path = os.path.join(sys.path[0],'..','..','TREND 4.0')
        self.dll_path = os.path.join(sys.path[0],'TREND_FIT_DLL.dll')


        vars = ['Enthalpy of mixing', 'Heat capacity of mixing', 'Isothermal phase equilibrium data', 'Isobaric phase equilibrium data', 'Azeotropic point']

        self.calc_vars = vars[0:5]
        # self.calc_vars = [vars[4]]

        # keys to delete from all model data dicts

        # self.del_keys = ['Isothermal phase equilibrium data', 'Isobaric phase equilibrium data', 'Azeotropic point']
        self.del_keys = []



        self.fluid_mappings = self.read_mappings("mappings")

        self.clean_model_data()

        

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

    def check_xy_swap(self, system, exp_data, model_data, mode):
    
        swap = False
        exp_x_system = system[0]


        # get first and last elements of data

        x1_exp = np.array(list(list(zip(*exp_data['measurements'][1:]))[1]))
        x1_exp_1_idx = np.argmax(x1_exp) + 1
        x1_exp_0_idx = np.argmin(x1_exp) + 1
        x1_mod = np.array(list(list(zip(*model_data['measurements'][1:]))[1]))
        x1_mod_1_idx = np.argmax(x1_mod) + 1
        x1_mod_0_idx = np.argmin(x1_mod) + 1

        model_check_data = {
            'first' : model_data['measurements'][x1_mod_0_idx],
            'last' : model_data['measurements'][x1_mod_1_idx],
        }

        exp_check_data = {
            'first' : exp_data['measurements'][x1_exp_0_idx],
            'last' : exp_data['measurements'][x1_exp_1_idx],
        }



        if mode == 'isotherm':

            var = 'Tvap'
            par = "T / K "

            par_val = model_data['params'][par]

            value_comp1, error_comp1 = self.calc_vap_pres(system[0], var, par_val) #MPa
            value_comp2, error_comp2 = self.calc_vap_pres(system[1], var, par_val) #MPa

            if error_comp1.value == 0 and error_comp2.value == 0:

                value_comp1 = value_comp1 * 10
                value_comp2 = value_comp2 * 10
            
            else:

                diff = [abs(model_check_data['first'][0] - exp_check_data['first'][0]), abs(model_check_data['first'][0] - exp_check_data['last'][0]), abs(model_check_data['last'][0] - exp_check_data['first'][0]), abs(model_check_data['last'][0] - exp_check_data['last'][0])]

                if diff[0] > diff[1] and diff[3] > diff[2]: 
                    swap = True

        else:

            var = 'pvap'
            par = "P / bar "

            par_val = model_data['params'][par]

            value_comp1, error_comp1 = self.calc_vap_pres(system[0], var, par_val)
            value_comp2, error_comp2 = self.calc_vap_pres(system[1], var, par_val)

            
            if error_comp1.value != 0 and error_comp2.value != 0:

                diff = [abs(model_check_data['first'][0] - exp_check_data['first'][0]), abs(model_check_data['first'][0] - exp_check_data['last'][0]), abs(model_check_data['last'][0] - exp_check_data['first'][0]), abs(model_check_data['last'][0] - exp_check_data['last'][0])]

                if diff[0] > diff[1] and diff[3] > diff[2]: 
                    swap = True


        diff_model = [abs(value_comp1 - model_check_data['first'][0]), abs(value_comp2 - model_check_data['first'][0]), abs(value_comp1 - model_check_data['last'][0]), abs(value_comp2 - model_check_data['last'][0])]

        if diff_model[0] < diff_model[1] or diff_model[2] > diff_model[3]:
            model_x_system = system[1]
        else:
            model_x_system = system[0]



        diff_exp = [abs(value_comp1 - exp_check_data['first'][0]), abs(value_comp2 - exp_check_data['first'][0]), abs(value_comp1 - exp_check_data['last'][0]), abs(value_comp2 - exp_check_data['last'][0])]

        if diff_exp[0] < diff_exp[1] or diff_exp[2] > diff_exp[3]:
            exp_x_system = system[1]
        else:
            exp_x_system = system[0]

        
        if model_x_system != exp_x_system:
            swap = True


        
        

        tmp_model = {
            "measurements" : [model_data["measurements"][0]],
            "params" : model_data["params"]
        }

        if swap == True:
            for i in range(1,len(model_data["measurements"])):
                tmp_model['measurements'].append([model_data['measurements'][i][0], 1 - model_data['measurements'][i][1], 1 - model_data['measurements'][i][2]])       

        else:
            for i in range(1,len(model_data["measurements"])):
                tmp_model['measurements'].append([model_data['measurements'][i][0], model_data['measurements'][i][1], model_data['measurements'][i][2]])       


        return exp_data, tmp_model, exp_x_system


    def read_mappings(self, filename):
        
        mappings_path = os.path.join(sys.path[0], "..", "..","Daten", filename + ".json")

        with open(mappings_path) as f:
            mappings = json.loads(f.read())

        return mappings


    def reset_model(self):
        files = os.listdir(self.model_dir)
        for file in files:
            os.remove(os.path.join(self.model_dir, file))


    def get_systems(self):
        
        """
        Function that returns all available experimental systems

        Returns:
            list: list of systems e.g [[<Comp1>,<Comp2>],[...],...]
        """
        systems = []
        
        data = os.listdir(self.data_dir)
        
        # remove backup from data
        if "0_backup.zip" in data:
            data.remove("0_backup.zip")

        for element in data:
            # split systems into components
            components = element.split('.json')[0].split('_')
            systems.append(components)


        return systems


    def get_system_data(self, system, type):
        
        if type != "model":
            path = os.path.join(self.data_dir, system[0]+"_"+system[1] + ".json")
        
        else:
            path = os.path.join(self.model_dir, system[0]+"_"+system[1] + ".json")


        if os.path.exists(path):

            with open(path) as f:
                data = json.loads(f.read())
        else:
            data = {}
        return data
    

    def do_model_backup(self):

        path = self.model_dir

        name = "0_backup"

        archive_path = os.path.join(self.model_dir, name + ".zip")

        res = input("Do you want to make a backup? (yes|no)")

        if res == "yes":

            if os.path.exists(archive_path):
                os.remove(archive_path)
            shutil.make_archive(name, 'zip', path)
            shutil.copyfile('./' + name + '.zip', archive_path)
            os.remove('./' + name + '.zip')

    
    
    def clean_model_data(self):

        for system in self.systems:

            data = self.get_system_data(system, 'model')

            if data != {}:
                
                # check keys de be deleted
                keys = list(data.keys())

                for key in self.del_keys:
                    if key in keys:
                        data.pop(key)
                        self.log.info("Deleted {} data in {} | {}".format(key, system[0], system[1]))


                keys = list(data.keys())
                
                for key in keys:
                    if key in ['BAC', 'sheet']:
                        continue
                    n_mes = len(data[key])
                    i = 0
                    while i < n_mes:
                        test_element = data[key][i]['measurements']
                        if len(test_element) == 1:
                            
                            data[key].remove(data[key][i])
                            n_mes -= 1
                        else:
                            i += 1

                self.write_results(system[0] + '_' + system[1] + '.json', data)


    def create_system_diags(self, system):
        model_data = self.get_system_data(system, 'model')
        exp_data = self.get_system_data(system, 'exp')

        for key in list(model_data.keys()):
                if not key in ["Isothermal phase equilibrium data", "Isobaric phase equilibrium data"]:
                    continue

                
    
                if key == "Isothermal phase equilibrium data":
                    mode = "isotherm"
                    par = "T / K "

                if key == "Isobaric phase equilibrium data":
                    mode = "isobar"
                    par = "P / bar "

                #
                for mes in model_data[key]:
                    # get exp dataset

                    for k in range(len(exp_data[key])):
                        if exp_data[key][k]["params"] == mes["params"]:
                            param = mes["params"][par]
                            self.create_phase_eq_diag(mes, exp_data[key][k], system, mode, param)

    def create_diags(self):

        for system in self.systems:

            self.create_system_diags(system)

    def create_phase_eq_diag(self, model_data, exp_data, system, mode, param):
         # check for existing diag
        # path = os.path.join(self.data_dir,'../../Diagramme', self.model_name, system[0]+ "_" + system[1] + "_" + mode + "_" + str(param) + "_" + ".pdf")
        path = os.path.join(self.data_dir,'../../Diagramme', self.model_name, system[0]+ "_" + system[1] + "_" + mode + "_" + str(param) + "_" + ".png")
        
        if os.path.exists(path):
            self.log.info("{} Diag for {} | {} already exsists for parameter {}".format(mode, system[0], system[1], param))
            return

        if model_data['measurements'][0][1:3] != ['x₁', 'y₁']:
            return

        exp_data , model_data, exp_x_system = self.check_xy_swap(system, exp_data, model_data , mode)


        model_data_mes = model_data["measurements"]
        exp_data_mes = exp_data["measurements"]


        if len(exp_data_mes[0]) != 3 or len(model_data_mes) == 1 or len(exp_data_mes) == 1:
            return

        # clean data
        mod_len = len(model_data_mes)
        exp_len = len(exp_data_mes)

        if len(model_data_mes[0]) != 3 or len(model_data_mes[0]) != 3:
            return

        i = 1
        while i < mod_len:

            if len(model_data_mes) == 1:
                return

            ele = model_data_mes[i]
            if type(ele[1]) == type("") or type(ele[2]) == type(""):
                model_data_mes.remove(model_data_mes[i])
            else:
                i += 1

        i = 1
        while i < exp_len:

            if len(exp_data_mes) == 1:
                return

            ele = exp_data_mes[i]
            if type(ele[1]) == type("") or type(ele[2]) == type(""):
                exp_data_mes.remove(exp_data_mes[i])
            else:
                i += 1
        
        

        x_data_model = np.array(list(list(zip(*model_data_mes[1:]))[1]))
        x_data_exp = np.array(list(list(zip(*exp_data_mes[1:]))[1]))

        y_data_model = np.array(list(list(zip(*model_data_mes[1:]))[2]))
        y_data_exp = np.array(list(list(zip(*exp_data_mes[1:]))[2]))
        
        var_data_model = np.array(list(list(zip(*model_data_mes[1:]))[0]))
        var_data_exp = np.array(list(list(zip(*exp_data_mes[1:]))[0]))

        fig, ax = plt.subplots()
        ax.plot(x_data_model, var_data_model,'g+',label="Modell-Daten")
        ax.plot(y_data_model, var_data_model,'g+')
        ax.plot(x_data_exp, var_data_exp,'r+',label="Exp-Daten")
        ax.plot(y_data_exp, var_data_exp,'r+')


        ax.legend()

        #set ticks
        ax.tick_params(direction='in', top=True, right=True)
        ax.tick_params(direction='in', top=True, right=True, which='minor', length=3)
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))

        # set labels
        
        x_label = "$x_{" + exp_x_system + "}$"

        plt.xlabel(x_label)

        if mode == "isotherm":
            plt.ylabel("p [bar]")
            
            #for i in range(len(var_data_model)):
            #    var_data_model[i] = var_data_model[i] * 10
                


        if mode == "isobar":
            plt.ylabel("T [K]")

        #set limits
        # plt.ylim(20, 70)
        plt.xlim(0, 1)

        # set size
        fig.set_size_inches(9, 6)

        
        fig.savefig(path, dpi=100)

        self.log.info("Created {} Diag for {} | {} for parameter {}".format(mode, system[0], system[1], param))

        plt.close()


    def check_possible_calculations(self):
        
        exp_count = self.get_experimental_count()


        model_count = {}

        res = {}

        # init results
        for bac in self.bacs:
            model_count["BAC" + str(bac)] = {}
            res["BAC" + str(bac)] = {}

        for system in self.systems:

            data = self.get_system_data(system, 'exp')

            bac = "BAC" + str(data["BAC"])
            
            for var in self.calc_vars:
                
                if not var in data.keys():
                    continue

                test = self.check_model_components(self.model, system)
                
                if test == True:

                    if var in model_count[bac].keys(): 
                        model_count[bac][var] += 1

                    else:
                        model_count[bac][var] = 1
        
        for key in model_count.keys():

            for var in self.calc_vars:
                res[key][var] = round(model_count[key][var] / exp_count[key][var] * 100, 0)


        return res, exp_count, model_count
        


    def get_experimental_count(self):
        res = {}

        exp_data_list = os.listdir(self.data_dir)

        # init results
        for bac in self.bacs:
            res["BAC" + str(bac)] = {}

         
        for system in self.systems:
            
            data = self.get_system_data(system, 'exp')

            for key in data.keys():
                if key in ["BAC","sheet"]:
                    continue
                else:
                    bac = "BAC"+ str(data["BAC"])
                    if key in res[bac].keys():
                        res[bac][key] += 1
                    else:
                        res[bac][key] = 1

        return res


    def check_model_components(self, model, components):
        
        res = {}

        for ele in components:
            res[ele] = False
        
        if model == "SRK":
            
            # get srk-fld data

            path = os.path.join(sys.path[0], "..", "..","TREND 4.0", "srk", "fluids_srk", "srkfluids.fld")
            reader = Filereader(path)
            srk_data = reader.readdata()

            for ele in components:
                model_comp_name = self.fluid_mappings[ele]

                if not model_comp_name in srk_data.keys() :
                    continue

                comp = srk_data[model_comp_name]

                letters = ["A", "B", "C", "D", "E", "F", "G"]

                for letter in letters:
                    if comp[letter] != '0':
                       res[ele] = True

            test_res = 0

            for ele in components:
                if res[ele] == True:
                    test_res += 1
            
            if test_res == 2:
                return True

            else:
                return False

        if model == "new model":
            # do check here
            pass

        else:
            return False

    def calc_model_results(self):

        for element in self.systems:

            sys_file_name = '_'.join(element) + '.json'

            # check for bac code
            with open(os.path.join(self.data_dir, sys_file_name)) as file:
                system = json.loads(file.read())

            if not system["BAC"] in self.bacs:
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
        model_data = {}

        # get experimental data
        sys_file_name = '_'.join(system) + '.json'

        with open(os.path.join(self.data_dir, sys_file_name)) as file:
            exp_data = json.loads(file.read())


        model_path = os.path.join(self.model_dir, sys_file_name) 

        if os.path.exists(model_path):

            with open(model_path) as file:
                model_data = json.loads(file.read())

        sys_keys = list(exp_data.keys())

        for element in self.calc_vars:
            if element not in sys_keys:
                self.log.info('Skipped {} {}'.format(system[0], system[1]))
                continue

            if "BAC" not in results.keys():
                results["BAC"] = exp_data["BAC"]

            if element in ['Enthalpy of mixing', 'Heat capacity of mixing']:
                
                components_test = self.check_model_components(self.model, system)
                

                if components_test == False:
                    self.log.info("No A-G data for {} | {}".format(self.fluid_mappings[system[0]], self.fluid_mappings[system[1]]))
                    return {}

                # loop through all measurements
                for i in range(len(exp_data[element])):
                    
                    data_set = exp_data[element][i]


                    #add key to dict
                    if not element in results.keys():
                        results[element] = []

                    results[element].append({})
                        
                    
                    # check for existing data
                    if model_data != {}:

                         # check for key in dict
                        if element in list(model_data.keys()):

                            if exp_data[element][i]["params"] == model_data[element][i]["params"]:
                                results[element][i] = model_data[element][i]
                                self.log.info("Already calculated {} data for {} | {}".format(element,self.fluid_mappings[system[0]], self.fluid_mappings[system[1]] ))
                                continue
                    
                    
                    Press = data_set["params"]["P / bar "]
                    Temp = data_set["params"]["T / K "]
                    

                    results[element][i]['measurements'] = [exp_data[element][i]['measurements'][0]]
                    results[element][i]['params'] = exp_data[element][i]['params']


                    for k in range(1,len(exp_data[element][i]['measurements'])):
                        
                        x = exp_data[element][i]['measurements'][k][1]

                        if element == 'Enthalpy of mixing':
                            hE , hE_error = self.calc_h_mix(system, Temp, Press, x)

                            # if no error accured
                            if hE_error.value != -7878:
                                results[element][i]['measurements'].append([hE, x])

                        if element == 'Heat capacity of mixing':
                            cp , cp_error = self.calc_heat_capa(system, Temp, Press, x)

                            # if no error accured
                            if cp_error.value != -7878:
                                results[element][i]['measurements'].append([cp, x])


            if element in ["Isothermal phase equilibrium data", "Isobaric phase equilibrium data"]:
                
                # loop through all measurements

                mes_number = len(exp_data[element])
                deleted = 0

                for i in range(mes_number):
                    
                    data_set = exp_data[element][i]


                    #add key to dict
                    if not element in results.keys():
                        results[element] = []

                    results[element].append({})
                        
                    
                    # check for existing data
                    if model_data != {}:

                        # check for key in dict
                        if element in list(model_data.keys()):

                            for k in range(len(model_data[element])):
                                if exp_data[element][i]["params"] == model_data[element][k]["params"]:
                                    break 

                            if exp_data[element][i]["params"] == model_data[element][k]["params"]:
                                results[element][i-deleted] = model_data[element][k]
                                self.log.info("Already calculated {} data for {} | {}".format(element,self.fluid_mappings[system[0]], self.fluid_mappings[system[1]] ))
                                continue
                    
                    if element == 'Isothermal phase equilibrium data':
                        var_val = data_set["params"]["T / K "]
                        var = 'Tvap'

                    if element == 'Isobaric phase equilibrium data':
                        var_val = data_set["params"]["P / bar "]
                        var = 'pvap'

                    # create results
                    results[element][i-deleted]['measurements'] = [exp_data[element][i]['measurements'][0]]
                    results[element][i-deleted]['params'] = exp_data[element][i]['params']

                    # calculate results
                    values, value_lis, phase_error = self.calc_phase_eq(system, var, var_val)

                    if phase_error != 0:
                        self.log.info("error in {} for {} | {}, error = {}".format(element,self.fluid_mappings[system[0]], self.fluid_mappings[system[1]], phase_error))
                        results[element].remove(results[element][-1])
                        deleted += 1
                        continue
                    
                    


                    for n in range(1,len(value_lis[1:])):
                        results[element][i-deleted]['measurements'].append([value_lis[n][0], value_lis[n][1], value_lis[n][2]])


                    self.log.info("Added new dataset in {} for {} | {}.".format(element,self.fluid_mappings[system[0]], self.fluid_mappings[system[1]]))


            if element == "Azeotropic point":
                
                if not 'Isothermal phase equilibrium data' in model_data.keys():
                    self.log.info("No isotherm phase eq data for {} | {} to calculate {}".format(self.fluid_mappings[system[0]], self.fluid_mappings[system[1]], element))
                    break


                
                
                 # loop through all measurements
                for i in range(len(exp_data[element])):

                    dataset = {
                        "params" : {
                            "T / K " : 0,
                            "P / bar " : 0
                        },
                        "measurements": [
                            [
                                "x\u2081",
                                "y\u2081"
                            ],
                        ]
                    }
                    
                    data_set = exp_data[element][i]
                    
                    #add key to dict
                    if not element in results.keys():
                        results[element] = []

                    results[element].append(dataset)
                    
                    # check for existing data
                    if model_data != {}:

                        # check for key in dict
                        if element in list(model_data.keys()):

                            if exp_data[element][i]["params"]['T / K '] == model_data[element][i]["params"]['T / K ']:
                                results[element][i] = model_data[element][i]
                                self.log.info("Already calculated {} data for {} | {}".format(element,self.fluid_mappings[system[0]], self.fluid_mappings[system[1]] ))
                                continue

                    # search for correct measurement dataset

                    T_search = exp_data[element][i]["params"]['T / K ']

                    model_dataset = None

                    for n in range(len(model_data['Isothermal phase equilibrium data'])):
                        
                        if model_data['Isothermal phase equilibrium data'][n]["params"]['T / K '] == T_search:

                            model_dataset = model_data['Isothermal phase equilibrium data'][n]
                            break
                        
                    if model_dataset == None:
                        continue

                    # get experimental isothermal data
                    for n in range(len(exp_data['Isothermal phase equilibrium data'])):
                        
                        if exp_data['Isothermal phase equilibrium data'][n]["params"] == model_dataset['params']:
                            exp_dataset = exp_data['Isothermal phase equilibrium data'][n]
                            break

                    exp_dataset, model_dataset, exp_x_system = self.check_xy_swap(system, exp_dataset, model_dataset, 'isotherm')

                    p_vals = np.array(list(list(zip(*model_dataset['measurements'][1:]))[0]))


                    if max(p_vals) - min(p_vals) < 0.1:
                        continue

                    azeo_point = self.get_azeo_point(dataset, model_dataset)

                    if azeo_point != {}:
                        results[element][i] = azeo_point
                        self.log.info("Added new dataset in {} for {} | {}.".format(element,self.fluid_mappings[system[0]], self.fluid_mappings[system[1]]))


                    


            if element == "blabla":
                pass
        
        # check all keys for model values
        for element in self.calc_vars:
            
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

        dirs = []

        path = os.path.join(self.data_dir,'../Modelle', self.model_name)
        dirs.append(path)

        path = os.path.join(self.data_dir,'../../Diagramme', self.model_name)
        dirs.append(path)

        for element in dirs:

            if os.path.isdir(element) == False:
                os.mkdir(element)


    def get_azeo_point(self, dataset, inputset):

        p_vals = np.array(list(list(zip(*inputset['measurements'][1:]))[0]))
        x1_vals = np.array(list(list(zip(*inputset['measurements'][1:]))[1]))
        y1_vals = np.array(list(list(zip(*inputset['measurements'][1:]))[2]))

        p_max_idx = np.argmax(p_vals)
        p_min_idx = np.argmin(p_vals)

        if p_max_idx > 0 and p_max_idx < len(p_vals):
            dataset['params']['P / bar '] = p_vals[p_max_idx]
            dataset['measurements'].append([x1_vals[p_max_idx], y1_vals[p_max_idx]])

        else:
            dataset['params']['P / bar '] = p_vals[p_min_idx]
            dataset['measurements'].append([x1_vals[p_min_idx], y1_vals[p_min_idx]])



        # Set T to inputset T value
        dataset['params']['T / K '] = inputset['params']['T / K ']
        
        return dataset


    def calc_h_mix(self, system, temp, press, x):
        
        fldmix = None
        fld1 = None
        fld2 = None
        hE = None
        h_mix = None
        h_fld1 = None
        h_fld2 = None
        errmix = None


        fld1_name = self.fluid_mappings[system[0]]
        fld2_name = self.fluid_mappings[system[1]]

            
        press = press/10  # MPa
        eqtype = 2 #Reinstoffgleichung: 1: Hochgenau, 2: SRK, 3: PR, 4: LKP, 6: PC-SAFT
        mixtype = 22 #Gemischmodell: 1: Multifluid-Gemischmodell, 2: SRK a quadratisch, b linear, 21: SRK a quadratisch, b quadratisch, 22: PSRK, 3: PR a quadratisch, b linear, 31: PR a quadratisch, b quadratisch, 32: VTPR

        # self.fldmix1 = Fluid('TP','HE',['methane','ethane'],[0.6,0.4],[1,1],1,self.trend_path,'molar',self.dll_path)
        fldmix = Fluid('TP','H',[fld1_name, fld2_name],[x, 1-x],[eqtype,eqtype],mixtype,self.trend_path,'molar',self.dll_path)
        
        fld1 = Fluid('TP','H',[fld1_name, fld2_name],[0.99999999,0.00000001],[eqtype,eqtype],mixtype,self.trend_path,'molar',self.dll_path)
        fld2 = Fluid('TP','H',[fld2_name, fld1_name],[0.99999999,0.00000001],[eqtype,eqtype],mixtype,self.trend_path,'molar',self.dll_path)        
        
        h_mix, errmix = fldmix.TREND_EOS_FIT(temp, press, self.COSMOparam)
        h_fld1, errmix = fld1.TREND_EOS_FIT(temp, press, self.COSMOparam)
        h_fld2, errmix = fld2.TREND_EOS_FIT(temp, press, self.COSMOparam)
        hE = h_mix - x * h_fld1 - (1-x) * h_fld2
        
        if errmix.value == 0:
            self.log.info("{}, x = {}, hE = {} J/mol".format(system,x,hE))

        else:
            self.log.info("{} hE calculation not possible. error = {}".format(system, errmix.value))


        return hE, errmix

    def calc_vap_pres(self, component, var , var_val):
        

        
        fld_name = self.fluid_mappings[component]

        if var == 'Tvap':
            calc_var = 'p'
        else:
            calc_var = 'T'
            var_val = var_val / 10

        eqtype = 2 #Reinstoffgleichung: 1: Hochgenau, 2: SRK, 3: PR, 4: LKP, 6: PC-SAFT
        mixtype = 22 

        fld1 = Fluid(var, calc_var,[fld_name],[1.0],[eqtype],mixtype,self.trend_path,'molar',self.dll_path)

        var_res, errmix = fld1.TREND_EOS_FIT(var_val, var_val, self.COSMOparam)

        if errmix.value == 0:
            self.log.info("{}, {} = {}".format(component, calc_var, var_res))

        else:
            self.log.info("{} {} calculation not possible. error = {}".format(component, var, errmix.value))
            
            
        return var_res, errmix

        

    def calc_heat_capa(self, system, temp, press, x):
        
        fldmix = None
        fld1 = None
        fld2 = None
        cp = None
        cp_mix = None
        cp_fld1 = None
        cp_fld2 = None
        errmix = None

        fld1_name = self.fluid_mappings[system[0]]
        fld2_name = self.fluid_mappings[system[1]]

        press = press/10  # MPa
        eqtype = 2 #Reinstoffgleichung: 1: Hochgenau, 2: SRK, 3: PR, 4: LKP, 6: PC-SAFT
        mixtype = 22 #Gemischmodell: 1: Multifluid-Gemischmodell, 2: SRK a quadratisch, b linear, 21: SRK a quadratisch, b quadratisch, 22: PSRK, 3: PR a quadratisch, b linear, 31: PR a quadratisch, b quadratisch, 32: VTPR

        # self.fldmix1 = Fluid('TP','HE',['methane','ethane'],[0.6,0.4],[1,1],1,self.trend_path,'molar',self.dll_path)
        fldmix = Fluid('TP','CP',[fld1_name, fld2_name],[x, 1-x],[eqtype,eqtype],mixtype,self.trend_path,'molar',self.dll_path)
        
        fld1 = Fluid('TP','CP',[fld1_name, fld2_name],[0.99999999,0.00000001],[eqtype,eqtype],mixtype,self.trend_path,'molar',self.dll_path)
        fld2 = Fluid('TP','CP',[fld2_name, fld1_name],[0.99999999,0.00000001],[eqtype,eqtype],mixtype,self.trend_path,'molar',self.dll_path)        

        cp_mix, errmix = fldmix.TREND_EOS_FIT(temp, press, self.COSMOparam)
        cp_fld1, errmix = fld1.TREND_EOS_FIT(temp, press, self.COSMOparam)
        cp_fld2, errmix = fld2.TREND_EOS_FIT(temp, press, self.COSMOparam)
        cp = cp_mix - x * cp_fld1 - (1-x) * cp_fld2
        
        if errmix.value == 0:
            self.log.info("{}, x = {}, cp = {} J/(mol*K)".format(system,x,cp))

        else:
            self.log.info("{} cp calculation not possible. error = {}".format(system, errmix.value))


        return cp, errmix



    def calc_phase_eq(self, system, var, var_val):

        fldmix = None

        values = {}

        lis = []

        fld1_name = self.fluid_mappings[system[0]]
        fld2_name = self.fluid_mappings[system[1]]
        
        eqtype = 2 #Reinstoffgleichung: 1: Hochgenau, 2: SRK, 3: PR, 4: LKP, 6: PC-SAFT
        mixtype = 22 #Gemischmodell: 1: Multifluid-Gemischmodell, 2: SRK a quadratisch, b linear, 21: SRK a quadratisch, b quadratisch, 22: PSRK, 3: PR a quadratisch, b linear, 31: PR a quadratisch, b quadratisch, 32: VTPR

        if var == 'pvap':
            var_val = var_val / 10

        # self.fldmix1 = Fluid('TP','HE',['methane','ethane'],[0.6,0.4],[1,1],1,self.trend_path,'molar',self.dll_path)
        fldmix = Fluid(var, 'CP', [fld1_name, fld2_name],[0.6,0.4],[eqtype,eqtype],mixtype,self.trend_path,'molar',self.dll_path)

        tmp_path = ''
        

        p_points_array, T_points_array, x_points, rhovap_points, rholiq_points, points, error = fldmix.PTXDIAG_FIT(var_val, self.COSMOparam, tmp_path)

        if error.value != 0:
            return values, lis, error.value

        if var == 'Tvap':
            lis.append(['p', "x", "y"])
            
            for i in range(points.value):
                element = p_points_array[i]
                values[element] = {}
                values[element]['x'] = x_points[2][i]
                values[element]['y'] = x_points[0][i]
                lis.append([p_points_array[i] * 10, x_points[2][i], x_points[0][i]])

        if var == 'pvap':
            lis.append(['T', "x", "y"])
            for i in range(points.value):
                element = T_points_array[i]
                values[element] = {}
                values[element]['x'] = x_points[2][i]
                values[element]['y'] = x_points[0][i]
                lis.append([T_points_array[i], x_points[2][i], x_points[0][i]])

        return values, lis, error.value