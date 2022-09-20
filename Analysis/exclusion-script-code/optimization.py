import computation

from scipy import integrate
from scipy import stats
from scipy.interpolate import interp1d
import pandas as pd
import numpy as np
from copy import deepcopy
import itertools  

def qeData(filepath):
    extractedData=pd.read_csv(filepath,names=["x","y"])
    qeX=extractedData.x.values
    qeY=extractedData.y.values
    return qeX,qeY

def get_weights(x,y,qex,qey):
    ## x is in wavelength
    fQE = interp1d(qex,qey)
    truncX=x[x>min(qex)]
    truncY=y[x>min(qex)]
    truncY=truncY[truncX<max(qex)]
    truncX=truncX[truncX<max(qex)]

    return truncX,truncY,fQE(truncX)

def weighted_integral(rawX,rawY,qex,qey):
    finalX,finalY,weights=get_weights(rawX,rawY,qex,qey)
    weighedFunc=(weights/100)*finalY ## dividing by hundred because QE is in percentage
   # print(weighedFunc)
    result=integrate.trapz(np.flip(weighedFunc),np.flip(finalX))
    
    return result,finalX,finalY,weighedFunc

def normalize(data):
    data=np.array(data)
    return ((data-min(data))/(max(data)-min(data)))

def optimize_integral_boost(qex,qey,maxT,n1,n2,layers,mirr=False):
    tlist=np.linspace(200,maxT,10)*10**(-9)
    clist=np.linspace(1,2,10)
    data=np.zeros(shape=(len(tlist)*len(clist),4))
    
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
        transVarChX,transVarChSol=computation.solution_rightwave(n1,n2,d1,stackSize,chirp=chirping,isTList=subList[i],mirror=mirrorMode)
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