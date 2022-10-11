import numpy as np
from numpy.linalg import multi_dot
import pandas as pd
import matplotlib.pyplot as plt

from sympy.solvers import solve
from sympy import Symbol
from sympy import limit,oo

c=2.99792*10e8
h=4.1356675*10e-15

def G12(n2,n1):
    G=np.array([[n2+n1,n2-n1],[n2-n1,n2+n1]])
    valToReturn=(G/(2*n2))
    return valToReturn

def S12(n2,n1,v,d,w):
    exponent=(1j*d*v*w)/c

    factor=0.5*((1/(n2**2))-(1/(n1**2)))
    S12arr=np.array([[1+(v/(n2*c)),1+(v/(n2*c))],[1-(v/(n2*c)),1-(v/(n2*c))]])
    valToReturn=np.exp(exponent)*factor*S12arr
    return valToReturn

def P2(n2,d,w):
    P=np.array([[np.exp((1j*n2*d*w)/c),0],[0,np.exp((-1j*n2*d*w)/c)]])
    return P 

def Tfull(nList,dList,w,v):
    if len(nList) != len(dList)+2: 
        print("index and thickness lists must match in length (Tfull)")
        return 
    Tmatrix=G12(nList[1],nList[0])
    #print("Tmatrix1",Tmatrix)
    for indices in range(len(dList)):
        Tmatrix=np.dot(P2(nList[indices+1],dList[indices],w),Tmatrix)
        Tmatrix=np.dot(G12(nList[indices+2],nList[indices+1]),Tmatrix)
    #print("Tmatrix1Final",Tmatrix) ## ORder 10 difference
    return Tmatrix ## this is a matrix


def Mfull(nList,dList,w,v):
    if len(nList) != len(dList)+2: 
        #print("index and thickness lists must match in length")
        return 
    m=S12(nList[-1], nList[-2], v, dList[0], w) 
    #print("m1",m)
    aux=[[1,0],[0,1]]
    for indices in range(len(dList)):
        aux=multi_dot([aux,G12(nList[-indices-1],nList[-indices-1-1]), P2(nList[-indices-1-1],dList[-indices-1],w)])
        mPlus=np.dot(aux,S12(nList[-indices-1-1],nList[-indices-2-1],v,np.sum(dList[0:indices+1]),w))
        #print(indices)
        m=m+mPlus

    return m 

def Bright(nList,dList,w,v):
    if len(nList) != len(dList)+2: 
        print("index and thickness lists must match in length (Bright)")
        return
    m=Mfull(nList,dList,w,v)
    t=Tfull(nList,dList,w,v)
    sol=(m[0][0]-((t[0][1]*m[1][0])/t[1][1]))
    return sol

def absolute(complexVal):
    realPart=complexVal.real
    complexPart=complexVal.imag
    theta=np.arctan(complexPart/realPart)
    amplitude=np.sqrt(realPart**2+complexPart**2)
    return amplitude

def make_IndexList(n1,n2,nLayers,mirror=False):
    ## Assuming always even number of layers
    if (nLayers%2!=0): 
        print("Please enter an even number of layers")
        return
    indList=np.zeros(nLayers)
    if mirror==0: indList[0]=1
    else: indList[0]=1e300
    #1e309 is infinity in python
    indList[-1]=1
    for i in range(1,nLayers-1):
        if (i%2!=0):
            indList[i]=n1
        else:
            indList[i]=n2
    return indList

def make_ThickList(d1,d2,nLayers):
    ##Assuming even number of layers
    if (nLayers%2!=0): 
        print("Please enter an even number of layers")
        return
    thickList=np.zeros(nLayers)
    for i in range(nLayers):
        if ((i+1)%2!=0):
            thickList[i]=d1
        else:
            thickList[i]=d2
    return thickList

# def make_chirpedThickList(d1,factor,nLayers):
#     chirpedList=np.zeros(nLayers)
#     for i in range(nLayers):
#         chirpedList[i]=d1*(factor**i)
#     return chirpedList

def make_chirplist(d1_,d2_,n1_,n2_,nLayers_,chirping_):
    x = Symbol('x')
    equation1=((d1_+x)-(d1_-x))/(d1_-x)-(chirping_-1)
    diff=np.array(solve(equation1,x))[0]
    y = Symbol('y') 
    equation2=(d1_ - diff)*(y**(nLayers_/2 - 1))-(d1_ - diff)*(chirping_);
    factor=np.array(solve(equation2,y))
    factor=[f for f in factor if (str(type(f))=="<class 'sympy.core.numbers.Float'>" and f>0)][0] 
    dList= np.array([[(d1_-diff)*factor**i,(d1_ - diff)*(factor**i)*n1_/n2_] for i in range(0,int(nLayers_/2))])
    dList=(dList.flatten()).astype(float)
    return dList


def phase_to_freq(theta,n,d):
    freq=(theta*c/(n*d))
    return freq

def phase_to_thick(theta,n,w):
    thick=(theta*c/(n*w))
    return thick

def freq_to_phase(w,n,d):
    phase=(n*d*w/c)
    return phase

def thick_to_freq(d,n):
    freq=(c*np.pi/(n*d))
    return freq

def freq_to_lamda(w):
    lamda=((2*np.pi*c/w)*1e9)
    return lamda ## returns in nm

def lamda_to_freq(lamda):
    freqToReturn=((2*np.pi*c/lamda)*1e9)
    return freqToReturn

def solution_rightwave(n1,n2,d1,nLayers,chirp=False,mirror=False,isTList=[]):
    ##nLayers is the number of layers in indexList
    d2=d1*n1/n2
    #nLayers=10
    #nL=[1,n1,n2,n1,n2,1]
    nL=make_IndexList(n1,n2,nLayers,mirror)

    #dL=[d1,d2,d1,d2]
    if chirp:
        dL=make_chirplist(d1,d2,n1,n2,nLayers-2,chirp) 
    else:
        dL=make_ThickList(d1,d2,nLayers-2)
    if len(isTList)>0:
        dL=isTList
       


    wmid=np.pi*c/(n1*d1)
    wmin=wmid*0.5 ##0.5
    wmax=wmid*2.5 ##1.5
    wL=np.linspace(wmin,wmax,1000)

    v=0
  #  print(dL)
    solList=[]
    for w in wL:
        solution=Bright(nL,dL,w,v)
       # print(solution)
        solList.append(absolute(solution))
    return wL,np.array(solList) 