# This script is designed to create a lens and optimise it for a particulat width and maximum gain with a small detector
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt
from tqdm import tqdm
from lens import *
from ray import *
from detector import *

## INITIALISATION PARAMETERS ############################################################

# Simulation Parameters
Nrays = 1000
rayEnergy = 1.5
rayBandwidth = 5.08
RayEnergyRange = [0.2,5.9] # eV
RayGenerationRange = [-2.54,2.54]
RayGenerationXPos = -4

detectorPos = 0
detectorWidth = 0.05
Bandwidth = 0.1
startPos = np.array([2,0])
endPos = np.array([50,0])

noiseStd = 0.01
noiseAmplitude = 0

lensRightPoint = np.array([2.54,0])
lensLeftPoint = np.array([-2.54,0])
lensCommonPoint = np.array([0,2.54])
edgeThickness = 0.3

theta0 = [2.54,-2.54]
bounds = [(0.001,2.55),(-2.55,-0.001)]
Ncores = 16

VERBOSE = False

# Create lens 1
arc1 = Arc(pointX=lensRightPoint,pointY=lensCommonPoint)
arc2 = Arc(pointX=lensLeftPoint,pointY=lensCommonPoint)
lens1 = Lens(arc1,arc2, noiseStd=noiseStd, noiseAmplitude=noiseAmplitude)

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
def generateLens(lensRightPoint:float,lensLeftPoint:float,lensCommonPoint:np.array = lensCommonPoint,edgeThickness = edgeThickness):
    lensRightPoint = np.array([lensRightPoint,0])
    lensLeftPoint = np.array([lensLeftPoint,0])
    lensCommonPoint = lensCommonPoint

    arc1 = Arc(pointX=lensRightPoint,pointY=lensCommonPoint)
    arc2 = Arc(pointX=lensLeftPoint,pointY=lensCommonPoint)
    return Lens(arc1,arc2, noiseStd=noiseStd, noiseAmplitude=noiseAmplitude,thickness=edgeThickness)


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
    # solution = optimize.minimize(handler, theta0, method = 'L-BFGS-B', bounds=bounds)
    # solution = optimize.shgo(handler,bounds, n=200, iters=5, sampling_method='sobol')
    solution = optimize.differential_evolution(handler,bounds, updating='deferred',workers=Ncores)

    print(solution)
