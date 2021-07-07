#!/usr/bin/python

import logging
import os
import re
import sys
import unittest

from fluid import *

# --- logging setup ---
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])
log.setLevel(logging.DEBUG)

fld = None


# @unittest.skip("Skipping Test01")
class Test01(unittest.TestCase):
    
    def setUp(self):
        global fld
        path = os.path.join(sys.path[0],'..','..','TREND 4.0')
        dll_path = os.path.join(sys.path[0],'TREND_FIT_DLL.dll')
        self.fld = Fluid('TP','D',['water'],[1],[1],1,path,'molar',dll_path)

    def test_constructor(self):
        self.assertIsNotNone(self.fld)

# @unittest.skip("Skipping Test01")
class Test02(unittest.TestCase):
    
    def setUp(self):
        global fld
        path = os.path.join(sys.path[0],'..','..','TREND 4.0')
        dll_path = os.path.join(sys.path[0],'TREND_FIT_DLL.dll')
        self.fldmix1 = Fluid('TP','HE',['methane','ethane'],[0.6,0.4],[1,1],1,path,'molar',dll_path)
        self.fldmix = Fluid('TP','H',['methane','ethane'],[0.6,0.4],[1,1],1,path,'molar',dll_path)
        self.fld1 = Fluid('TP','H',['methane','ethane'],[0.99999999,0.00000001],[1,1],1,path,'molar',dll_path)
        self.fld2 = Fluid('TP','H',['ethane','methane'],[0.99999999,0.00000001],[1,1],1,path,'molar',dll_path)

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

    def test_mixture_density(self):
        hE, errmix = self.fldmix1.TREND_EOS_FIT(91.50,0.10132,self.COSMOparam)
        print("Excess enthalpy = {}, error = {}".format(hE, errmix))
        self.assertIsNotNone(hE)

    def test_mixture_mix_enthalpy(self):
        h_mix, errmix = self.fldmix.TREND_EOS_FIT(91.50,0.10132,self.COSMOparam)
        h_comp1, errmix = self.fld1.TREND_EOS_FIT(91.50,0.10132,self.COSMOparam)
        h_comp2, errmix = self.fld2.TREND_EOS_FIT(91.50,0.10132,self.COSMOparam)
        hE = h_mix - 0.6 * h_comp1 - 0.4 * h_comp2
        print("Excess enthalpy (combined) = {} J/mol, error = {}".format(hE, errmix))
        pass

    def test_mixture_heat_cap(self):
        pass

class Test03(unittest.TestCase):
    
    def setUp(self):
        global fld
        path = os.path.join(sys.path[0],'..','..','TREND 4.0')
        dll_path = os.path.join(sys.path[0],'TREND_FIT_DLL.dll')
        self.fld = Fluid('TP','D',['water'],[1],[1],1,path,'molar',dll_path)

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

    def test_fld_density(self):
        densemix, errmix = self.fld.TREND_EOS_FIT(273.15,1,self.COSMOparam)
        print("density = {}, error = {}".format(densemix, errmix))
        self.assertIsNotNone(densemix)

    def test_fld_mix_enthalpy(self):
        pass

    def test_fld_heat_cap(self):
        pass

# @unittest.skip("Skipping Test01")
class Test04(unittest.TestCase):
    
    def setUp(self):
        global fld
        path = os.path.join(sys.path[0],'..','..','TREND 4.0')
        dll_path = os.path.join(sys.path[0],'TREND_FIT_DLL.dll')
        #self.fldmix1 = Fluid('TP','HE',['methane','ethane'],[0.6,0.4],[1,1],1,path,'molar',dll_path)
        self.fldmix = Fluid('TP','CP',['methane','ethane'],[0.6,0.4],[1,1],1,path,'molar',dll_path)
        self.fld1 = Fluid('TP','CP',['methane','ethane'],[0.99999999,0.00000001],[1,1],1,path,'molar',dll_path)
        self.fld2 = Fluid('TP','CP',['ethane','methane'],[0.99999999,0.00000001],[1,1],1,path,'molar',dll_path)

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

    def test_mixture_mix_heat_capacity(self):
        cp_mix, errmix = self.fldmix.TREND_EOS_FIT(91.50,0.10132,self.COSMOparam)
        cp_comp1, errmix = self.fld1.TREND_EOS_FIT(91.50,0.10132,self.COSMOparam)
        cp_comp2, errmix = self.fld2.TREND_EOS_FIT(91.50,0.10132,self.COSMOparam)
        cpE = cp_mix - 0.6 * cp_comp1 - 0.4 * cp_comp2
        print("heat_capacity (combined) = {} J/molK, error = {}".format(cpE, errmix))
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)