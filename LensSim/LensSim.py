import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox
import scipy.constants as c
import pandas as pd
from tqdm import tqdm
from lens import *
from ray import *
from detector import *


# Simulation Parameters
Nrays = 100
RayEnergyRange = [0.2,5.9] # eV
RayGenerationRange = [-1.5,1.5]
RayGenerationXPos = -4
Bandwidth = 0.1
noiseStd = 0.01
noiseAmplitude = 0
VERBOSE = False


# Create lens 1
arc1 = Arc(C=np.array([-1,0]),R=2,dirPositive=False)
arc2 = Arc(C=np.array([-15,0]),R=14,dirPositive=True)
lens = Lens(arc1,arc2, noiseStd=noiseStd, noiseAmplitude=noiseAmplitude)

# Create lens 2
arc3 = Arc(C=np.array([1,0]),R=1,dirPositive=False)
arc4 = Arc(C=np.array([2,0]),R=1.5,dirPositive=False)
lens2 = Lens(arc3,arc4, noiseStd=noiseStd, noiseAmplitude=noiseAmplitude)

lenses = [lens]

# Create rays list
rays = []

# Create Detector
detector = Detector(position=np.array([1.,0.]),height=1)


# GUI
controlH = 0.75
dist = 0.05
right = 0.8
left = 0.2
ylim = [-2,2]
xlim = [-4,5]
color = 'blue'

# Create the figure
plt.rcParams["font.family"] = 'monospace'
fig = plt.figure('Ray Simulation',figsize=(7,8),dpi=120)
plt.subplots_adjust(top=0.75,bottom=0.05)
ax = fig.add_subplot(211,aspect='equal')
ax.grid()
ax.set_ylim(*ylim)
ax.set_xlim(*xlim)
detectorAx = fig.add_subplot(212)

# Add Sliders
spawn = np.arange(*RayGenerationRange,0.1)

axBandwidth = plt.axes([left,controlH,0.5,0.03])
sBandwidth = Slider(axBandwidth, 'Light Bandwidth', 0.01,10, valinit=3, valstep=0.01, color=color)

axNumber = plt.axes([left, controlH+dist, 0.50, 0.03])
sNumber = Slider(axNumber, 'Number of Rays', 1, 1000, valinit=Nrays, valstep=1, color=color)

axEnergy = plt.axes([left, controlH+2*dist, 0.50, 0.03])
sEnergy = Slider(axEnergy, 'Energy of Rays', *RayEnergyRange, valinit=2, valstep=0.01, color=color)

axDetector = plt.axes([left,controlH+3*dist,0.5,0.03])
sDetector = Slider(axDetector, 'Detector Pos', *xlim, valinit=1, valstep=0.01, color=color)

# Add Buttons
axShoot = plt.axes([right, controlH, 0.1, 0.04])
bShoot = Button(axShoot, 'Shoot', hovercolor=color, color='0.975')

# Add Radio Buttons
axRadio = plt.axes([right,controlH+dist,0.1,0.08])
radio = RadioButtons(axRadio, ('random','linear'),active = 1)

# Add text box inputs
axDetectorWidth = plt.axes([left,controlH+4*dist,0.1,0.04])
tDetectorWidth = TextBox(axDetectorWidth,'Detector Width ',initial='1')

axNoiseSTD = plt.axes([left+0.3,controlH+4*dist,0.1,0.04])
tNoiseSTD = TextBox(axNoiseSTD,'Noise STD ',initial='0.01')

axNoiseAmplitude = plt.axes([left+0.6,controlH+4*dist,0.1,0.04])
tNoiseAmplitude = TextBox(axNoiseAmplitude,'Noise Amplitude ',initial='0')


# Function to shoot the rays
def shootRays(rays,lenses,ax=ax,draw=True,VERBOSE=False,color='aqua'):
    # Shoot the rays
    print("Shootting Rays")
    for ray in tqdm(rays):
        ray.VERBOSE = VERBOSE
        ray.shootThroughLenses(lenses)
        ray.draw(ax,color=color)

# Create Rays
def createRays(Nrays=Nrays,RayGenerationXPos=RayGenerationXPos,RayGenerationRange=RayGenerationRange,RayEnergyRange=RayEnergyRange,rand=True):
    rays = []
    print("Creating Rays")

    length = np.linspace(*RayGenerationRange,Nrays)
    for i in tqdm(range(Nrays)):
        if rand: ray = Ray(start=np.array([RayGenerationXPos,random(*RayGenerationRange)]),energy=random(*RayEnergyRange))
        else: ray = Ray(start=np.array([RayGenerationXPos,length[i]]),energy=random(*RayEnergyRange))
        rays.append(ray)

    return rays

def drawLenses(lenses,ax):
    for lens in lenses:
        lens.draw(ax)

def update(val=-1):
    ax.cla()

    ax.grid()
    ax.set_ylim(-2,2)
    ax.set_xlim(-4,5)

    # Update lenses
    for lens in lenses:
        lens.noiseStd = float(tNoiseSTD.text)
        lens.noiseAmplitude = float(tNoiseAmplitude.text)

    # Create and shoot new rays
    global rays
    rays = createRays(Nrays=int(sNumber.val),RayEnergyRange=[sEnergy.val]*2,rand=radio.value_selected=='random',\
        RayGenerationRange=[-sBandwidth.val/2,sBandwidth.val/2])
    shootRays(rays,lenses,VERBOSE=VERBOSE)

    # Plot lenses
    drawLenses(lenses,ax)

    # Update and Plot detector
    detector.position[0] = sDetector.val
    detector.generateLineMesh()
    detector.draw(ax)

    # Count hits and plot density
    detectorAx.cla()
    detector.countHits(rays)
    detector.densityPlot(ax=detectorAx, bandwidth=Bandwidth)
    fig.canvas.draw_idle()

def moveDetector(val = -1):
    # Update and plot Detector
    ax.get_lines()[-1].remove()
    detector.position[0] = sDetector.val
    detector.height = float(tDetectorWidth.text)
    detector.generateLineMesh()
    detector.draw(ax)

    # Count hits and plot density
    detectorAx.cla()
    detector.countHits(rays)
    detector.densityPlot(ax=detectorAx, bandwidth=Bandwidth)
    fig.canvas.draw_idle()




sNumber.on_changed(update)
sEnergy.on_changed(update)
sDetector.on_changed(moveDetector)
bShoot.on_clicked(update)
tDetectorWidth.on_submit(moveDetector)
tNoiseSTD.on_submit(update)
tNoiseAmplitude.on_submit(update)

update()
plt.show()