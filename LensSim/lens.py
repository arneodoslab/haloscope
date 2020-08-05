# Contains class for lens
import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as c
import pandas as pd
import scipy.linalg as la

from curves import *

# class Lens:

#     def __init__(self, arc1,arc2,rotate=0,refractiveIndexFilename = 'NBK7.csv', noiseAmplitude:float = 0, noiseStd:float = 0, thickness:float = 0):
#         self.arc1 = arc1
#         self.arc2 = arc2
#         self.arcs = [self.arc1,self.arc2]
#         self.noiseAmplitude = noiseAmplitude
#         self.noiseStd = noiseStd
#         self.refractiveIndexData = pd.read_csv(refractiveIndexFilename,skiprows=1).values.T
#         self.calculateIntersectionAngles()
#         self.addThickness(thickness)
#         self.thickness = thickness
        
#         # self.rotate(0)

#     def addThickness(self,thickness):
#         for arc in self.arcs:
#             i = np.array([1,0])
#             if not arc.dirPositive: i = -1*i

#             arc.C += i*thickness

#     # Returns the angles that the two arcs intersect
#     def calculateIntersectionAngles(self):
#         # in case the circles don't intersect
#         R1 = self.arc1.R
#         R2 = self.arc2.R
#         R3 = mag(self.arc1.C-self.arc2.C)
#         if R1+R2+R3 - 2*max(R1,R2,R3) < 0: # The sum of the two shortest sides isn't larger than the longest
#             return 0,0,0,0
        
#         #If they intersect
#         self.arc1.theta = 2*np.arccos((R1**2 + R3**2 - R2**2) / (2 * R1 * R3))
#         self.arc2.theta = 2*np.arccos((R2**2 + R3**2 - R1**2) / (2 * R2 * R3))
        
#         for arc in [self.arc1,self.arc2]:
#             if arc == self.arc1: other = self.arc2
#             else: other = self.arc1
#             arc.phi = 0

#             if arc.dirPositive:
#                 if (arc.C-other.C).dot(np.array([1,0])) > 0:
#                     arc.phi   = np.pi + arc.theta/2
#                     arc.theta = 2*np.pi - arc.theta
#                 else:
#                     arc.phi = 2*np.pi - arc.theta/2
            
#             else:
#                 if (arc.C-other.C).dot(np.array([1,0])) < 0:
#                     arc.phi   = arc.theta/2
#                     arc.theta = 2*np.pi - arc.theta
#                 else:
#                     arc.phi = np.pi - arc.theta/2


#     def draw(self, ax = None, Npts = 100, figsize = (5,5), dpi = 200):
#         if ax == None:
#             fig = plt.figure(figsize = figsize, dpi=dpi)
#             ax  = fig.add_subplot(111,aspect='equal')

#         for arc in [self.arc1,self.arc2]:
#             arc.draw(ax,color='darkblue',Npts=Npts)

#         # plt.show()

#     def getArcs(self):
#         return [self.arc1,self.arc2]

#     def getRefractiveIndex(self,energy):
#         return np.interp(energy,self.refractiveIndexData[0],self.refractiveIndexData[1])

# This class represents a lens
class Lens:

    def __init__(self,curves,refractiveIndexFilename = 'NBK7.csv', noiseAmplitude:float = 0, noiseStd:float = 0, thickness:float = 0):
        self.curves = curves
        self.noiseAmplitude = noiseAmplitude
        self.noiseStd = noiseStd
        self.refractiveIndexData = pd.read_csv(refractiveIndexFilename,skiprows=1).values.T
        self.addThickness(thickness)
        self.thickness = thickness

    # Draws the lens in an ax object
    def draw(self, ax = None, Npts = 100, figsize = (5,5), dpi = 200):
        if ax == None:
            fig = plt.figure(figsize = figsize, dpi=dpi)
            ax  = fig.add_subplot(111,aspect='equal')

        for curve in self.curves:
            curve.draw(ax,color='darkblue',Npts=Npts)

        # plt.show()


    # Returns the reftactive index at a particular wavelength
    def getRefractiveIndex(self,energy):
        return np.interp(energy,self.refractiveIndexData[0],self.refractiveIndexData[1])

    # Moves the center position of each of the two curves so that they are thickness apart
    def addThickness(self,thickness):
        self.curves[0].position = np.array([-thickness/2,0])
        self.curves[1].position = np.array([ thickness/2,0])