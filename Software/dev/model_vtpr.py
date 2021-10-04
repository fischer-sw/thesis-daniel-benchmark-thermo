#!/usr/bin/python
import os
import sys

from fluid import *
from srk_fld_file import *
from check_phase_eq_direction import *
from model import *

class VTPR(Model):

    def __init__(self, model_name, mappings_filename, eqtype, mixtype, logger=None):
        
        """ 
        Constructor of srk model class

        """
        super().__init__(model_name, mappings_filename, eqtype, mixtype, logger)

        vars = ['Enthalpy of mixing', 'Heat capacity of mixing', 'Isothermal phase equilibrium data', 'Isobaric phase equilibrium data', 'Azeotropic point']
        
        # vars to calc model values for
        self.calc_vars = vars[0:2]

        # vars to delete keys to calculate again
        self.del_keys = []
        # self.del_keys = vars[0:2]

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