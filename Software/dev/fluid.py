from __future__ import print_function
import ctypes as ct
import sys
import platform
import os
import time

input_length = 12
fluid_length = 30
path_length = 255
unit_length = 20
COSMO_length = 30

class Fluid:
    def __init__(self,input,calctype,fluids,moles,eos_ind,mix_ind,path,unit,dll_path):
        input = str.encode(input)
        self.input = ct.create_string_buffer(input.ljust(input_length),input_length)
        calctype = str.encode(calctype)
        self.calctype = ct.create_string_buffer(calctype.ljust(input_length),input_length)

        #fluid
        fluids_type = (ct.c_char * fluid_length) * fluid_length
        fluids_tmp = fluids_type()

        for i in range(0,fluid_length):
            fluids_tmp[i] = ct.create_string_buffer(b" ".ljust(fluid_length),fluid_length)

        for fid,fluid in enumerate(fluids):
            fluids_tmp[fid] = ct.create_string_buffer(str.encode(fluid.ljust(fluid_length)),fluid_length)
        self.fluid = fluids_tmp
        
        #moles
        moles_tmp = (fluid_length * ct.c_double)()
        for mid,mole in enumerate(moles):
            moles_tmp[mid] =  mole
        self.moles = moles_tmp

        #eos_ind
        eos_ind_tmp = (fluid_length * ct.c_int)()
        for eid,eos_id in enumerate(eos_ind):
            eos_ind_tmp[eid] =  eos_id
        self.eos_ind = eos_ind_tmp
         
        self.mix_ind = ct.c_int(mix_ind)

        path = str.encode(path)
        self.path = ct.create_string_buffer(path.ljust(path_length),path_length)
        unit = str.encode(unit)
        self.unit = ct.create_string_buffer(unit.ljust(unit_length),unit_length)

        if fid==mid and mid==eid:
            pass
        else:
            raise ValueError('NOT SAME LENGTHS OF INPUTS')
        
		 #Variables for Flash
        #Phasetype
        self.phasetype = (5 * ct.c_int)()
        #Phasetext
        phasetext_type = (ct.c_char * 4) * 5
        self.phasetext = phasetext_type()
        #x_phase
        x_phase_type = (30 * ct.c_double) * 5
        self.x_phase = x_phase_type()
        #prop_phase
        prop_phase_type = (30 * ct.c_double) * 5
        self.prop_phase = prop_phase_type()
        #prop_overall
        prop_overall_type = (30 * ct.c_double)()
        self.prop_overall = prop_overall_type
        #lnfug_phase
        lnfug_phase_type = (30 * ct.c_double) * 5
        self.lnfug_phase = lnfug_phase_type()
        #chempot_phase
        chempot_phase_type = (30 * ct.c_double) * 5
        self.chempot_phase = chempot_phase_type()
        #phasefrac
        self.phasefrac = (5 * ct.c_double)()
        #PropNameUnit
        prop_name_unit_type = (ct.c_char * 30) * 37 * 2
        self.prop_name_unit = prop_name_unit_type()
		
        #Variables for PTDIAG
        #t_pts_out
        t_pts_out = (400 * ct.c_double)()
        self.t_pts_out = t_pts_out
        #p_pts_out
        p_pts_out = (400 * ct.c_double)()
        self.p_pts_out = p_pts_out
        #rholiq_pts_out
        rholiq_pts_out = (400 * ct.c_double)()
        self.rholiq_pts_out = rholiq_pts_out
        #rhovap_pts_out
        rhovap_pts_out = (400 * ct.c_double)()
        self.rhovap_pts_out = rhovap_pts_out
        #pointID_pts_out
        pointID_pts_out = (400 * ct.c_int)()
        self.pointID_pts_out = pointID_pts_out     
        #x_pts_out
        x_pts_out = (400 * ct.c_double) * 30
        self.x_pts_out = x_pts_out()   
        
        #Variables for PTXDIAG
        #p_points
        p_pts_arr = (300 * ct.c_double)()
        self.p_points_array = p_pts_arr
        #T_points
        T_pts_arr = (300 * ct.c_double)()
        self.T_points_array = T_pts_arr
        #rhovap_points
        rhovap_pts_arr = (300 * ct.c_double)()
        self.rhovap_points = rhovap_pts_arr
        #rholiq_points
        rholiq_pts_arr = (300 * ct.c_double)()
        self.rholiq_points = rholiq_pts_arr
        #x_points
        x_points = (300 * ct.c_double) * 4
        self.x_points = x_points()        
        
        #Variables for Viscosity
        #prop_overall
        prop_viscosity_type = (30 * ct.c_double)()
        self.prop_viscosity = prop_viscosity_type
        
        #Variables for TREND_SPEC_EOS
        limits_text_arg_type = (30 * ct.c_char) * 30
        self.limits_text_arg = limits_text_arg_type()
        
        limits_values_type = (30 * ct.c_double) * 31
        self.limits_values = limits_values_type()
        
        self.handle_ptr = ct.POINTER(ct.c_int)()
        self.dll_path = dll_path
        assert(os.path.exists(self.dll_path))
        self.TrendDLL = ct.windll.LoadLibrary(self.dll_path)

    def TREND_EOS(self,pr1,pr2):
        errorflag = ct.c_int(0)
        self.TrendDLL.TREND_EOS_STDCALL.restype = ct.c_double # !beware required line otherwise you get unsensible output
        return self.TrendDLL.TREND_EOS_STDCALL(self.calctype, self.input, ct.byref(ct.c_double(pr1)), ct.byref(ct.c_double(pr2)), self.fluid, self.moles, self.eos_ind, ct.byref(self.mix_ind), self.path, self.unit, ct.byref(errorflag), ct.byref(self.handle_ptr), 12, 12, 30, 255, 20),errorflag
    
    def TREND_EOS_FIT(self,pr1,pr2,COSMOparam_tmp):
        errorflag = ct.c_int(0)
        #print(COSMOparam_tmp[1])
        COSMOparam = (ct.c_double * COSMO_length)()
        for i in range(0,COSMO_length):
            COSMOparam[i] = COSMOparam_tmp[i]
            #print(COSMOparam[i])
        self.TrendDLL.TREND_EOS_FIT_STDCALL.restype = ct.c_double # !beware required line otherwise you get unsensible output
        #print(COSMOparam[0])
        return self.TrendDLL.TREND_EOS_FIT_STDCALL(self.calctype, self.input, ct.byref(ct.c_double(pr1)), ct.byref(ct.c_double(pr2)), self.fluid, self.moles, self.eos_ind, ct.byref(self.mix_ind), self.path, self.unit, COSMOparam, ct.byref(errorflag), ct.byref(self.handle_ptr), 12, 12, 30, 255, 20),errorflag
    
    def FLASH(self,pr1,pr2):
        errorflag = ct.c_int(0)
        y = self.TrendDLL.FLASH3_STDCALL(self.input, ct.byref(ct.c_double(pr1)), ct.byref(ct.c_double(pr2)), self.fluid, self.moles, self.eos_ind, ct.byref(self.mix_ind), self.path, self.unit, self.phasetype, self.phasetext, self.x_phase, self.prop_phase, self.prop_overall, self.lnfug_phase, self.chempot_phase, self.phasefrac, self.prop_name_unit, ct.byref(errorflag), ct.byref(self.handle_ptr), 12, 30, 255, 20, 4, 30)         
        #if self.phasetype[1]==0:
            #NOTE: THE ORDER OF THE MATRICES SEEM TO BE SWITCHED IN PYTHON COMPARED TO FORTRAN. Fortran: x(fluid_nr,phasetype), Python: x(phasetype(fluid_nr))
            #return self.phasetype[0], self.phasetype[1], self.x_phase[self.phasetype[0]-1][0], 0.0, errorflag
        #else:
            #return self.phasetype[0], self.phasetype[1], self.x_phase[self.phasetype[0]-1][0], self.x_phase[self.phasetype[1]-1][0], errorflag    
        return self.prop_overall, self.x_phase, self.prop_phase, self.phasetype

    def FLASH_FIT(self,pr1,pr2,COSMOparam_tmp):
        errorflag = ct.c_int(0)
        COSMOparam = (ct.c_double * COSMO_length)()
        for i in range(0,COSMO_length):
            COSMOparam[i] = COSMOparam_tmp[i]
        y = self.TrendDLL.FLASH3_FIT_STDCALL(self.input, ct.byref(ct.c_double(pr1)), ct.byref(ct.c_double(pr2)), self.fluid, self.moles, self.eos_ind, ct.byref(self.mix_ind), self.path, self.unit, COSMOparam, self.phasetype, self.phasetext, self.x_phase, self.prop_phase, self.prop_overall, self.lnfug_phase, self.chempot_phase, self.phasefrac, self.prop_name_unit, ct.byref(errorflag), ct.byref(self.handle_ptr), 12, 30, 255, 20, 4, 30)         
        #if self.phasetype[1]==0:
            #NOTE: THE ORDER OF THE MATRICES SEEM TO BE SWITCHED IN PYTHON COMPARED TO FORTRAN. Fortran: x(fluid_nr,phasetype), Python: x(phasetype(fluid_nr))
            #return self.phasetype[0], self.phasetype[1], self.x_phase[self.phasetype[0]-1][0], 0.0, errorflag
        #else:
            #return self.phasetype[0], self.phasetype[1], self.x_phase[self.phasetype[0]-1][0], self.x_phase[self.phasetype[1]-1][0], errorflag    
        return self.prop_overall, self.x_phase, self.prop_phase, self.phasetype

    def PTXDIAG_FIT(self,pr1,COSMOparam_tmp,fileout):
        errorflag = ct.c_int(0)
        COSMOparam = (ct.c_double * COSMO_length)()
        for i in range(0,COSMO_length):
            COSMOparam[i] = COSMOparam_tmp[i]
        points = ct.c_int(0)
        fileout = str.encode(fileout)
        fileout_arg = ct.create_string_buffer(fileout.ljust(255),255)
        y = self.TrendDLL.PTXDIAG_OUT_FIT_STDCALL(self.input, ct.byref(ct.c_double(pr1)), self.fluid, self.eos_ind, ct.byref(self.mix_ind), self.path, COSMOparam, self.p_points_array, self.T_points_array, self.x_points, self.rhovap_points, self.rholiq_points, ct.byref(points), fileout_arg, ct.byref(errorflag), ct.byref(self.handle_ptr), 12, 30, 255, 255)                
        return self.p_points_array, self.T_points_array, self.x_points, self.rhovap_points, self.rholiq_points, points          


    def PTDIAG(self,env_pv,p_spec,T_spec,fileout):
        errorflag = ct.c_int(0)
        fileout = str.encode(fileout)
        fileout_arg = ct.create_string_buffer(fileout.ljust(255),255)
        y = self.TrendDLL.PTDIAG_OUT_STDCALL(ct.byref(ct.c_int(env_pv)), self.fluid, self.moles, self.eos_ind, ct.byref(self.mix_ind), self.path, ct.byref(ct.c_double(p_spec)), ct.byref(ct.c_double(T_spec)),self.t_pts_out, self.p_pts_out, self.rholiq_pts_out, self.rhovap_pts_out, self.pointID_pts_out, self.x_pts_out, fileout_arg, ct.byref(errorflag), ct.byref(self.handle_ptr), 30, 255, 255)                
        return self.t_pts_out, self.p_pts_out, self.rholiq_pts_out, self.rhovap_pts_out, self.pointID_pts_out     
        
        
    def PTXDIAG(self,pr1,fileout):
        errorflag = ct.c_int(0)
        points = ct.c_int(0)
        fileout = str.encode(fileout)
        fileout_arg = ct.create_string_buffer(fileout.ljust(255),255)
        y = self.TrendDLL.PTXDIAG_OUT_STDCALL(self.input, ct.byref(ct.c_double(pr1)), self.fluid, self.eos_ind, ct.byref(self.mix_ind), self.path, self.p_points_array, self.T_points_array, self.x_points, self.rhovap_points, self.rholiq_points, ct.byref(points), fileout_arg, ct.byref(errorflag), ct.byref(self.handle_ptr), 12, 30, 255, 255)                
        return self.p_points_array, self.T_points_array, self.x_points, self.rhovap_points, self.rholiq_points, points          
    
    def RES_VISCOSITY(self,pr1,pr2):
        errorflag = ct.c_int(0)
        y = self.TrendDLL.RES_viscosity_STDCALL(self.input, ct.byref(ct.c_double(pr1)), ct.byref(ct.c_double(pr2)), self.fluid, self.moles, self.eos_ind, ct.byref(self.mix_ind), self.path, self.unit, self.prop_viscosity,  ct.byref(errorflag), ct.byref(self.handle_ptr), 12, 30, 255, 20)         
        return self.prop_viscosity, errorflag
        
    def TREND_SPEC_EOS(self):
        errorflag = ct.c_int(0)
        y = self.TrendDLL.TREND_SPEC_EOS_STDCALL(self.fluid, self.moles, self.eos_ind, ct.byref(self.mix_ind), self.path, self.unit, self.limits_text_arg, self.limits_values, ct.byref(errorflag), ct.byref(self.handle_ptr), 30, 255, 20, 30)         
        return self.limits_text_arg, self.limits_values