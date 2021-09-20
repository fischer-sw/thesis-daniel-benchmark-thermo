import numpy as np


from fluid import *

def check_xy_swap(logger, system, exp_data, model_data, mode):
    
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

            value_comp1, error_comp1 = calc_vap_pres(logger, system[0], var, par_val) #MPa
            value_comp2, error_comp2 = calc_vap_pres(logger, system[1], var, par_val) #MPa

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

            value_comp1, error_comp1 = calc_vap_pres(logger, system[0], var, par_val)
            value_comp2, error_comp2 = calc_vap_pres(logger, system[1], var, par_val)

            
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



def calc_vap_pres(logger, component, var , var_val):


        COSMOparam = (ct.c_double * COSMO_length)()
        COSMOparam[0] = 6525.69 * 4184.0
        COSMOparam[1] = 1.4859 * 10**8 * 4184.0
        COSMOparam[2] = 4013.78 * 4184.0
        COSMOparam[3] = 932.31 * 4184.0 
        COSMOparam[4] = 3016.43 * 4184.0
        COSMOparam[5] = 115.7023
        COSMOparam[6] = 117.4650
        COSMOparam[7] = 66.0691
        COSMOparam[8] = 95.6184
        COSMOparam[9] = -11.0549
        COSMOparam[10] = 15.4901
        COSMOparam[11] = 84.6268
        COSMOparam[12] = 109.6621
        COSMOparam[13] = 52.9318
        COSMOparam[14] = 104.2534
        COSMOparam[15] = 19.3477
        COSMOparam[16] = 141.1709
        COSMOparam[17] = 58.3301
        COSMOparam[18] = 115.70
        COSMOparam[19] = 76.89
        COSMOparam[20] = 85.37 


        trend_path = os.path.join(sys.path[0],'..','..','TREND 4.0')
        dll_path = os.path.join(sys.path[0],'TREND_FIT_DLL.dll')
        
        fluid_mappings = read_mappings("mappings")
        
        fld_name = fluid_mappings[component]

        if var == 'Tvap':
            calc_var = 'p'
        else:
            calc_var = 'T'
            var_val = var_val / 10

        eqtype = 2 #Reinstoffgleichung: 1: Hochgenau, 2: SRK, 3: PR, 4: LKP, 6: PC-SAFT
        mixtype = 22 

        fld1 = Fluid(var, calc_var,[fld_name],[1.0],[eqtype],mixtype,trend_path,'molar',dll_path)

        var_res, errmix = fld1.TREND_EOS_FIT(var_val, var_val, COSMOparam)

        if errmix.value == 0:
            logger.info("{}, {} = {}".format(component, calc_var, var_res))

        else:
            logger.info("{} {} calculation not possible. error = {}".format(component, var, errmix.value))
            
            
        return var_res, errmix

def read_mappings(filename):
        
        mappings_path = os.path.join(sys.path[0], "..", "..","Daten", filename + ".json")

        with open(mappings_path) as f:
            mappings = json.loads(f.read())

        return mappings