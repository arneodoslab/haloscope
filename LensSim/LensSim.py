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
rayEnergy = 1.5
rayBandwidth = 5.08
RayEnergyRange = [0.2,5.9] # eV
RayGenerationRange = [-2.54,2.54]
RayGenerationXPos = -4

detectorPos = 2
detectorWidth = 0.1
Bandwidth = 0.1

noiseStd = 0.01
noiseAmplitude = 0

# lensRightPoint = np.array([0.4316416,0])
# lensLeftPoint = np.array([-0.66065332,0])
lensRightPoint = np.array([0.1578881,0])
lensLeftPoint = np.array([-0.43856842,0])
lensCommonPoint = np.array([0,2.54])

rayXlim = [-4,20]
rayYlim = [-3,3]


VERBOSE = False


# Create lens 1
arc1 = Arc(pointX=lensRightPoint,pointY=lensCommonPoint)
arc2 = Arc(pointX=lensLeftPoint,pointY=lensCommonPoint)
lens = Lens(arc1,arc2, noiseStd=noiseStd, noiseAmplitude=noiseAmplitude, thickness=0.18)

# # Create lens 2
# arc3 = Arc(pointX=np.array([2,0]),pointY=np.array([1,1]))
# arc4 = Arc(C=np.array([2,0]),R=1.5,dirPositive=False)
# lens2 = Lens(arc3,arc4, noiseStd=noiseStd, noiseAmplitude=noiseAmplitude)

lenses = [lens]

# Create rays list
rays = []

# Create Detector
detector = Detector(position=np.array([detectorPos,0.]),height=detectorWidth)

# GUI ######################################################################
height = 0.03
controlH = 0.75
dist = height + 0.01
right = 0.8
left = 0.2
ylim = [-2,2]
xlim = [-4,5]
color = 'blue'
dpi = 110
figsize = (7,9)

# Create the figure
plt.rcParams["font.family"] = 'monospace'
fig = plt.figure('Ray Simulation',figsize=figsize,dpi=dpi)
plt.subplots_adjust(top=0.75,bottom=0.05)
ax = fig.add_subplot(211,aspect='equal')
ax.grid()
ax.set_ylim(*ylim)
ax.set_xlim(*xlim)
detectorAx = fig.add_subplot(212)

# Add Sliders
spawn = np.arange(*RayGenerationRange,0.1)

axBandwidth = plt.axes([left,controlH,0.5,height])
sBandwidth = Slider(axBandwidth, 'Light Bandwidth', 0.01,10, valinit=rayBandwidth, valstep=0.01, color=color)

axNumber = plt.axes([left, controlH+dist, 0.5, height])
sNumber = Slider(axNumber, 'Number of Rays', 1, 1000, valinit=Nrays, valstep=1, color=color)

axEnergy = plt.axes([left, controlH+2*dist, 0.5, height])
sEnergy = Slider(axEnergy, 'Energy of Rays', *RayEnergyRange, valinit=rayEnergy, valstep=0.01, color=color)

axDetector = plt.axes([left,controlH+3*dist,0.5,height])
sDetector = Slider(axDetector, 'Detector Pos', *xlim, valinit=detectorPos, valstep=0.01, color=color)

# Add Buttons
axShoot = plt.axes([right, controlH, 0.1, height])
bShoot = Button(axShoot, 'Shoot', hovercolor=color, color='0.975')

axSweep = plt.axes([right,controlH+dist*3,0.1,height])
bSweep = Button(axSweep, 'Sweep', hovercolor=color, color='0.975')

# Add Radio Buttons
axRadio = plt.axes([right,controlH+dist,0.1,height+dist])
radio = RadioButtons(axRadio, ('random','linear'),active = 1)

# Add text box inputs
axDetectorWidth = plt.axes([left,controlH+4*dist,0.1,height])
tDetectorWidth = TextBox(axDetectorWidth,'Detector Width ',initial=str(detectorWidth))

axNoiseSTD = plt.axes([left+0.3,controlH+4*dist,0.1,height])
tNoiseSTD = TextBox(axNoiseSTD,'Noise STD ',initial='0.01')

axNoiseAmplitude = plt.axes([left+0.6,controlH+4*dist,0.1,height])
tNoiseAmplitude = TextBox(axNoiseAmplitude,'Noise Amplitude ',initial='0')

axStartPos = plt.axes([left,controlH+5*dist,0.1,height])
tStartPos = TextBox(axStartPos,'Sweep Start ',initial='0')

axEndPos = plt.axes([left+0.3,controlH+5*dist,0.1,height])
tEndPos = TextBox(axEndPos,'Sweep End ',initial='4')

axNsteps = plt.axes([left+0.6,controlH+5*dist,0.1,height])
tNsteps = TextBox(axNsteps,'Sweep Steps ',initial='100')


# Function to shoot the rays
def shootRays(rays,lenses,ax=ax,draw=True,VERBOSE=False,color='aqua'):
    # Shoot the rays
    print("Shootting Rays")
    for ray in tqdm(rays):
        ray.VERBOSE = VERBOSE
        ray.shootThroughLenses(lenses)
        if draw: ray.draw(ax,color=color)

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

# Draw the lenses on an ax
def drawLenses(lenses,ax):
    for lens in lenses:
        lens.draw(ax)

# Update the plots based on the given values
def update(val=-1):
    ax.cla()

    ax.grid()
    ax.set_ylim(*rayYlim)
    ax.set_xlim(*rayXlim)

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

# Only update the detector without affecting all the plot
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

# Create a new plot based on the sweep inputs
def sweep(val):
    update()
    detector.sweepPlot(rays,startPos=np.array([float(tStartPos.text),0]),\
        endPos=np.array([float(tEndPos.text),0]),Nsteps=int(tNsteps.text))
    plt.show()


# Add functions to the relevant objects
sNumber.on_changed(update)
sEnergy.on_changed(update)
sDetector.on_changed(moveDetector)

bShoot.on_clicked(update)
bSweep.on_clicked(sweep)

tDetectorWidth.on_submit(moveDetector)
tNoiseSTD.on_submit(update)
tNoiseAmplitude.on_submit(update)


# Show Everything
update()
moveDetector()
plt.show()