import computation

from scipy import integrate
from scipy import stats
from scipy.interpolate import interp1d
import pandas as pd
import numpy as np
from copy import deepcopy
import itertools  

def qeData(filepath):
    '''
    extracts data from file containing quantum efficiency data
    
    inputs:
        filepath - directory of the file with quantum efficiency data of the sensor
    
    returns:
        qeX - wavelength list
        qeY - % QE @ given wavelength
    '''
    extractedData=pd.read_csv(filepath,names=["x","y"])
    qeX=extractedData.x.values
    qeY=extractedData.y.values
    return qeX,qeY

def get_weights(x,y,qex,qey):
    '''
    This function clips the given dataset (x,y) according to the dataset (qex,qey).
    Useful for getting a weighted boost spectrum, since we want to weight the 
    boost@given walvenegth by QE@given wavelength before starting optimization

    inputs: 
        x - wavelength array over which we want to sample the QE curve
        y - boost spectrum for the given wavelengths
        qex - wavelength data from QE cruve
        qey - QE % data from QE curve (y-axis)
    
    returns:
        truncX,trunY - x,y arrays truncated according to qex
        weights - values to use for getting the weighted boost spectrum
    '''
    ## x is in wavelength
    fQE = interp1d(qex,qey)
    truncX=x[x>min(qex)]
    truncY=y[x>min(qex)]
    truncY=truncY[truncX<max(qex)]
    truncX=truncX[truncX<max(qex)]
    weights = fQE(truncX)

    return truncX,truncY,weights

def weighted_integral(rawX,rawY,qex,qey):
    '''
    gives an integral of the weighted boost spectrum using the trapezoid method in scipy

    inputs:    
        rawX - wavelength list
        rawY - boost spectrum list
        qeX - wavelength data from QE curve
        qeY - QE% from QE cruve
    
    returns:
        result - integral
        finalX - truncated wavelength list
        finalY - truncated boost spectrum list
        weightedFunc - weighted boost spectrum list
    '''
    finalX,finalY,weights=get_weights(rawX,rawY,qex,qey)
    weighedFunc=(weights/100)*finalY  # get the weighted function
    ## dividing by hundred because QE is in percentage
    # print(weighedFunc)
    result=integrate.trapz(np.flip(weighedFunc),np.flip(finalX))
    
    return result,finalX,finalY,weighedFunc

def normalize(data):
    '''
    Normalizes input list such that min-->0 and max-->1
    
    inputs:
        data - list of values to be normalized
        
    returns:
        normalized dataset
    '''
    data=np.array(data)
    return ((data-min(data))/(max(data)-min(data)))

def optimize_integral_boost(qex,qey,maxT,n1,n2,layers,mirr=False):
    
    '''
    This function calculates the weighted integral of the boost spectrum across different thickness values
    and returns the dataset for all the values
    
    inputs:
        qex, qey - wavelength and % data for QE of the sensor
        maxT - maximum thickness 
        n1,n2 - refractive index of the two media
        layers - number of layers
        mirr -  boolean, indicate whether stack is mirrored or not
    
    returns:
        optimized dataset with
            data[index][0] --> thickness, 
            data[index][1] --> chirp, 
            data[index][2] --> weighted integral of boost spectrum,
            data[index][3] --> max weighted boost value
    '''
    
    tlist=np.linspace(200,maxT,10)*10**(-9) # generate list of thickness values to scan over
    clist=np.linspace(1,2,10) # generate list of chirp values to scan over
    data=np.zeros(shape=(len(tlist)*len(clist),4)) # initialize a null matrix to hold optimization data
    # data[index][0] --> thickness, 
    # data[index][1] --> chirp, 
    # data[index][2] --> weighted integral of boost spectrum,
    # data[index][3] --> max weighted boost value
    
    index=0
    for t in tlist:
        for c in clist:
            data[index][0]=t
            data[index][1]=c
            w,sol=computation.solution_rightwave(n1,n2,t,layers,chirp=c,mirror=mirr)
            wave=computation.freq_to_lamda(w)
            integral, x,y,wx= weighted_integral(wave,np.array(sol),qex,qey)
            data[index][2]=integral
            data[index][3]=np.max(wx) ## weighed max boost
            index=index+1
    return data

def optimize(A,B):
    '''
    optimization function. Here, we have a parameter set A and parameter set B,
    we want both these parameters to be maximized, 
    so we construct a composite function (A/A0)*(B/B0) and maximize it. 
    A0 and B0 are maximum values of these paramters
    
    intputs:
        A,B - dataset with these parameters
    
    returns:
        A' - Ideal value for A
        B' - Ideal value for B
        idx - index at which these values occur
    '''
    
    A0=max(A)
    B0=max(B)
    func=(A/A0)*(B/B0)
   # func=(A/A0)
    bestIdx=np.argmax(func)
    
    return A[bestIdx],B[bestIdx],bestIdx

def gaussian_list(stackSize,chirping,d1,n1,n2,nlists=40,std=30e-9):
    mainChirpList=computation.make_chirplist(d1,d1*(n1/n2),n1,n2,stackSize-2,chirping)
    # 0 1 2 3 4 5 6 7

    gaussianSubList=[]
    layers_to_skip=[0,stackSize-4,(stackSize-2)/2-1,(stackSize-2)/2]
    for idx in range(0,40):
        dummy=deepcopy(mainChirpList)
       # for i in range(1,int((stackSize-2)/2)-1):
        for i in range(1,stackSize-2):
          #  randIdx=np.random.randint(len(chirplists))
            if i in layers_to_skip: continue
            dummy[i]=np.random.normal(loc=mainChirpList[i],scale=std)
            #dummy[-(i+1)]=np.random.normal(loc=mainChirpList[-(i+1)],scale=std)

        gaussianSubList.append(dummy)
    return gaussianSubList

def boost_int_output(qex,qey,stackSize,chirping,d1,n1,n2,subList,mirrorMode="False"):

    tranVarChBoost=np.zeros(len(subList))
    tranVarChIntegral=np.zeros(len(subList))



    for i in range(0,len(subList)):
                       
            
        transVarChX,transVarChSol=computation.solution_rightwave(n1,n2,d1,stackSize,chirp=chirping,
                                                                 isTList=subList[i],mirror=mirrorMode)
        transVarChWave=computation.freq_to_lamda(transVarChX)
        areaVar,finalX,finalY,boostsWVar=weighted_integral(transVarChWave,transVarChSol,qex,qey)
        tranVarChBoost[i]=max(boostsWVar)
        tranVarChIntegral[i]=areaVar
    return tranVarChBoost,tranVarChIntegral

def get_integral_boost_vs_thickness(qex,qey,tMax,n1,n2,chirpVal,layers,mirror=False):
    tList=np.linspace(200,tMax,20)*10**(-9)
    integralList=[]
    maxBoostList=[]
    for thickness in tList:
        w,sol=computation.solution_rightwave(n1,n2,thickness,layers,chirp=chirpVal,mirror=mirror)
        wave=computation.freq_to_lamda(w)
        integral, x,y,wx= weighted_integral(wave,np.array(sol),qex,qey)
        integralList.append(integral)
        maxBoostList.append(max(wx))
    return tList,integralList,maxBoostList