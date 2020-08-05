# Contains class for lens
import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as c
import pandas as pd
import scipy.linalg as la

from curves import *


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