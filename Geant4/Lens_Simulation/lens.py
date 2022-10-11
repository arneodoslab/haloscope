# Contains class for lens
import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as c
import pandas as pd
import scipy.linalg as la

from curves import *


# This class represents a lens
class Lens:

    # Constructor
    def __init__(self,curves,refractive_index_filename = 'NBK7.csv', noise_amplitude:float = 0, noise_std:float = 0, thickness:float = 0):
        self.curves = curves                    # The curves that constitute the lens
        self.noise_amplitude = noise_amplitude    # The amplitude of the perlin noise added to the surface
        self.noise_std = noise_std                # The std of the perlin noise added to the surface
        self.refractive_index_data = pd.read_csv(refractive_index_filename,skiprows=1).values.T     # Reads CSV file with the refractive index data and saves it there
        self.add_thickness(thickness)            # Function to add the requested thickness for the lens
        self.thickness = thickness              # The thickness of the lens

    # Draws the lens in an ax object
    def draw(self, ax = None, Npts = 100, figsize = (5,5), dpi = 200):
        if ax == None:
            fig = plt.figure(figsize = figsize, dpi=dpi)
            ax  = fig.add_subplot(111,aspect='equal')

        for curve in self.curves:
            curve.draw(ax,color='darkblue',Npts=Npts)

        # plt.show()


    # Returns the reftactive index at a particular wavelength
    def get_refractive_index(self,energy):
        return np.interp(energy,self.refractive_index_data[0],self.refractive_index_data[1])

    # Draws the frenet frame of each curve at certain points
    def draw_frenet_frame(self,ax,color='darkgreen',Npts=15,label='Frenet Frame of spline'):
        for curve in self.curves:
            curve.draw_frenet_frame(ax,color,Npts,label)

    # Moves the center position of each of the two curves so that they are thickness apart
    def add_thickness(self,thickness):
        return
        # self.curves[0].position += np.array([-thickness/2,0.])
        # self.curves[1].position += np.array([ thickness/2,0.])
    