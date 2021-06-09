#!/usr/bin/python
import os
import json
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



    def create_results(self):

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

        return res

    
    def write_results_file(self, res):
        """
        Function to write results to file

        Arguments:
            res (dict): results dictionary
        """
        
        path = os.path.join(self.result_dir, self.model, self.test_name +'.json')
        with open(path, 'w') as outfile:
            json.dump(res, outfile, ensure_ascii=False, indent=2, sort_keys=True)

    
    def calc_sys_result(self, sys):
        """
        Function to cacluate all grades possible for one system

        Arguments:
            sys (str): System to calculate grades for
        Returns:
            dict: dictionary with all grades possible to calculate for the system
        """
        # get model data
        

        res_path = os.path.join(self.result_dir, self.model, self.test_name +'.json')
        mod_path = os.path.join(self.data_dir, 'Modelle', self.model ,sys +'.json')
        exp_path = os.path.join(self.data_dir, 'Experimente' ,sys + '.json')
        
        with open(res_path, 'r') as file:
            res = json.loads(file.read())

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


            elif key == "Isobaric phase equilibrium data" or key == "Isothermal phase equilibrium data":
                vals = [["x1", "y1"],["x2", "y2"]]
                mod_res, exp_res = self.get_param_data(mod_sets, exp_sets, 'Critical point', vals)
                

                
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
                    exp_val = exp_res[name][i]
                    mod_val = mod_res[name][i]

                    err = 0.5 * (self.MAPE([mod_val], [exp_val])+ self.MAPE([exp_val], [mod_val]))

                    if err > 80.0:
                        err = 80.0

                    sum += err

                mark_h_mix = 20 - 0.25 * 1/len(mod_res) * sum
                

                # write results
                res[BAC]['sys_res'][sys]["mark_h_mix"] = mark_h_mix

            elif key == "Heat capacity of mixing":
                vals = [["cp_mix"],[]]
                mod_res, exp_res = self.get_param_data(mod_sets, exp_sets, 'Heat capacity of mixing', vals)
                
                name = vals[0][0]

                sum = 0

                for i in range(len(mod_res[name])):
                    exp_val = exp_res[name][i]
                    mod_val = mod_res[name][i]

                    err = 0.5 * (self.MAPE([mod_val], [exp_val])+ self.MAPE([exp_val], [mod_val]))

                    if err > 200.0:
                        err = 200.0

                    sum += err

                mark_cp_mix = 20 - 0.1 * 1/len(mod_res) * sum
                

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
        for i in range(len(model_data)):
            model_ele = model_data[i] 
            exp_ele = exp_data[i]
            for j in range(len(model_ele['measurements'])):
                for k in values[0] + values[1]:
                    # create lists
                    if not k in model_res:
                        model_res[k] = []
                        exp_res[k] = []
                    
                    # get index
                    header = model_ele['measurements'][0]
                    v = 'NaN'
                    for value in range(len(header)):
                        if k in header[value]:
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


                    if k in values[0] and v != 'NaN':
                        ele = model_ele['measurements'][j][v]
                        if type(ele) != type(""):
                            model_res[k].append(ele)
                            exp_res[k].append(exp_ele['measurements'][j][v])
                        else:
                            continue

                    elif k in values[1]:
                        if k[-1] == '2' and model_res[k[0]+"1"] != [] :
                            model_res[k].append(1 - model_res[k[0]+"1"][-1])
                            exp_res[k].append(1 - exp_res[k[0]+"1"][-1])

                        

        return model_res , exp_res 

