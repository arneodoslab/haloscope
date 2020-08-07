import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox
import scipy.constants as c
import pandas as pd
from tqdm import tqdm
from lens import *
from ray import *
from detector import *
from curves import *


# Simulation Parameters
Nrays = 100
ray_energy = 1.5
rayBandwidth = 5.08
ray_energy_range = [0.2,5.9] # eV
ray_generation_range = [-2.54,2.54]
ray_generation_x_pos = -4

detector_pos = 2
detector_width = 0.05
Bandwidth = 0.1

noise_std = 0.01
noise_amplitude = 0

lens_right_point = np.array([0.001,0])
lens_left_point = np.array([-2,0]) #Thickness 0

# lens_right_point = np.array([0.4316416,0])  #From 2 to 20
# lens_left_point = np.array([-0.66065332,0]) #Thickness 0

# lens_right_point = np.array([0.1578881,0])  #From 2 to 20
# lens_left_point = np.array([-0.43856842,0]) #Thickness 0

# lens_right_point = np.array([0.24315284,0]) #From 2 to 50
# lens_left_point = np.array([-0.09266229,0]) #Thickness 0.18

# lens_right_point = np.array([0.02806994,0]) #From 2 to 50
# lens_left_point = np.array([-0.29361477,0]) #Thickness 0.18

# lens_right_point = np.array([0.12054916,0]) #From 2 to 50
# lens_left_point = np.array([-0.12780141,0]) #Thickness 0.3

# lens_right_point = np.array([0.0707879,0])  #From 2 to 50
# lens_left_point = np.array([-0.13389945,0]) #Thickness 0.3

# lens_right_point = np.array([0.09579702,0]) #From 10 ro 20
# lens_left_point = np.array([-0.22188508,0]) #Thickness 0.3

lens_right_point = np.array([0.07842648,0]) #From 5 to 10
lens_left_point = np.array([-0.54216092,0]) #Thickness 0.3 
lens_common_point = np.array([0,2.54])
edge_thickness = 0.3

ray_x_lim = [-4,15]
ray_y_lim = [-4,4]


VERBOSE = False


# Create lens 1
arc1 = Arc(point_1=np.array([0,2.54]),point_2=np.array([1,0]),point_3=np.array([0,-2.54]))
spline1 = Spline([0,0.25,0.5],[0,0.3,0.5],scale=5.08,position=np.array([1,-2.54]))
lens = Lens([arc1,spline1], noise_std=noise_std, noise_amplitude=noise_amplitude, thickness=edge_thickness)
# print("RADIUS 1: ",lens.arc1.R,"\nRADIUS 2: ",lens.arc2.R,"\nMAX THICKNESS: ",lens.arc1.R+lens.arc2.R+lens.thickness)

# # Create lens 2
# arc3 = Arc(pointX=np.array([2,0]),pointY=np.array([1,1]))
# arc4 = Arc(C=np.array([2,0]),R=1.5,dirPositive=False)
# lens2 = Lens(arc3,arc4, noise_std=noise_std, noise_amplitude=noise_amplitude)

lenses = [lens]

# Create rays list
rays = []

# Create Detector
detector = Detector(position=np.array([detector_pos,0.]),height=detector_width)

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
spawn = np.arange(*ray_generation_range,0.1)

axBandwidth = plt.axes([left,controlH,0.5,height])
sBandwidth = Slider(axBandwidth, 'Light Bandwidth', 0.01,10, valinit=rayBandwidth, valstep=0.01, color=color)

axNumber = plt.axes([left, controlH+dist, 0.5, height])
sNumber = Slider(axNumber, 'Number of Rays', 1, 1000, valinit=Nrays, valstep=1, color=color)

axEnergy = plt.axes([left, controlH+2*dist, 0.5, height])
sEnergy = Slider(axEnergy, 'Energy of Rays', *ray_energy_range, valinit=ray_energy, valstep=0.01, color=color)

axDetector = plt.axes([left,controlH+3*dist,0.5,height])
sDetector = Slider(axDetector, 'Detector Pos', *ray_x_lim, valinit=detector_pos, valstep=0.01, color=color)

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
tDetectorWidth = TextBox(axDetectorWidth,'Detector Width ',initial=str(detector_width))

axNoiseStd = plt.axes([left+0.3,controlH+4*dist,0.1,height])
tnoise_std = TextBox(axNoiseStd,'Noise STD ',initial='0.01')

axNoiseAmplitude = plt.axes([left+0.6,controlH+4*dist,0.1,height])
tnoise_amplitude = TextBox(axNoiseAmplitude,'Noise Amplitude ',initial='0')

axStartPos = plt.axes([left,controlH+5*dist,0.1,height])
tStartPos = TextBox(axStartPos,'Sweep Start ',initial='0')

axEndPos = plt.axes([left+0.3,controlH+5*dist,0.1,height])
tEndPos = TextBox(axEndPos,'Sweep End ',initial='4')

axNsteps = plt.axes([left+0.6,controlH+5*dist,0.1,height])
tNsteps = TextBox(axNsteps,'Sweep Steps ',initial='100')


# Function to shoot the rays
def shoot_rays(rays,lenses,ax=ax,draw=True,VERBOSE=False,color='aqua'):
    # Shoot the rays
    print("Shootting Rays")
    for ray in tqdm(rays):
        ray.VERBOSE = VERBOSE
        ray.shoot_through_lenses(lenses)
        if draw: ray.draw(ax,color=color)

# Create Rays
def createRays(Nrays=Nrays,ray_generation_x_pos=ray_generation_x_pos,ray_generation_range=ray_generation_range,ray_energy_range=ray_energy_range,rand=True):
    rays = []
    print("Creating Rays")

    length = np.linspace(*ray_generation_range,Nrays)
    for i in tqdm(range(Nrays)):
        if rand: ray = Ray(start=np.array([ray_generation_x_pos,random(*ray_generation_range)]),energy=random(*ray_energy_range))
        else: ray = Ray(start=np.array([ray_generation_x_pos,length[i]]),energy=random(*ray_energy_range))
        rays.append(ray)

    return rays

# Draw the lenses on an ax
def draw_lenses(lenses,ax):
    for lens in lenses:
        lens.draw(ax)

# Update the plots based on the given values
def update(val=-1):
    ax.cla()

    ax.grid()
    ax.set_ylim(*ray_y_lim)
    ax.set_xlim(*ray_x_lim)

    # Update lenses
    for lens in lenses:
        lens.noise_std = float(tnoise_std.text)
        lens.noise_amplitude = float(tnoise_amplitude.text)

    # Create and shoot new rays
    global rays
    rays = createRays(Nrays=int(sNumber.val),ray_energy_range=[sEnergy.val]*2,rand=radio.value_selected=='random',\
        ray_generation_range=[-sBandwidth.val/2,sBandwidth.val/2])
    shoot_rays(rays,lenses,VERBOSE=VERBOSE)

    # Plot lenses
    draw_lenses(lenses,ax)

    # Update and Plot detector
    detector.position[0] = sDetector.val
    detector.generate_line_mesh()
    detector.draw(ax)

    # Count hits and plot density
    detectorAx.cla()
    detector.count_hits(rays)
    detector.density_plot(ax=detectorAx, bandwidth=Bandwidth)
    fig.canvas.draw_idle()

# Only update the detector without affecting all the plot
def move_detector(val = -1):
    # Update and plot Detector
    ax.get_lines()[-1].remove()
    detector.position[0] = sDetector.val
    detector.height = float(tDetectorWidth.text)
    detector.generate_line_mesh()
    detector.draw(ax)

    # Count hits and plot density
    detectorAx.cla()
    detector.count_hits(rays)
    detector.density_plot(ax=detectorAx, bandwidth=Bandwidth)
    fig.canvas.draw_idle()

# Create a new plot based on the sweep inputs
def sweep(val):
    update()
    detector.sweep_plot(rays,startPos=np.array([float(tStartPos.text),0]),\
        endPos=np.array([float(tEndPos.text),0]),Nsteps=int(tNsteps.text))
    plt.show()


# Add functions to the relevant objects
sNumber.on_changed(update)
sEnergy.on_changed(update)
sDetector.on_changed(move_detector)

bShoot.on_clicked(update)
bSweep.on_clicked(sweep)

tDetectorWidth.on_submit(move_detector)
tnoise_std.on_submit(update)
tnoise_amplitude.on_submit(update)


# Show Everything
update()
move_detector()
plt.show()