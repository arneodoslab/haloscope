import computation
import optimization

import numpy as np
import pandas as pd
import itertools  


from scipy import integrate
from scipy import stats
import scipy.constants as const
from scipy.interpolate import interp1d

## Define stack parameters
N1=1.4656
N2=1.9166
AREA_DEFAULT = np.pi*(25 * 1e-3)**2
PHOTODETECTION = 0.718 # from Geant4 simulations by Panos


# GmirrStackNewfinal=[2.64301304e-07, 2.05023010e-07, 2.64161979e-07, 1.97160669e-07,
#        2.91493464e-07, 2.08610261e-07, 2.71752078e-07, 2.35044161e-07,
#        2.83712516e-07, 1.86253287e-07, 2.39798560e-07, 2.02669693e-07,
#        2.68153236e-07, 2.06719177e-07, 2.80724213e-07, 2.02468834e-07,
#        3.05888313e-07, 2.44214957e-07, 2.69521019e-07, 2.18623695e-07,
#        2.81774108e-07, 2.17044466e-07, 2.73523119e-07, 2.09159701e-07,
#        2.59531054e-07, 1.77575379e-07, 3.18208316e-07, 2.21923160e-07,
#        2.98821231e-07, 2.28392324e-07, 2.76196207e-07, 2.09442925e-07,
#        2.50243585e-07, 2.15603643e-07, 2.77090494e-07, 2.50607575e-07,
#        2.57450918e-07, 2.34109609e-07, 2.78263942e-07, 2.29144964e-07,
#        2.71076475e-07, 2.16733672e-07, 2.82051087e-07, 2.20987585e-07,
#        2.83066696e-07, 2.28998961e-07]

GmirrStackNewfinal = np.loadtxt("measured-thickness-080821.txt",skiprows=1)[:,0]*1e-9 ## measured thicknesses
per85boost = np.load("boost-err-85per.npy") ## 85%ile boost factor
per15boost = np.load("boost-err-15per.npy")


thick=2.736840000000001e-07 ##m , thickness of central layer, used for optimization/boost factor calculation
chirp=1.071
nLayers=48 # actual number of layers+2 (air and air)

qeX,qeY=optimization.qeData("hamamatsu_qe.csv")
#qeXSensor, qeYSensor = optimization.qeData("excelitas_qe.csv") ## used where the qeCurve is to estimate the error function
#qeYSensor = qeYSensor*(0.02/0.89) ## correction to convert QE to PDE. 0.02 is PDE at 1V excess, 830nm, 0.89 is QE at 830nm. 
qeXSensor, qeYSensor = optimization.qeData("excelitas_qe1V.csv")
qeYSensor = qeYSensor * 100
qeXlc, qeYlc = optimization.qeData("laser-components_qe.csv")
#qe_func=interp1d(qeXSensor,qeYSensor)

def trim_data(x1,x2,sensor="excelitas"):
    if (sensor=="excelitas"): qeXhere = qeXSensor
    elif (sensor=="LC"): qeXhere = qeXlc
    mask1 = (x1<max(qeXhere)) & (x1>min(qeXhere)) 
    x1 = x1[mask1]
    x2 = x2[mask1]
    return x1,x2

## function to get [wavelength,boost] 
def get_solution(n1,n2,chirp,d1,N,tlist=[],isMirr=False):
    
    w,sol=computation.solution_rightwave(n1,n2,d1,nLayers=N,chirp=chirp,isTList=tlist,mirror=isMirr)
    phase=computation.freq_to_phase(w,n1,d1)
    wave=computation.freq_to_lamda(w)
    
    return wave,sol

def rate_calc(wavelength ,qex, qey,boost,kappa=1e-14, fDM=1,hitRate=PHOTODETECTION,sensor="matsu"):
      
    wave,beta,__=optimization.get_weights(wavelength,boost,qex,qey)
    
    if sensor=="matsu": qe_func=interp1d(qex,qey)
    elif sensor=="TES": qe_func = lambda w: np.ones(len(wave))*50
    elif sensor=="LC": 
        wave,beta = trim_data(wave,beta,"LC")
        qe_func = interp1d(qeXlc,qeYlc)
    else: 
        wave,beta = trim_data(wave,beta)
        qe_func=interp1d(qeXSensor,qeYSensor)
    mass=const.h*const.c/(wave*1e-9)*6.2*1e18
       
    eta= qe_func(wave)*hitRate
    
    rate = (5.2)* (beta**2)* eta * (1/mass) * 1e27 * (kappa)**2 * fDM ## 1/(days*cm**2 * eV)
    
    return wave, rate


GmirrWaveNew,GmirrSolNew=get_solution(N1,N2,chirp,thick,nLayers,tlist=GmirrStackNewfinal,isMirr=True)

def get_rate(kappa=1e-11, fDM=1,hitRate=PHOTODETECTION,sensor="matsu"):
    wave,rate=rate_calc(GmirrWaveNew ,qeX, qeY, GmirrSolNew, kappa, fDM, hitRate,sensor=sensor)
    m = const.h*const.c/(wave*1e-9)*6.2*1e18
    return m,rate

def get_kappa(energyIdx,N,time=7,area=AREA_DEFAULT,fDM=1,hitRate=PHOTODETECTION,sensor="matsu",percentile=100):
    ## time in days
    '''
    function to get kappa at a specific energy (accessed by index) for a given number of events (N)
    '''
   # print(time)
    if (percentile==100): 
        wave,beta,__=optimization.get_weights(GmirrWaveNew,GmirrSolNew,qeX,qeY)
    if (percentile==15): 
        wave,beta = per15boost
       
    if (percentile==85):
        wave,beta = per85boost
    #print(len(wave),len(beta)) 
    if sensor=="matsu": qe_func=interp1d(qeX,qeY)
    elif sensor=="TES": qe_func = lambda w: np.ones(len(w))*50
    elif sensor=="LC": 
        wave,beta = trim_data(wave,beta,"LC")
        qe_func = interp1d(qeXlc,qeYlc)
    else: 
        wave,beta = trim_data(wave,beta)
        qe_func=interp1d(qeXSensor,qeYSensor)
        
    mass=const.h*const.c/(wave*1e-9)*6.2*1e18
    eta= qe_func(wave)*hitRate/100 ## dividing by 100 since QE is expressed in %
    
    #print(time)
    kSquare = (N/(area*time))/( (5.2)* (beta[energyIdx]**2)* eta[energyIdx] * 1e27 * fDM)*(1/mass[energyIdx])
    #kSquare = (N/(area*time))/( (5.2)* (beta[energyIdx]**2)* eta[energyIdx] * 1e31 * fDM)
    #print('len mass=')
    #print(len(mass))
    #print('ksquare=')
    #print(kSquare)
    return np.sqrt(kSquare)

def get_NvsT(energyIdx,kappa,time=7,area=AREA_DEFAULT,fDM=1,hitRate=PHOTODETECTION,sensor="matsu"):
    ## get number of hits as a function of time
    wave,beta,__=optimization.get_weights(GmirrWaveNew,GmirrSolNew,qeX,qeY)
    
    if sensor=="matsu": qe_func=interp1d(qex,qey)
    elif sensor=="TES": qe_func = lambda w: np.ones(len(wave))*50
    elif sensor=="LC": 
        wave,beta = trim_data(wave,beta,"LC")
        qe_func = interp1d(qeXlc,qeYlc)
    else: 
        wave,beta = trim_data(wave,beta)
        qe_func=interp1d(qeXSensor,qeYSensor)

    mass=const.h*const.c/(wave*1e-9)*6.2*1e18
    eta= qe_func(wave)*hitRate    
    print(beta[energyIdx],mass[energyIdx],eta[energyIdx],kappa,fDM,time,area)
    nHits = (mass[energyIdx])*(5.2)* (beta[energyIdx]**2)* eta[energyIdx] * 1e27 * (kappa)**2 * fDM / (time * area)
    #nHits = (5.2)* (beta[energyIdx]**2)* eta[energyIdx] * 1e31 * (kappa)**2 * fDM / (time * area)
    return nHits


