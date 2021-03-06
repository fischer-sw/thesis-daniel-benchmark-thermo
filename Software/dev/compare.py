#!/usr/bin/python
import os
import sys
import json
import math
from shutil import copyfile
import numpy as np
import logging

from check_phase_eq_direction import *

class Comparison:

    

    def __init__(self, data_dir, result_dir, model_name, test_name, logger=None):
        """
        Constructor of comparison class

        Arguments:
            data_dir (str): Path to data from experiments (e.g. ../../Datenbank)
            result_dir (str): Path to store results to
            model_name (str): Name of model (results in filename)
            test_name (str): Name of Test to execute
            logger (obj): Logging object 
        """

        if logger == None:
            self.log = logging.getLogger(__file__)
        else:
            self.log = logger
        self.test_name = test_name
        self.data_dir = data_dir
        self.result_dir = result_dir
        self.model = model_name
        self.setup_test_model()
        self.init_results()

        marks = ['mark_h_mix', 'mark_cp_mix', 'mark_isoth_x' ,'mark_isoth_y', 'mark_isob_x', 'mark_isob_y', 'mark_paz', 'mark_xaz']

        self.res_vars = marks
        self.bacs = list(range(1,10))
     

    def setup_model(self, name):
        """
        Function that sets up Test Model

        Arguments:
            name (str): Model Name
        """
        
        # create model folder
        path = os.path.join(sys.path[0],'..', '..', 'Datenbank', 'Modelle', name)
        os.makedirs(path, exist_ok=True)

        # create results folcer
        path = os.path.join(sys.path[0],'..', '..', 'Ergebnisse', name)
        os.makedirs(path, exist_ok=True)

    def setup_test_model(self):
        
        # create folder
        name = "Test_Modell"
        self.setup_model(name)

        # reset results file
        file = os.listdir(os.path.join(self.result_dir, self.model))
        for f in file:
            os.remove(os.path.join(self.result_dir, self.model, f))


    def init_results(self):

        """
        Function to initialize results file

        Returns:
            dict: dictionary with results structure
        """
        res = {}
        for i in range(1,10):
            res["BAC"+str(i)] = {}
            res["BAC"+str(i)]["group_res"] = {}
            res["BAC"+str(i)]["sys_res"] = {}
            res["model_res"] = 0.0
            res["class_res"] = {
                "mark_NA" : 0.0,
                "mark_SA" : 0.0,
                "mark_CA" : 0.0,
                "mark_CA_SA" : 0.0
            }
        
        # check if file exisits:
        path = os.path.join(self.result_dir, self.model, self.test_name +'.json')
        if not os.path.isfile(path):
            self.write_results_file(res)

    
    def write_results_file(self, res):
        """
        Function to write results to file

        Arguments:
            res (dict): results dictionary
        """
        
        path = os.path.join(self.result_dir, self.model, self.test_name +'.json')
        with open(path, 'w') as outfile:
            json.dump(res, outfile, ensure_ascii=False, indent=2, sort_keys=True)

    
    def create_sys_results(self):
        """
        Function that creates results for all systems in model directory

        """
        res_path = os.path.join(self.result_dir, self.model, self.test_name +'.json')
        path = os.path.join(sys.path[0],'..', '..', 'Datenbank', 'Modelle', self.model)

        with open(res_path, 'r') as file:
            res = json.loads(file.read())

        systems = os.listdir(path)

        # remove backup from data
        if "0_backup.zip" in systems:
            systems.remove("0_backup.zip")

        for element in systems:
            sys_name = element.split('.json')[0]
            
            mod_path = os.path.join(path, element)

            with open(mod_path, 'r') as file:
                model_data = json.loads(file.read())

            BAC = model_data
            res = self.calc_sys_results(sys_name, res)
        
        return res


    def calc_bac_results(self):
        """
        Function that calculates BAC results
        """


        

        res_path = os.path.join(self.result_dir, self.model, self.test_name +'.json')
        
        with open(res_path, 'r') as file:
            res = json.loads(file.read())


        # check if sys results are there
        check = False
        for i in self.bacs:
            BAC = "BAC" + str(i)
            if res[BAC]["sys_res"] == {}:
                check = True

        if check == True:
           res = self.create_sys_results()


        for element in self.res_vars:

            

            for key in res.keys():

                mark_sum = 0
                sys_count = 0
                
                if key[0:3] != "BAC" or len(res[key]["sys_res"]) == 0:
                    continue
                for system in res[key]["sys_res"].keys():
                    
                    if not element in res[key]["sys_res"][system].keys():
                        continue

                    mark_sum += res[key]["sys_res"][system][element]
                    sys_count += 1

                if sys_count != 0:

                    res[key]["group_res"][element] = mark_sum/sys_count
                    self.log.info("{} group results {} = {}".format(key, element, mark_sum/sys_count))

                    # combine phase eq grades if they both exsist

                    if 'mark_isob_x' in res[key]["group_res"].keys() and 'mark_isoth_x' in res[key]["group_res"].keys():
                        mark_phase_eq_x = (res[key]["group_res"]['mark_isob_x'] + res[key]["group_res"]['mark_isoth_x']) / 2
                        res[key]["group_res"]['mark_phase_eq_x'] = mark_phase_eq_x
                        self.log.info("{} group results mark_phase_eq_x = {}".format(key, mark_phase_eq_x))
                        res[key]["group_res"].pop('mark_isob_x')
                        res[key]["group_res"].pop('mark_isoth_x')


                    if 'mark_isob_y' in res[key]["group_res"].keys() and 'mark_isoth_y' in res[key]["group_res"].keys():
                        mark_phase_eq_y = (res[key]["group_res"]['mark_isob_y'] + res[key]["group_res"]['mark_isoth_y']) / 2 
                        res[key]["group_res"]['mark_phase_eq_y'] = mark_phase_eq_y
                        self.log.info("{} group results mark_phase_eq_y = {}".format(key, mark_phase_eq_y))
                        res[key]["group_res"].pop('mark_isob_y')
                        res[key]["group_res"].pop('mark_isoth_y')


                   
        

        

        

        return res

    def calc_group_results(self):

        """
        Function that calcultes group results
        """
        
        res = self.calc_bac_results()

        

        mark_NA_list = []

        mark_SA_list = []

        mark_CA_list = []

        mark_CA_SA_list = []

        for i in range(1,10):
            bac = "BAC" + str(i)


            #calculate bac results

            tmp = []
            for element in list(res[bac]["group_res"].keys()):
                tmp.append(res[bac]["group_res"][element])

            if len(tmp) != 0:
                res[bac]["res"] = sum(tmp)/len(tmp)

            # append bac results to class list
            if i in range(1,5):
                if 'res' in res[bac].keys():
                    mark_NA_list.append(res[bac]["res"])
                    continue

            if i == 5:
                if 'res' in res[bac].keys():
                    
                    mark_SA_list.append(res[bac]["res"])
                    continue
                

            if i == 6:
                if 'res' in res[bac].keys():
                    
                    mark_CA_list.append(res[bac]["res"])
                    continue


            if i in range(7,10):
                if 'res' in res[bac].keys():
                    
                    mark_CA_SA_list.append(res[bac]["res"])
                    continue
                
            
        # calc class marks
        if mark_NA_list != []:
            mark_NA = sum(mark_NA_list)/(len(mark_NA_list))
            res["class_res"]["mark_NA"] = mark_NA
            self.log.info("mark_NA = {}".format(mark_NA))

        if mark_SA_list != []:
            mark_SA = sum(mark_SA_list)/(len(mark_SA_list))
            res["class_res"]["mark_SA"] = mark_SA
            self.log.info("mark_SA = {}".format(mark_SA))

        if mark_CA_list != []:
            mark_CA = sum(mark_CA_list)/(len(mark_CA_list))
            res["class_res"]["mark_CA"] = mark_CA
            self.log.info("mark_CA = {}".format(mark_CA))

        if mark_CA_SA_list != []:
            mark_CA_SA = sum(mark_CA_SA_list)/(len(mark_CA_SA_list))
            res["class_res"]["mark_CA_SA"] = mark_CA_SA
            self.log.info("mark_CA_SA = {}".format(mark_CA_SA))

        return res

    def calc_model_results(self):
        """
        Function that calculates model results from BAC results
        """

        res = self.calc_group_results()

        marks = ["mark_NA", "mark_SA", "mark_CA", "mark_CA_SA"]

        
        mark_list = []

        for mark in marks:
            
            mark_list.append(res["class_res"][mark])
        
        if mark_list != []:
            model_mark = sum(mark_list)/len(mark_list)
            res["model_res"] = model_mark
            self.log.info("model_mark = {}".format(model_mark))

                
        return res

    


    def calc_sys_results(self, sys, res):
        """
        Function to cacluate all grades possible for one system

        Arguments:
            sys (str): System to calculate grades for
        Returns:
            dict: dictionary with all grades possible to calculate for the system
        """
        # get model data
        
        system = []
        system.append(sys.split('_')[0])
        system.append(sys.split('_')[1])  
        
        mod_path = os.path.join(self.data_dir, 'Modelle', self.model ,sys +'.json')
        exp_path = os.path.join(self.data_dir, 'Experimente' ,sys + '.json')
        

        with open(mod_path, 'r') as file:
            model_data = json.loads(file.read())

        with open(exp_path, 'r') as file:
            exp_data = json.loads(file.read())

        # calculate MAPEs
        for key in model_data.keys():
            if key in ["BAC","sheet"]:
                continue
            
            mod_sets = model_data[key]
            exp_sets = exp_data[key]
            # create results dataset if not available
            BAC = "BAC" + str(model_data["BAC"])

            if not sys in res[BAC]['sys_res'].keys():
                res[BAC]['sys_res'][sys] = {}

            if key == "Critical point":
                vals = [["P", "x1"],["x2"]]
                mod_res, exp_res = self.get_param_data(mod_sets, exp_sets, 'Critical point', vals, system)

                MPAE_p = self.MAPE(mod_res["P"], exp_res["P"])
                MPAE_x1 = self.MAPE(mod_res["x1"], exp_res["x1"])
                MPAE_x2 = self.MAPE(mod_res["x2"], exp_res["x2"])
                
                mark_pc = 20 - 0.75 * MPAE_p

                mark_xc = 20 - 0.5 * (MPAE_x1 + MPAE_x2)/2  
                
                # write results
                res[BAC]['sys_res'][sys]["mark_pc"] = mark_pc
                res[BAC]['sys_res'][sys]["mark_xc"] = mark_xc

            elif key == "Azeotropic point":
                
                vals = [["x1"],["x2"]]
                mod_res, exp_res = self.get_param_data(mod_sets, exp_sets, 'Azeotropic point', vals, system)
                
                # add P mod_res
                mod_res["P"] = []
                for i in range(len(mod_res['x1'])):
                    mod_res["P"].append(mod_sets[i]["params"]["P / bar "])

                # add P exp_res
                exp_res["P"] = []
                for i in range(len(exp_res['x1'])):
                    exp_res["P"].append(exp_sets[i]["params"]["P / bar "])

                MPAE_p_az = self.MAPE(mod_res["P"], exp_res["P"])

                if MPAE_p_az > 80/3:
                    MPAE_p_az = 80/3

                MPAE_x1_az = self.MAPE(mod_res["x1"], exp_res["x1"])
                MPAE_x2_az = self.MAPE(mod_res["x2"], exp_res["x2"])

                if MPAE_x1_az > 40:
                    MPAE_x1_az = 40

                if MPAE_x2_az > 40:
                    MPAE_x2_az = 40
                
                mark_paz = 20 - 0.5 * MPAE_p_az

                mark_xaz = 20 - 0.5 * (MPAE_x1_az + MPAE_x2_az)/2  
                
                # write results
                res[BAC]['sys_res'][sys]["mark_paz"] = mark_paz
                res[BAC]['sys_res'][sys]["mark_xaz"] = mark_xaz

            elif key == "Isobaric phase equilibrium data" or key == "Isothermal phase equilibrium data":
                vals = [["x1", "y1"],["x2", "y2"]]

                

                mod_res, exp_res = self.get_param_data(mod_sets, exp_sets, 'phase equilibrium data', vals, system)
                
                # check if enough data is available
                if mod_res["x1"] == [] or mod_res["x2"] == [] or mod_res["y1"] == [] or mod_res["y2"] == []:
                    continue

                if exp_res["x1"] == [] or exp_res["x2"] == [] or exp_res["y1"] == [] or exp_res["y2"] == []:
                    continue
                

                

                mod_res_tmp = mod_res
                exp_res_tmp = exp_res
                i = 0

                # get minimal length

                min_len = min([len(exp_res["x1"]), len(exp_res["y1"]), len(mod_res["x1"]), len(mod_res["x1"])])

                exp_res["x1"] = exp_res["x1"][:min_len]
                exp_res["x2"] = exp_res["x2"][:min_len]
                exp_res["y1"] = exp_res["y1"][:min_len]
                exp_res["y2"] = exp_res["y2"][:min_len]

                mod_res["x1"] = mod_res["x1"][:min_len]
                mod_res["x2"] = mod_res["x2"][:min_len]
                mod_res["y1"] = mod_res["y1"][:min_len]
                mod_res["y2"] = mod_res["y2"][:min_len]



                while i < len(mod_res_tmp['x1']):

                    x1_exp_val = exp_res["x1"][i]
                    x2_exp_val = exp_res["x2"][i]
                    y1_exp_val = exp_res["y1"][i]
                    y2_exp_val = exp_res["y2"][i]

                    x1_mod_val = mod_res["x1"][i]
                    x2_mod_val = mod_res["x2"][i]
                    y1_mod_val = mod_res["y1"][i]
                    y2_mod_val = mod_res["y2"][i]

                    if x1_exp_val == 0 or x2_exp_val == 0 or y1_exp_val == 0 or y2_exp_val == 0:
                        i += 1
                        continue

                    pct_err_x1 = abs(x1_exp_val - x1_mod_val)/ x1_exp_val * 100
                    pct_err_x2 = abs(x2_exp_val - x2_mod_val)/ x2_exp_val * 100
                    pct_err_y1 = abs(y1_exp_val - y1_mod_val)/ y1_exp_val * 100
                    pct_err_y2 = abs(y2_exp_val - y2_mod_val)/ y2_exp_val * 100


                    # check x and y
                    if ((x1_exp_val < 0.01 or x1_exp_val > 0.99) and 0.5 * (pct_err_x1+ pct_err_x2)/2 > 45.0) or ((y1_exp_val < 0.01 or y1_exp_val > 0.99) and 0.5 * (pct_err_y1+ pct_err_y2)/2 > 45.0): 
                        
                        # delte model datapoint
                        mod_res_tmp["x1"].remove(mod_res["x1"][i])
                        mod_res_tmp["x2"].remove(mod_res["x2"][i])
                        mod_res_tmp["y1"].remove(mod_res["y1"][i])
                        mod_res_tmp["y2"].remove(mod_res["y2"][i])

                        # delete exp datapoint
                        exp_res_tmp["x1"].remove(exp_res["x1"][i])
                        exp_res_tmp["x2"].remove(exp_res["x2"][i])
                        exp_res_tmp["y1"].remove(exp_res["y1"][i])
                        exp_res_tmp["y2"].remove(exp_res["y2"][i])
                        i -= 1 

                    i += 1

                # check if enough data is available
                if mod_res["x1"] == [] or mod_res["x2"] == [] or mod_res["y1"] == [] or mod_res["y2"] == []:
                    continue

                if exp_res["x1"] == [] or exp_res["x2"] == [] or exp_res["y1"] == [] or exp_res["y2"] == []:
                    continue

                MPAE_x1 = self.MAPE(mod_res_tmp["x1"], exp_res_tmp["x1"])
                if MPAE_x1 > 40:
                    MPAE_x1 = 40.0
                
                MPAE_x2 = self.MAPE(mod_res_tmp["x2"], exp_res_tmp["x2"])
                if MPAE_x2 > 40:
                    MPAE_x2 = 40.0

                MPAE_y1 = self.MAPE(mod_res_tmp["y1"], exp_res_tmp["y1"])
                if MPAE_y1 > 40:
                    MPAE_y1 = 40.0

                MPAE_y2 = self.MAPE(mod_res_tmp["y2"], exp_res_tmp["y2"])
                if MPAE_y2 > 40:
                    MPAE_y2 = 40.0

                mark_x = 20 - 0.5 * (MPAE_x1 + MPAE_x2)/2
                mark_y = 20 - 0.5 * (MPAE_y1 + MPAE_y2)/2


                # write results
                if key == "Isothermal phase equilibrium data":
                    res[BAC]['sys_res'][sys]["mark_isoth_x"] = mark_x
                    res[BAC]['sys_res'][sys]["mark_isoth_y"] = mark_y
                
                if key == "Isobaric phase equilibrium data":
                    res[BAC]['sys_res'][sys]["mark_isob_x"] = mark_x
                    res[BAC]['sys_res'][sys]["mark_isob_y"] = mark_y
                

            elif key == "Enthalpy of mixing":
                
                vals = [["h_mix"],[]]
                mod_res, exp_res = self.get_param_data(mod_sets, exp_sets, 'Enthalpy of mixing', vals, system)
                
                name = vals[0][0]

                sum = 0
                

                for i in range(len(mod_res[name])):

                    err = 0

                    exp_val = exp_res[name][i]
                    mod_val = mod_res[name][i]

                    # err = 0.5 * (self.MAPE([mod_val], [exp_val])+ self.MAPE([exp_val], [mod_val]))

                    if exp_val != 0.0 and mod_val != 0.0:
                        err = 0.5 * (100 * abs((exp_val - mod_val)/exp_val) + 100 * abs((exp_val - mod_val)/mod_val))

                    if err > 80.0:
                        err = 80.0

                    sum += err

                mark_h_mix = 20 - 0.25 * 1/len(mod_res["h_mix"]) * sum

                # write results
                res[BAC]['sys_res'][sys]["mark_h_mix"] = mark_h_mix

            elif key == "Heat capacity of mixing":

                vals = [["cp_mix"],[]]
                mod_res, exp_res = self.get_param_data(mod_sets, exp_sets, 'Heat capacity of mixing', vals, system)
                
                name = vals[0][0]

                sum = 0

                for i in range(len(mod_res[name])):

                    err = 0

                    exp_val = exp_res[name][i]
                    mod_val = mod_res[name][i]

                    if exp_val != 0.0 and mod_val != 0.0:
                        err = 0.5 * (100 * abs((exp_val - mod_val)/exp_val) + 100 * abs((exp_val - mod_val)/mod_val))

                    if err > 200.0:
                        err = 200.0

                    sum += err

                mark_cp_mix = 20 - 0.1 * 1/len(mod_res["cp_mix"]) * sum
                if abs(mark_cp_mix) < 1.0e-4:
                    mark_cp_mix = 0.0

                # write results
                res[BAC]['sys_res'][sys]["mark_cp_mix"] = mark_cp_mix

            else:
                self.log.info("{}, Key '{}' wird bisher nicht verwendet".format(sys,key))
        
        if list(model_data.keys()) != ['BAC']:
            self.log.info("{},{}".format(sys,res[BAC]['sys_res'][sys]))
        return res


    def MAPE(self, model, exp):
        """ Function to calculate Mean Average Percentage Error

        Arguments:
            model (list): model data
            exp (list): experimental data

        Returns:
            float: MPAE [%]

        """
        model , exp = np.array(model[0:]), np.array(exp[0:])

        if len(model) > 1 and len(exp) > 1:
            res = np.mean(np.abs((model[exp != 0] - exp[exp != 0])/exp[exp != 0])) * 100
            if math.isnan(res) == False:
                return res
            else:
                return 0.0

        else:
            if float(exp[0]) != 0.0:
                return np.mean(np.abs((float(model[0]) - float(exp[0]))/float(exp[0]))) * 100
            else:
                return 0.0


    def get_param_data(self, model_data, exp_data, param, values, system):
        """ Function to get parameter data

        Arguments:
            model_data (dict): dictionary containing all model data for a specific system
            exp_data (dict): dictionary containing all experimental data for a specific system
            param (str): Parameter to look for e.g. 'Enthalpy of mixing'
            values (list): variables to look for and that are calculated e.g. [["x1", "y1"],["x2", "y2"]] x1 and y1 are looked for, x2 and y2 are calculated

        Returns:
            dict: mod_res contains all data found and calculated for the model
            dict: exp_res contains all data found and calculated for the experiment

        """

        exp_res = {}
        model_res = {}

        # create keys
        for k in values[0] + values[1]:
            # create lists
            if not k in model_res:
                model_res[k] = []
                exp_res[k] = []

        # get header of first element (all headers are the same)
        model_ele = model_data[0] 

        header = model_ele['measurements'][0]
        
        # loop through needed values
        for k in values[0]:
        
            # get all needed values
            for i in range(len(model_data)):
                mod_mes = model_data[i]
                exp_mes = exp_data[i]

                header = mod_mes["measurements"][0]

                v = 'NaN'
                # check header of model data for position
                for value in range(len(header)):

                    element = header[value]

                    if k in element:
                        v = value
                    
                    # check for x_1, x_2, y_1 and y_2
                    if ord(header[value][-1]) == 8321 and k[0] == header[value][0]:
                        v = value
                    
                    # check for h_mix
                    if param == "Enthalpy of mixing" and header[value] == "h\u1d39 / J.mol\u207b\u00b9":
                        v = value

                    # check for cp_mix
                    if param == "Heat capacity of mixing" and header[value] == "c\u1d18\u1d39 / J.mol\u207b\u00b9.K\u207b\u00b9":
                        v = value


                if v == 'NaN':
                    continue
                

                exp_mes_data = exp_mes["measurements"]
                mod_mes_data = mod_mes["measurements"]

                if param != 'phase equilibrium data':

                    # add add data normaly (n model = n exp)
                    
                    # Experiment Data
                    if len(exp_mes_data) > 2:
                        exp_vals = list(list(zip(*exp_mes["measurements"][1:]))[v])
                    else:
                        exp_vals = [exp_mes["measurements"][-1][v]]
                    exp_res[k] += exp_vals

                    # Modell Data

                    if len(mod_mes_data) > 2:
                        mes_vals = list(list(zip(*mod_mes["measurements"][1:]))[v])
                    else:
                        mes_vals = [mod_mes["measurements"][-1][v]]
                    model_res[k] += mes_vals


                else:

                    # merge data (n model > n exp)

                    # check if variables need to be switched

                    if mod_mes_data[0][0].replace(" ", "") == 'T/K':
                        mode = 'isobar'
                    else:
                        mode = 'isotherm'

                    # search for experimental data to match model data

                    for l in range(len(exp_data)):
                        test_set = exp_data[l]
                        if test_set["params"] == mod_mes["params"]:
                            exp_mes = test_set

                    exp_mes, mod_mes, changed = check_xy_swap(self.log, system, exp_mes, mod_mes, mode)

                    exp_mes_data = exp_mes['measurements']

                    mod_mes_data = mod_mes['measurements']

                    # get all p/T values


                    mes_vals = []
                    exp_vals = []

                    if len(mod_mes["measurements"]) == 1 or len(exp_mes["measurements"]) == 1:
                        return model_res , exp_res 

                    mes_var_vals = list(list(zip(*mod_mes["measurements"][1:]))[0])

                    # get max and min p/T values
                    max_value = max(mes_var_vals)
                    min_value = min(mes_var_vals)

                    for datarow in exp_mes_data:
                        if datarow == ['P / bar', 'x???', 'y???'] or datarow == ['T / K', 'x???', 'y???'] or datarow == ['P / bar', 'x??????', 'x??????', 'y???'] or datarow == header or len(datarow) != 3:
                            continue

                        # serach for closest value
                        search_val = datarow[0]

                        dist = 1000
                        dist_abs = 1000

                        closest_row = []

                        for row in mod_mes_data:
                            if row == header or type(row[0]) == type(''):
                                continue
                            new_dist_abs = abs(search_val - row[0])
                            new_dist = search_val - row[0]
                            
                            if new_dist_abs < dist_abs:
                                dist = new_dist
                                closest_row = row
                                dist_abs = new_dist_abs

                        if search_val < min_value or search_val > max_value:
                            continue
                        
                        if v < len(closest_row) and v < len(datarow) and type(closest_row[v]) != type('') and type(datarow[v]) != type('') and closest_row != []:
                            mes_vals.append(closest_row[v])
                            exp_vals.append(datarow[v])

                        
                    
                    # if (type(mes_vals[1]) != type('') and type(mes_vals[2]) != type('')):
                    model_res[k] += mes_vals
                    # if (type(exp_vals[1]) != type('') and type(exp_vals[2]) != type('')):
                    exp_res[k] += exp_vals

                # check if calculation is needed:

                # clean mes_vals
                j = 0
                while j < len(mes_vals):
                    mes_ele = mes_vals[j]
                    if type(mes_ele) == type(''):
                        mes_vals.remove(mes_ele)
                    else:
                        j += 1

                j = 0
                while j < len(exp_vals):
                    exp_ele = exp_vals[j]
                    if type(exp_ele) == type(''):
                        exp_vals.remove(exp_ele)
                    else:
                        j += 1



                if mes_vals != [] and exp_vals != []:
                    first_chrs = []
                    if values[1] != []:
                        first_chrs =  list(list(zip(*values[1]))[0])

                    if len(k) > 1 and k[0] in first_chrs:

                        mod_calc_vals = [1-x for x in mes_vals]
                        exp_calc_vals = [1-x for x in exp_vals]

                        model_res[k[0]+ "2"] += mod_calc_vals
                        exp_res[k[0]+ "2"] += exp_calc_vals

        return model_res , exp_res 

