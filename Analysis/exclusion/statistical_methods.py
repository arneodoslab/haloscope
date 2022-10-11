# numerical computing
import numpy as np
import pandas as pd
from scipy import integrate
from scipy import stats as sps
from scipy import optimize as opt
import scipy.constants as const
from scipy.interpolate import interp1d
from scipy.optimize import brentq


##########################################
##--- statistics functions  ---###########
##########################################


##########################################
##--- Option A (Poisson statistics)
##########################################
##--- upper limit using poisson statistics
def poisson_interval(n,gamma=0.1):
    if n==0:
        ld = 0.
    else:
        ld = 0.5*sps.chi2(2*n).ppf(0.5*gamma)
    lu = 0.5*sps.chi2(2*n+2).ppf(1-0.5*gamma)
    return(ld,lu)

##--- selection method for getting upper vs lower limits using poisson interval
def poisson_1sided_interval(n,beta,limit="upper"):
    if limit=="upper":
        return poisson_interval(n,beta)[1]
    else: 
        return poisson_interval(n,beta)[0]

##--- discovery power using poisson statistics
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

##########################################
##--- Option B
##########################################
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
def upper_limitB(n_on,n_off,days_on,days_off,plot=False):

    ton =  days_on * 24 * 60 * 60
    toff = days_off *24* 60 * 60
    #toff =1
    #ton=1
    
    alpha = ton/toff
   

    n_on = sps.poisson(n_on).median()
    n_off = sps.poisson(n_off).median()
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
