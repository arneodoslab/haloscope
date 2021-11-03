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

# Simulation Parameters
Nrays = 500
rayEnergy = 1.5
rayBandwidth = 5.08
RayEnergyRange = [0.2,5.9] # eV
RayGenerationRange = [-2.54,2.54]
RayGenerationXPos = -4

detectorPos = 0
detectorWidth = 0.02
Bandwidth = 0.1
startPos = np.array([5,0])
endPos = np.array([10,0])

noise_std = 0.01
noise_amplitude = 0

X_1 = np.array([0,0.25,0.5])
Y_1 = np.array([0,0.25,0.5])
phi_1 = 1

X_2 = np.array([0,0.25,0.5])
Y_2 = np.array([0,0.25,0.5])
phi_2 = 2

thickness = 0.3

theta0 = [2.54,-2.54]
bounds = [(0.001,2.55),(-2.55,-0.001)]
Ncores = 4

VERBOSE = False

# Create lens 1
spline_1 = Spline(X_1,Y_1,phi_1,theta=-np.pi/2,scale=5.08,position=np.array([-thickness/2,0]))
spline_2 = Spline(X_2,Y_2,phi_2,theta=np.pi/2,scale=5.08,position=np.array([thickness/2,0]))
lens1 = Lens([spline_1,spline_2], noise_std=noise_std, noise_amplitude=noise_amplitude)

# Create lens list
lenses = [lens1]

# Create rays list
rays = []

# Create Detector
detector = Detector(position=np.array([detectorPos,0.]),height=detectorWidth)

    
## HELPING FUNCTIONS ####################################################################

# Create Rays
def createRays(Nrays=Nrays,RayGenerationXPos=RayGenerationXPos,RayGenerationRange=RayGenerationRange,RayEnergyRange=RayEnergyRange,rand=True):
    rays = []
    length = np.linspace(*RayGenerationRange,Nrays)
    for i in range(Nrays):
        if rand: ray = Ray(start=np.array([RayGenerationXPos,random(*RayGenerationRange)]),energy=random(*RayEnergyRange))
        else: ray = Ray(start=np.array([RayGenerationXPos,length[i]]),energy=random(*RayEnergyRange))
        rays.append(ray)

    return rays

# Function to shoot the rays
def shootRays(rays,lenses,VERBOSE=VERBOSE):
    # Shoot the rays
    for ray in rays:
        ray.VERBOSE = VERBOSE
        ray.shootThroughLenses(lenses)

# Function to create a lens and update it as planned
def generateLens(X_1:np.array = X_1,Y_1:np.array = Y_1,phi_1:float=phi_1,X_2:np.array = X_2,Y_2:np.array = Y_2,phi_2:float = phi_2):
    spline_1 = Spline(X_1,Y_1,phi_1,theta=-np.pi/2,scale=5.08,position=np.array([-thickness/2,0]))
    spline_2 = Spline(X_2,Y_2,phi_2,theta=np.pi/2,scale=5.08,position=np.array([thickness/2,0]))

    return Lens([spline_1,spline_2], noise_std=noise_std, noise_amplitude=noise_amplitude)


## OPTIMISATION SCRIPT #################################################################

# Optimisation parameters

def calculateLensScore(lenses,rays,detector:Detector):
    #Create a set of rays
    rays = createRays(Nrays=Nrays,RayEnergyRange=[rayEnergy]*2,rand=False)

    # Shoot the rays through the lenses
    shootRays(rays,lenses)
    
    # Sweep that predefined length with the detector
    rates, widths = detector.sweepPath(rays,VERBOSE=VERBOSE,startPos=startPos,endPos=endPos)
    rate = rates.T[0]
    width = widths.T[0]

    # Calculate the cost
    cost = (1-max(rate)) # *width[rate.tolist().index(max(rate))]

    return cost

# This functions acts as the minimisation function that takes a vector input theta, and distributes the parameters
def handler(theta):
    print("Theta: ",theta)
    # Create a detector
    detector = Detector(position=np.array([detectorPos,0.]),height=detectorWidth)

    # Create the new lenses
    lenses = [generateLens(*theta)]

    # Calculate the score by shooting rays through them, and return it
    score = calculateLensScore(lenses,rays,detector)
    return score




# Optimization command
if __name__=='__main__':
    solution = optimize.differential_evolution(handler,bounds, updating='deferred',workers=Ncores)

    print(solution)
