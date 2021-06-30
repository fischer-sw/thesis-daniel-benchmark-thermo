# TREND 4.0 Python Interface 
# Example Call
# @authors: David Celný , Sven Pohl
# Bochum, 16.05.2019
from fluid import *

# For path seperation use D:\\...\\
path = os.path.join(sys.path[0],'..','..','TREND 4.0')

# Path to the TREND 4.0 DLL

#dll_path = 'D:\\COSMO-SAC_SCREAM\\mixtures\\interface\\python\\COSMOSAC_FIT_DLL.dll'
# dll_path = 'D:\\COSMO-SAC_SCREAM\\mixtures\\interface\\python\\COSMOSAC_FIT_DLL.dll'
dll_path = os.path.join(sys.path[0],'TREND_FIT_DLL.dll')

#dll_path = 'D:\\COSMO-SAC_SCREAM\\TREND 4.0\\TREND_x64.dll'

# Create object of Fluid
fld = Fluid('TP','D',['water'],[1],[1],1,path,'molar',dll_path)

fldmix = Fluid('TP','D',['methane','ethane', 'propane'],[0.6,0.3,0.1],[2,2,2],22,path,'molar',dll_path)

fldmix = Fluid('TP','HE',['methane','ethane', 'propane'],[0.6,0.3,0.1],[2,2,2],22,path,'molar',dll_path)


#fldmix = Fluid('TP','D',['methane','ethane'],[0.5,0.5],[1,1],13,path,'specific',dll_path)
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

# Calculate density with temperature and pressure input
#dense,err = fld.TREND_EOS_FIT(300,1,[1,1,1])
#densemix,errmix = fldmix.TREND_EOS_FIT(300,1,[1,2,1,3,1,4,1,5,1,6,1,7,1,8,1,9,1,10,1,11])
densemix,errmix = fldmix.TREND_EOS_FIT(300,1,COSMOparam)
#densemix,errmix = fldmix.TREND_EOS(300,1)
#print('Density: ',dense)
#print('Error: ',err)
print('Density: ',densemix)
print('Error: ',errmix)
COSMOparam[18] = 120
densemix,errmix = fldmix.TREND_EOS_FIT(300,1,COSMOparam)
#densemix,errmix = fldmix.TREND_EOS(300,1)
#print('Density: ',dense)
#print('Error: ',err)
print('Density: ',densemix)
print('Error: ',errmix)
COSMOparam[18] = 116
densemix,errmix = fldmix.TREND_EOS_FIT(300,1,COSMOparam)
#densemix,errmix = fldmix.TREND_EOS(300,1)
#print('Density: ',dense)
#print('Error: ',err)
print('Density: ',densemix)
print('Error: ',errmix)
COSMOparam[18] = 120
densemix,errmix = fldmix.TREND_EOS_FIT(300,1,COSMOparam)
#densemix,errmix = fldmix.TREND_EOS(300,1)
#print('Density: ',dense)
#print('Error: ',err)
print('Density: ',densemix)
print('Error: ',errmix)




#prop_overall, x_phase, prop_phase, phasetype = fldmix.FLASH_FIT(300,1,COSMOparam)
prop_overall, x_phase, prop_phase, phasetype = fldmix.FLASH(300,1)
print(prop_overall[1])
print(x_phase[phasetype[0]-1][0])
print(phasetype[0])
prop_overall, x_phase, prop_phase, phasetype = fldmix.FLASH(300,1)
print(prop_overall[1])
print(x_phase[phasetype[0]-1][0])
print(phasetype[0])

#Viscosity
mu,error = fldmix.RES_VISCOSITY(300,1)
print('Viscosity ', mu[0])
print('Error ', error)



fldmix = Fluid('TLIQ','D',['propane','dme'],[0.5,0.5],[1,1],1,path,'molar',dll_path)
        
matrix2,MW = fldmix.TREND_SPEC_EOS()
print('Molecular weight Fluid1 ', MW[0][0])   
print('Molecular weight Fluid2 ', MW[1][0])
#print('Molecular weight Fluid3 ', MW[2][0])
#print('Molecular weight Fluidmix ', MW[3])