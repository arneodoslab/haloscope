# local pacakges
import computation
import optimization
import rate

# utilities
import sys,getopt
from datetime import datetime
import itertools  

# numerical computing
import numpy as np
import pandas as pd
import math
from scipy import integrate
from scipy import stats as sps
from scipy import optimize as opt
import scipy.constants as const
from scipy.interpolate import interp1d
from scipy.optimize import brentq

# plotting
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.ticker import MaxNLocator
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import FuncFormatter

AREA_DEFAULT = np.pi*(2.5)**2


##--- statistics functions

##--- Option A

##--- upper limit
def poisson_interval(n,gamma=0.1):
    if n==0:
        ld = 0.
    else:
        ld = 0.5*sps.chi2(2*n).ppf(0.5*gamma)
    lu = 0.5*sps.chi2(2*n+2).ppf(1-0.5*gamma)
    return(ld,lu)

def poisson_1sided_interval(n,beta,limit="upper"):
    if limit=="upper":
        return poisson_interval(n,beta)[1]
    else: 
        return poisson_interval(n,beta)[0]

##--- discovery power
def disc_powerA(muB_,sigmaDiscovery_=5):
    xc = sps.poisson(muB_).ppf(sps.norm.cdf(sigmaDiscovery_)) ## critical value
    muS = np.linspace(0,25,25)
    mu1 = muB_ + muS ## alternate hypothesis
    disPow = []
    for i in mu1:
        disPow.append(1-sps.poisson(i).cdf(xc))
    print('critical x value (for which alpha = 5 sigma) is', xc)
    muStar = np.interp(0.5, disPow, muS)
    print('mu* value (for which alpha = 5 sigma) is', muStar)
    return muStar

##--- Option B

##--- log likelihood ratio calculation
def hathatb(n_on, n_off, alpha, s):
    """
        best-fit b _conditional_ on a fixed s
    """
    if s==0.:
        hhb = (n_on+n_off) / (1+alpha)
        return hhb
    a = alpha*(1+alpha)
    b = s*(1+alpha) - alpha*(n_on + n_off)
    c = -1.*n_off * s
    hhb = (-b + np.sqrt(b**2-4*a*c)) / (2*a)
    return hhb

def hatsb(n_on, n_off , alpha, s_positive = False):
    """
        returns best-fit s,b (and demands that 0<s-- if s is small this means trouble!)
    """
    hs = float(n_on - alpha*n_off)
    if s_positive and hs<0:
        hs = 0.
        hb = hathatb(n_on, n_off, alpha, hs)
    else:
        hb = float(n_off)
    return hs,hb

#s0 is the null-hypothesis signal strength
def llr(n_on, n_off, alpha, s0,s_positive = False):
    """
    log-likelihood ratio. at the moment, s is not forced positive. 
    """
    hs, hb = hatsb(n_on, n_off, alpha)
    hhb = hathatb(n_on, n_off, alpha, s0)
    
    ret  = sps.poisson(hs+alpha*hb).logpmf(n_on) + sps.poisson(hb).logpmf(n_off) #best-fit likelihood
    ret -= sps.poisson(s0+alpha*hhb).logpmf(n_on) + sps.poisson(hhb).logpmf(n_off) #-conditional best-fit
    return 2.*ret

def llr2(n_on, n_off, alpha, s0,s_positive = False):
    """
    log-likelihood ratio. at the moment, s is not forced positive. 
    """
    hs, hb = hatsb(n_on, n_off, alpha)
    hhb = hathatb(n_on, n_off, alpha, s0)
    
    ret = n_on * np.log((alpha*hb+hs)/(alpha*hhb+s0)) + n_off * np.log(hb/hhb) - (hs - s0) - (alpha+1)* (hb-hhb)
    return 2.*ret

##--- upper limit
def upper_limitB(muB_,dayson,daysoff,plot=False,mu_=1):

    ton =  dayson * 24 * 60 * 60
    toff = daysoff *24* 60 * 60
    #toff =1
    #ton=1
    
    alpha = ton/toff
   

    n_on = sps.poisson(mu_ * ton).median()
    n_off = sps.poisson(muB_ * toff).median()
#         signal = n_on- alpha *n_off
#         n_on_median = signal + alpha*n_off
#         n_off_median = n_off*alpha

    #TS_threshold = sps.chi2(1).isf(2.*0.1) #the reason for the factor 2 is that we're doing an upper-limit only-- 
    print("non0, noff0:", n_on,n_off)

    TS_threshold = sps.chi2(1).ppf(0.8)
    function = lambda s : llr(n_on, n_off, alpha, s, s_positive=True) - TS_threshold
    
    xd = max(0,  n_on- alpha * n_off)
    xu = n_on + 100*np.sqrt(n_on)
    
    crossing = brentq(function,xd,xu)
    
    print("non, noff:", n_on,n_off)
    print("the signal at which the median no-signal dataset is excluded at 90% confidence is",crossing)

    return (crossing)
    #return (0)

##--- discovery power
def discovery_powerB(muB_,days=1):
    #bgd = bg*24*60*60
    #print(np.round(bgd))
    muB_ = np.floor(muB_ * days * 24 * 60 * 60)
    TS_ = sps.chi2(1).ppf(sps.norm.cdf(5))
    alpha=1
    fc = lambda strength : llr(sps.poisson(strength+alpha*muB_).median(), muB_, alpha, 0, s_positive=True) - TS_
    try:
        sStar = brentq(fc,0.,1000.)
    except:
        sStar = brentq(fc,(muB_*0.01)/(days*24*60*60),(muB_*1000)/(days*24*60*60))
    #sStar = brentq(fc,0.,100.)
    return sStar

def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)
##--- stack functions

def n_vs_eV(kappa=1e-11,fDM=1,hitRate=0.75,area=AREA_DEFAULT,timeon=1):
    '''
    area in units of cm^2
    time in units of days
    returns energy,number of events
    '''
    m,rate_curve = rate.get_rate(kappa)
    N = rate_curve*(m*area*timeon)
    return m,N

##--- helper functions
def get_critical(paramDict):
    """
    paramDict - dictionary of input choices
    returns corresponding list of critical values
    """
    muS = np.zeros(len(paramDict))
    beta = 0.2
    
    for i,keys in enumerate(paramDict):
        choice = paramDict[keys][0] 
        timeon = paramDict[keys][2]
        timeoff = paramDict[keys][3]

        print('time when we get critical')
        print(timeon,timeoff)
        bgd = paramDict[keys][1]
        mu = paramDict[keys][-2]

        if (choice=="A1"):
            muS[i] = (poisson_1sided_interval(bgd*timeoff*24*60*60,beta)-np.round(bgd*timeoff*24*60*60))*(timeon/timeoff)
        if (choice=="A2"):
            sigmaDiscovery = 5
            muS[i] = disc_powerA(bgd,sigmaDiscovery)
        if (choice=="B1"):
            muS[i] = upper_limitB(bgd,dayson=timeon,daysoff=timeoff,mu_=mu)
        if (choice=="B2"):
            muS[i] = discovery_powerB(bgd,days=timeon)
    print('muS:')
        
    print(muS)
    return muS 
    

def main(argv):
    
    #--- default values
    mu = 0
    bgd = 0
    timeon = 1 
    choices = []
    percentile = 1
    labelDict =	{
                "A1": "Option A, Upper Limit",
                "A2": "Option A, Discovery Power",
                "B1": "Option B, Upper Limit ",
                "B2": "Option B, Discovery Power"
                }
    
    # getting the correct energy values based on sensors    
    energyMatsu, __ = n_vs_eV(kappa=1e-11,fDM=1,hitRate=0.75)
    wave=const.h*const.c/(energyMatsu*1e-9)*6.2*1e18
    maskEx = wave<max(optimization.qeData("excelitas_qe.csv")[0])
    energyExcel = energyMatsu[maskEx]
    maskLC = wave<max(optimization.qeData("laser-components_qe.csv")[0])
    energyLC = energyMatsu[maskLC]
    
    energyMap = {"matsu":energyMatsu,"excelitas":energyExcel,"TES":energyExcel,"LC":energyLC} 
    parameterMap = {}
    count = 0
    axions=False
    bfield=0
    #--- user input at each step
    inputString = ""
    while (inputString!="exit" and inputString!="e"):
        try:
            mu = float(input ("Enter observed rate in Hz:"))
            bgd = float(input ("Enter bgd rate in Hz :"))
            timeon = float(input ("Enter measurement time in hours :"))/24
            timeoff = float(input ("Enter background time in hours :"))/24
            qeChoice = input ("Enter the sensor ('matsu','excelitas','LC', or 'TES') :")
            plotChoice = input ("Enter the type of plot (A1,A2,B1,B2) :")
            boostpercentile = int(input ("Enter the percentile to use, 100 for full boost :"))
            parameterMap[str(count)]=[plotChoice,bgd,timeon,timeoff,qeChoice,mu,boostpercentile]
            axions = bool(input ("Enter (True) to switch to axion search:"))
            if axions:
                bfield = float(input ("Enter the B Field Used in Tesla:"))

            inputString = input ("type 'e' or 'exit' to quit, anything else to add more options :")
            count+=1
            if count==5 : break ## more than 5 plots will be painful
        except KeyboardInterrupt:
            print('Keyboard Interrupt. Skip...S\n')
            continue
            
    #--- get the critical vals
    muS = get_critical(parameterMap)
    #--- set up plotting environment
    plt.rcParams.update({'font.size': 16})
    print(axions)
    formatter = FuncFormatter(lambda y, _: '{:.3g}'.format(y))

    fig,ax = plt.subplots(figsize=(10,8)) # set up the figure

    #--- get kappa values and plot
    cmap = get_cmap(len(choices))
    maxlim = 0
    print('Parameter map:')
    print(parameterMap)
    print('enumerate Parameter map:')
    print(list(enumerate(parameterMap)))
    for i,keys in enumerate(parameterMap):
        
        choice = parameterMap[keys][0]
        sensor = parameterMap[keys][-3]
        per = parameterMap[keys][-1]
        energy = energyMap[sensor]
        kAnalytic = np.zeros(len(energy)) ## store all kappa values here
        
        for j,e in enumerate(energy):
            kAnalytic[j] = rate.get_kappa(j,muS[i],timeon,sensor=sensor,percentile=per)
            if axions:
                kAnalytic[j] = rate.get_g_agamma(bfield,j,muS[i],timeon,sensor=sensor,percentile=per)

           
        maxlim = max(maxlim,max(kAnalytic))
        nowtime = datetime.now()
        dt_string = nowtime.strftime("%Y%m%d%H%M%S")
        if(~axions):
            np.save("./plot-data/"+dt_string+"B"+str(bgd)+choice+"T"+str(np.round(timeon,2))+sensor+"Per"+str(per),kAnalytic)
            np.save("./plot-data/"+dt_string+"B"+str(bgd)+choice+"T"+str(np.round(timeon,2))+sensor+"Per"+str(per)+"-energy",energy)

        #--- plotting
        if(axions):
            print(i)
            print("Producing the plot for:"+labelDict[choice])
            print("$g_agamma  min", min(kAnalytic))
            print("Energies:")
            print(repr(energy))
            print("g_agamma  Values:")
            print(repr(kAnalytic))

            ax.plot(energy,kAnalytic,c="C"+str(i),label=labelDict[choice]+","+parameterMap[keys][-3]+","+"bgd="+str(parameterMap[keys][1])+" Hz"+","+"mu="+str(parameterMap[keys][-2])+" Hz")

            #--- plot formatting
            ax.set_yscale("log")
            ax.set_xscale("log")

            #ax.set_ylim(1e-18,maxlim)
            ax.set_xlim(0.1,30)
            ax.set_xticks([0.1,0.2,0.5,1.0,2.0,5.0,10,20])

            ax.xaxis.set_major_formatter(formatter)

            plt.xlabel("mass [eV/c$^2$]")
            plt.grid(linestyle="--")
            plt.ylabel("$g_{a\gamma} $ [eV/Tesla]")
            plt.legend()
            plt.show()
        else:
            #print(i)
            #print("Producing the plot for:"+labelDict[choice])
            #print("kappa min", min(kAnalytic))
            #print("Energies:")
            #print(repr(energy))
            #print("k Values:")
            #print(repr(kAnalytic))

            ax.plot(energy,kAnalytic,c="C"+str(i),label=labelDict[choice]+","+parameterMap[keys][-3]+","+"bgd="+str(parameterMap[keys][1])+" Hz"+","+"mu="+str(parameterMap[keys][-2])+" Hz")


            #--- plot formatting
            ax.set_yscale("log")
            ax.set_xscale("log")

            #ax.set_ylim(1e-18,maxlim)
            ax.set_xlim(0.1,30)
            ax.set_xticks([0.1,0.2,0.5,1.0,2.0,5.0,10,20])

            ax.xaxis.set_major_formatter(formatter)

            plt.xlabel("mass [eV/c$^2$]")
            plt.grid(linestyle="--")
            plt.ylabel("$\kappa$")
            plt.legend()
            plt.show()
            
                

if __name__ == "__main__":
    main(sys.argv[1:])
