import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import scipy.constants as c
import pandas as pd
from tqdm import tqdm
from lens import *
from ray import *
from detector import *


# Create lens 1
arc1 = Arc(C=np.array([-1,0]),R=2,dirPositive=False)
arc2 = Arc(C=np.array([-5,0]),R=4,dirPositive=True)
lens = Lens(arc1,arc2, noiseStd=1, noiseAmplitude=10)

# Create lens 2
arc3 = Arc(C=np.array([-2.5,0]),R=2.5,dirPositive=True)
arc4 = Arc(C=np.array([-1.5,0]),R=2,dirPositive=True)
lens2 = Lens(arc3,arc4, noiseStd=1, noiseAmplitude=10)

# Create the figure 
fig = plt.figure(figsize=(7,7),dpi=100)
ax = fig.add_subplot(211,aspect='equal')
ax.grid()
ax.set_ylim(-2,2)
ax.set_xlim(-4,5)

# Simulation Parameters
Nrays = 1000
RayEnergyRange = [0.2,5.9] # eV
RayGenerationRange = [-1.5,1.5]

# Create Rays
rays = []
for i in range(Nrays):rays.append(Ray(start=np.array([-4,random(*RayGenerationRange)]),energy=random(*RayEnergyRange)))

# Shoot the rays
print("Shootting Rays")
for ray in tqdm(rays):
    # ray.shootThroughLens(lens)
    # ray.VERBOSE = True
    ray.shootThroughLenses([lens,lens2])
    ray.draw(ax,color='aqua')

# Create Detector
detector = Detector(position=np.array([1,0]),height=1)
detector.draw(ax)
lens.draw(ax)
lens2.draw(ax)

# Count hits and plot density
detector.countHits(rays)
detector.densityPlot(ax=fig.add_subplot(212),bandwidth=0.05)

plt.show()
