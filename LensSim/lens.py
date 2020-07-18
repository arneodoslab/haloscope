# Contains class for lens
import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as c
import pandas as pd

def mag(a:np.array):
    return a.dot(a)**0.5

def arg(a):
    if a[0] == 0:
        if a[1]>0:
            return np.pi/2
        else:
            return 3/2*np.pi

    elif a[0]>0:
        if a[1]>0:
            return np.arctan(a[1]/a[0])
        else:
            return np.arctan(a[1]/a[0])+2*np.pi

    else:
        return np.arctan(a[1]/a[0])+np.pi

def random(m,M):
    return np.random.rand()*(M-m) + m

def isInRange(a,m,M):
    if (a > m and a < M) or (a + 2*np.pi > m and a + 2*np.pi < M):
        return True
    else: 
        return False

def minAngle(a,b):
    a.dot(b)


class Arc:
    def __init__(self, C:np.array = np.array([0,0]),R:float = 1,theta:float = 2*np.pi, phi:float = 0, dirPositive:bool = False,pointX:np.array = None,pointY:np.array = None):
        
        if type(pointX) == type(None) or type(pointY) == type(None):
            self.C = C
            self.R = R
            self.theta = theta
            self.phi = phi
            self.dirPositive = dirPositive

        else:
            # Find the center and radius of the arc, and decide its direction
            p = 1/2*(pointX + pointY)
            v = pointY - pointX
            v[0] = v[1]
            v[1] = -(pointY-pointX)[0]
            v = v/mag(v)
            l = - p[1]/v[1]
            self.C = p+v*l
            self.R = mag(self.C - pointX)
            self.theta = arg(pointY-self.C)
            self.dirPositive = (pointX-self.C).dot(np.array([1,0])) >= 0
            if not self.dirPositive:
                self.phi = self.theta/2
                self.theta = 2*np.pi - self.theta
            else:
                self.phi = 2*np.pi - self.theta/2

            

    def draw(self,ax,color='k',Npts=100,label='Lens'):
        angles = np.linspace(self.phi,self.phi+self.theta,Npts)
        ptsX = self.R*np.cos(angles) + self.C[0]
        ptsY = self.R*np.sin(angles) + self.C[1]

        ax.scatter(self.R*np.cos(angles[0])+self.C[0],self.R*np.sin(angles[0])+self.C[1])
        
        return ax.plot(ptsX,ptsY, c=color, label=label)

    def print(self):
        print("Object of type arc.\n\n\tC = "+str(self.C)\
            +"\n\tR = "+str(self.R)\
            +"\n\tTheta = "+str(self.theta*180/np.pi)\
            +"\n\tphi = "+str(self.phi*180/np.pi)\
            +"\n\tdirPositive = "+str(self.dirPositive)+"\n")

class Lens:

    def __init__(self, arc1:Arc,arc2:Arc,rotate=0,refractiveIndexFilename = 'NBK7.csv', noiseAmplitude:float = 0, noiseStd:float = 0):
        self.arc1 = arc1
        self.arc2 = arc2
        self.noiseAmplitude = noiseAmplitude
        self.noiseStd = noiseStd
        self.refractiveIndexData = pd.read_csv(refractiveIndexFilename,skiprows=1).values.T
        self.calculateIntersectionAngles()
        # self.rotate(0)


    # Returns the angles that the two arcs intersect
    def calculateIntersectionAngles(self):
        # in case the circles don't intersect
        R1 = self.arc1.R
        R2 = self.arc2.R
        R3 = mag(self.arc1.C-self.arc2.C)
        if R1+R2+R3 - 2*max(R1,R2,R3) < 0: # The sum of the two shortest sides isn't larger than the longest
            return 0,0,0,0
        
        #If they intersect
        self.arc1.theta = 2*np.arccos((R1**2 + R3**2 - R2**2) / (2 * R1 * R3))
        self.arc2.theta = 2*np.arccos((R2**2 + R3**2 - R1**2) / (2 * R2 * R3))
        
        for arc in [self.arc1,self.arc2]:
            if arc == self.arc1: other = self.arc2
            else: other = self.arc1
            arc.phi = 0

            if arc.dirPositive:
                if (arc.C-other.C).dot(np.array([1,0])) > 0:
                    arc.phi   = np.pi + arc.theta/2
                    arc.theta = 2*np.pi - arc.theta
                else:
                    arc.phi = 2*np.pi - arc.theta/2
            
            else:
                if (arc.C-other.C).dot(np.array([1,0])) < 0:
                    arc.phi   = arc.theta/2
                    arc.theta = 2*np.pi - arc.theta
                else:
                    arc.phi = np.pi - arc.theta/2


    def draw(self, ax = None, Npts = 100, figsize = (5,5), dpi = 200):
        if ax == None:
            fig = plt.figure(figsize = figsize, dpi=dpi)
            ax  = fig.add_subplot(111,aspect='equal')

        for arc in [self.arc1,self.arc2]:
            arc.draw(ax,color='darkblue',Npts=Npts)

        # plt.show()

    def getArcs(self):
        return [self.arc1,self.arc2]

    def getRefractiveIndex(self,energy):
        return np.interp(energy,self.refractiveIndexData[0],self.refractiveIndexData[1])