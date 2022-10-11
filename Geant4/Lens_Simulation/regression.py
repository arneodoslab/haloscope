# This script is designed to create a lens and optimise it for a particulat width and maximum gain with a small detector
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt
from tqdm import tqdm
from lens import *
from ray import *
from detector import *
from curves import *

## INITIALISATION PARAMETERS ############################################################

# Lens Parameters
noise_std = 0.01
noise_amplitude = 0
lens_thickness = 0.3
lens_diameter = 5.08

# Ray Parameters
N_rays = 700
ray_energy = 1.53
ray_generation_range = [-lens_diameter/2,lens_diameter/2]
ray_generation_xpos = -4

# Detector Parameters
detector_width = 0.025
detector_bandwidth = 0.1
detector_start_pos = np.array([5,0])
detector_end_pos   = np.array([10,0])

# Curve Parameters
X_1 = np.array([0,0.25,0.5])
Y_1 = np.array([0,0.25,0.5])
phi_1 = 1

X_2 = np.array([0,0.25,0.5])
Y_2 = np.array([0,0.25,0.5])
phi_2 = 2

# Simulation Parameters
N_cores = 16
bounds = [(0.1,0.45),(0.0/lens_diameter,1.5/lens_diameter),(0.0/lens_diameter,2/lens_diameter),(0.0,2),\
	  (0.1,0.45),(0.0/lens_diameter,1.5/lens_diameter),(0.0/lens_diameter,2/lens_diameter),(0.0,2)]
VERBOSE = False

## HELPING FUNCTIONS ####################################################################

# Create a lens
def create_lens(theta):
    X_1 = np.array([0,theta[0],0.5])
    Y_1 = np.array([0,theta[1],theta[2]])
    phi_1 = theta[3]

    X_2 = np.array([0,theta[4],0.5])
    Y_2 = np.array([0,theta[5],theta[6]])
    phi_2 = theta[7]

    spline_1 = Spline(X_1,Y_1,phi_1,theta=-np.pi/2,scale=lens_diameter,position=np.array([lens_thickness/2,lens_diameter/2]))
    spline_2 = Spline(X_2,Y_2,phi_2,theta=np.pi/2,scale=lens_diameter,position=np.array([-lens_thickness/2,-lens_diameter/2]))
    lens_1 = Lens([spline_1,spline_2],noise_std=noise_std,noise_amplitude=noise_amplitude)

    return lens_1

# Create Rays
def create_rays(N_rays=N_rays, ray_generation_xpos=ray_generation_xpos, ray_generation_range=ray_generation_range, ray_energy=ray_energy):
    rays = []
    length = np.linspace(*ray_generation_range,N_rays)
    for i in range(N_rays):
        rays.append(Ray(start=np.array([ray_generation_xpos,length[i]]),energy=ray_energy))

    return rays

# Shoot Rays
def shoot_rays(rays,lenses,VERBOSE=VERBOSE):
    for ray in rays:
        ray.VERBOSE = VERBOSE
        ray.shoot_through_lenses(lenses)
    
# Calculates the score of a lens 
def calculate_lens_score(lenses,detector):
    # Create a set of rays
    rays = create_rays()

    # Shoot rays through the lenses
    shoot_rays(rays,lenses)

    # Sweep the detector
    rates, widths = detector.sweep_path(rays,VERBOSE=VERBOSE,startPos=detector_start_pos,endPos=detector_end_pos)
    rate = rates.T[0]
    width = widths.T[0]

    # Calculate cost
    cost = (1-max(rate))

    return cost

# Handler function
def handler(theta):
    if VERBOSE: print("Theta: ",theta)

    # Create a detector
    detector = Detector(position=detector_start_pos,height=detector_width)

    # Create a new lenses playlist thingy
    lenses = [create_lens(theta)]

    # Calculate the score
    score = calculate_lens_score(lenses,detector)
    print(score)
    return score


## SIMULATION PRIMITIVES ################################################################


# Create lens 1
spline_1 = Spline(X_1,Y_1,phi_1,theta=-np.pi/2,scale=lens_diameter,position=np.array([-lens_thickness,0]))
spline_2 = Spline(X_2,Y_2,phi_2,theta=np.pi/2,scale=lens_diameter,position=np.array([lens_thickness,0]))
lens_1 = Lens([spline_1,spline_2],noise_std=noise_std,noise_amplitude=noise_amplitude)

# Create lens list
lenses = [lens_1]


## OPTIMISATION SCRIPT ##################################################################

if __name__=='__main__':
    solution = optimize.differential_evolution(handler, bounds, updating='deferred', workers=N_cores)
    print(solution)
    file = open('results.txt','a+')
    file.write(str(solution)+'\n\n')
