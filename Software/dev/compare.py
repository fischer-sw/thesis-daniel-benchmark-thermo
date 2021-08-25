#!/usr/bin/python
import os
import sys
import json
from shutil import copyfile
#from typing_extensions import ParamSpec
import numpy as np
import logging



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


        self.res_vars = ['mark_h_mix', 'mark_cp_mix']
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
            res["model_res"] = {}
            res["group_res"] = {
                "mark_NA" : {},
                "mark_SA" : {},
                "mark_CA" : {},
                "mark_CA_SA" : {}
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

                res[key]["group_res"][element] = mark_sum/sys_count
                self.log.info("{} group results {} = {}".format(key, element, mark_sum/sys_count))

        return res

    def calc_group_results(self):
        
        res = self.calc_bac_results()

        for element in self.res_vars:

            mark_NA_list = []

            mark_SA_list = []

            mark_CA_list = []

            mark_CA_SA_list = []

            for i in range(1,10):
                bac = "BAC" + str(i)
                
                if i in range(1,5):
                    
                    if element in list(res[bac]["group_res"].keys()):
                        mark_NA_list.append(res[bac]["group_res"][element])
                    continue

                if i == 5:
                    
                    if element in list(res[bac]["group_res"].keys()):
                        mark_SA_list.append(res[bac]["group_res"][element])
                    continue

                if i == 6:
                    
                    if element in list(res[bac]["group_res"].keys()):
                        mark_CA_list.append(res[bac]["group_res"][element])
                    continue


                if i in range(7,10):
                    
                    if element in list(res[bac]["group_res"].keys()):
                        mark_CA_SA_list.append(res[bac]["group_res"][element])
                    continue
                
            
            # calc marks
            if mark_NA_list != []:
                mark_NA = sum(mark_NA_list)/(len(mark_NA_list))
                res["group_res"]["mark_NA"][element] = mark_NA
                self.log.info("mark_NA {} = {}".format(element, mark_NA))

            if mark_SA_list != []:
                mark_SA = sum(mark_SA_list)/(len(mark_SA_list))
                res["group_res"]["mark_SA"][element] = mark_SA
                self.log.info("mark_SA {} = {}".format(element, mark_SA))

            if mark_CA_list != []:
                mark_CA = sum(mark_CA_list)/(len(mark_CA_list))
                res["group_res"]["mark_CA"][element] = mark_CA
                self.log.info("mark_CA {} = {}".format(element, mark_CA))

            if mark_CA_SA_list != []:
                mark_CA_SA = sum(mark_CA_SA_list)/(len(mark_CA_SA_list))
                res["group_res"]["mark_CA_SA"][element] = mark_CA_SA
                self.log.info("mark_CA_SA {} = {}".format(element, mark_CA_SA))

        return res

    def calc_model_results(self):
        """
        Function that calculates model results from BAC results
        """

        res = self.calc_group_results()

        marks = ["mark_NA", "mark_SA", "mark_CA", "mark_CA_SA"]

        for element in self.res_vars:

            mark_list = []

            for mark in marks:
                if element in list(res["group_res"][mark]):
                    mark_list.append(res["group_res"][mark][element])
            
            if mark_list != []:
                model_mark = sum(mark_list)/len(mark_list)
                res["model_res"][element] = model_mark
                self.log.info("model_mark {} = {}".format(element, model_mark))

                
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
        

        
        mod_path = os.path.join(self.data_dir, 'Modelle', self.model ,sys +'.json')
        exp_path = os.path.join(self.data_dir, 'Experimente' ,sys + '.json')
        

        with open(mod_path, 'r') as file:
            model_data = json.loads(file.read())

        with open(exp_path, 'r') as file:
            exp_data = json.loads(file.read())

        # calculate MAPEs
        for key, val in model_data.items():
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
                mod_res, exp_res = self.get_param_data(mod_sets, exp_sets, 'Critical point', vals)

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
                mod_res, exp_res = self.get_param_data(mod_sets, exp_sets, 'Azeotropic point', vals)
                
                # add P mod_res
                mod_res["P"] = []
                for i in range(len(mod_res["x1"])):
                    mod_res["P"].append(mod_sets[i]["params"]["P / bar "])

                # add P exp_res
                exp_res["P"] = []
                for i in range(len(exp_res["x1"])):
                    exp_res["P"].append(exp_sets[i]["params"]["P / bar "])

                MPAE_p_az = self.MAPE(mod_res["P"], exp_res["P"])
                MPAE_x1_az = self.MAPE(mod_res["x1"], exp_res["x1"])
                MPAE_x2_az = self.MAPE(mod_res["x2"], exp_res["x2"])
                
                mark_paz = 20 - 0.75 * MPAE_p_az

                mark_xaz = 20 - 0.5 * (MPAE_x1_az + MPAE_x2_az)/2  
                
                # write results
                res[BAC]['sys_res'][sys]["mark_paz"] = mark_paz
                res[BAC]['sys_res'][sys]["mark_xaz"] = mark_xaz

            elif key == "Isobaric phase equilibrium data" or key == "Isothermal phase equilibrium data":
                vals = [["x1", "y1"],["x2", "y2"]]
                mod_res, exp_res = self.get_param_data(mod_sets, exp_sets, 'phase equilibrium data', vals)
                
                # check if enough data is available
                if mod_res["x1"] == [] or mod_res["x2"] == [] or mod_res["y1"] == [] or mod_res["y2"] == []:
                    continue

                if exp_res["x1"] == [] or exp_res["x2"] == [] or exp_res["y1"] == [] or exp_res["y2"] == []:
                    continue
                
                for i in range(len(mod_res)):

                    x1_exp_val = exp_res["x1"][i]
                    x2_exp_val = exp_res["x2"][i]
                    y1_exp_val = exp_res["y1"][i]
                    y2_exp_val = exp_res["y2"][i]

                    x1_mod_val = mod_res["x1"][i]
                    x2_mod_val = mod_res["x2"][i]
                    y1_mod_val = mod_res["y1"][i]
                    y2_mod_val = mod_res["y2"][i]

                    pct_err_x1 = abs(x1_exp_val - x1_mod_val)/ x1_exp_val * 100
                    pct_err_x2 = abs(x2_exp_val - x2_mod_val)/ x2_exp_val * 100
                    pct_err_y1 = abs(y1_exp_val - y1_mod_val)/ y1_exp_val * 100
                    pct_err_y2 = abs(y2_exp_val - y2_mod_val)/ y2_exp_val * 100


                    # check x
                    if (x1_exp_val < 0.01 or x1_exp_val > 0.99) and 0.5 * (pct_err_x1+ pct_err_x2)/2 > 45.0: 
                        mod_res["x1"].remove(mod_res["x1"][i])
                        mod_res["x2"].remove(mod_res["x2"][i])

                    # check y
                    if (y1_exp_val < 0.01 or y1_exp_val > 0.99) and 0.5 * (pct_err_y1+ pct_err_y2)/2 > 45.0: 
                        mod_res["y1"].remove(mod_res["y1"][i])
                        mod_res["y2"].remove(mod_res["y2"][i])




                MPAE_x1 = self.MAPE(mod_res["x1"], exp_res["x1"])
                MPAE_x2 = self.MAPE(mod_res["x2"], exp_res["x2"])
                
                MPAE_y1 = self.MAPE(mod_res["y1"], exp_res["y1"])
                MPAE_y2 = self.MAPE(mod_res["y2"], exp_res["y2"])

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
                mod_res, exp_res = self.get_param_data(mod_sets, exp_sets, 'Enthalpy of mixing', vals)
                
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
                mod_res, exp_res = self.get_param_data(mod_sets, exp_sets, 'Heat capacity of mixing', vals)
                
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
                

                # write results
                res[BAC]['sys_res'][sys]["mark_cp_mix"] = mark_cp_mix

            else:
                self.log.info("{}, Key '{}' wird bisher nicht verwendet".format(sys,key))
        
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
        return np.mean(np.abs((model[exp != 0] - exp[exp != 0])/exp[exp != 0])) * 100



    def get_param_data(self, model_data, exp_data, param, values):
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
                # Experiment Data
                exp_mes_data = exp_mes["measurements"]
                if len(exp_mes_data) > 2:
                    exp_vals = list(list(zip(*exp_mes["measurements"][1:-1]))[v])
                else:
                    exp_vals = [exp_mes["measurements"][-1][v]]
                exp_res[k] += exp_vals

                # Modell Data
                mod_mes_data = mod_mes["measurements"]
                if len(mod_mes_data) > 2:
                    mes_vals = list(list(zip(*mod_mes["measurements"][1:-1]))[v])
                else:
                    mes_vals = [mod_mes["measurements"][-1][v]]
                model_res[k] += mes_vals
            
                # check if calculation is needed:
                first_chrs = []
                if values[1] != []:
                    first_chrs =  list(list(zip(*values[1]))[0])

                if len(k) > 1 and k[0] in first_chrs:
                    mod_calc_vals = [1-x for x in mes_vals]
                    exp_calc_vals = [1-x for x in exp_vals]

                    model_res[k[0]+ "2"] += mod_calc_vals
                    exp_res[k[0]+ "2"] += exp_calc_vals

        return model_res , exp_res 

