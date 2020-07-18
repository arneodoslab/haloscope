# Class to represent a Detector
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
from tqdm import tqdm
from ray import *
from lens import *

class Detector:
    
    def __init__ (self, position:np.array=np.array([1.0,0.0]), height:float = 1):
        self.position = position
        self.height = height
        self.mesh = self.generateLineMesh()
        self.hits = []
        self.count = 0

    def generateLineMesh(self):
        mesh = []
        mesh.append(self.position+np.array([0,self.height/2]))
        mesh.append(self.position+np.array([0,-self.height/2]))

        self.mesh = np.array(mesh)

        return self.mesh

    # Function that given an array of rays counts how many of the hit the detector
    def countHits(self,rays):
        count = 0
        hits = []
        avg = 0
        for ray in rays:
            for point in self.mesh:
                rX = ray.points.T[0]
                rY = ray.points.T[1]
                yest = np.interp(point[0],rX,rY)
                avg += abs(yest)
                if self.belongInMesh(np.array([point[0],yest])):
                    count+=1
                    hits.append([point[0],yest])
                    break
        
        self.count = count
        self.hits = np.array(hits)
        self.rate = count/len(rays)
        self.beamWidth = avg*2/len(rays)

        return self.count, self.rate, self.hits, self.beamWidth

    def belongInMesh(self,p):
        return p[1]<max(self.mesh.T[1]) and p[1]>min(self.mesh.T[1])

    def setPosition(self,position:np.array):
        self.position = position
        self.mesh = self.generateLineMesh()

    # This function creates and stores an array of data with the efficiency at each poiint of the detectector in a sweep
    def sweepPath(self,rays,startPos:np.array = np.array([0,0]),endPos:np.array=np.array([4,0]),Nsteps = 100, VERBOSE:bool=True):
        direction = (endPos-startPos)
        steps = np.linspace(0,1,Nsteps)

        rates = []
        widths = []
        if VERBOSE: 
            print("Sweeping from: [%.2f,%.2f]"%(startPos[0],startPos[1])," to: [%.2f,%.2f]"%(endPos[0],endPos[1]))
            steps = tqdm(steps)
        for step in steps:
            self.setPosition(startPos+step*direction)
            countResults = self.countHits(rays)
            rates.append([countResults[1],self.position])
            widths.append([countResults[3],self.position])
        
        self.rates = np.array(rates)
        self.widths = np.array(widths)

        return self.rates, self.widths


    def densityPlot(self,ax=None,Npts = 500, figsize = (7,7), dpi = 100, color = 'k', lw = 1, title="Detector Density Plot",bandwidth=0.5):
        if ax==None:
            fig = plt.figure(figsize=figsize,dpi=dpi)
            ax  = fig.add_subplot(111)

        ax.set_title(title)

        data = self.hits.T[1]
        # print(data)
        kde = scipy.stats.gaussian_kde(data,bw_method=bandwidth)
        x = np.linspace(min(self.mesh.T[1]),max(self.mesh.T[1]),Npts)
        y = kde(x)

        ax.plot(x,y,c=color,lw=lw,\
            label='Observed Detection Rate: %.2f\nReceived: %d\nSent: %d'%(self.rate,self.count,int(self.count/self.rate)))
        
        ax.set_xlabel('Detector Length [AU]')
        ax.set_ylabel('Gaussian Kernel Density Estimation Plot')
        ax.set_xlim(min(x),max(x))
        ax.set_ylim(0,max(y))
        ax.legend()
        ax.grid()

    def sweepPlot(self,rays,startPos:np.array = np.array([0,0]),endPos:np.array=np.array([4,0]),Nsteps = 100,\
        ax=None,Npts = 500, figsize = (7,7), dpi = 100, color = 'k', lw = 1, title="Detector Sweep Plot"):

        # Get the sweep parameters
        rates, widths = self.sweepPath(rays,startPos=startPos,endPos=endPos,Nsteps = Nsteps)

        # Split them up
        rate = rates.T[0]
        width = widths.T[0]
        points = rates.T[1]
        distances = np.array([mag(point-startPos) for point in points])

        # Plotting stuff
        if ax==None:
            fig = plt.figure('Detector Sweep from: [%.2f,%.2f] to: [%.2f,%.2f]'%(startPos[0],startPos[1],endPos[0],endPos[1]),figsize=figsize,dpi=dpi)
            ax  = fig.add_subplot(111)
        ax.set_title("Hits per distance from detector Convex Lens\nDetector Diameter: L = %.2f"%self.height)

        ax2 = ax.twinx()

        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        box = ax2.get_position()
        ax2.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])

        ax.plot(distances,rate,c='blue',ls='-',\
            label="Experimental Rate\nMax Rate: %.2f @ d = %.2f AU"%(max(rate),distances[rate.tolist().index(max(rate))]))

        color = 'tab:red'
        ax2.plot(distances,width,c=color,ls='-',\
            label="Experimental Beam Width\nMin Width: %.2f @ d = %.2f AU"%(min(width),distances[width.tolist().index(min(width))]))

        ax2.plot(distances,(1-rate)*width,color='k',ls=':',\
            label="Cost of lens arrangement \nMin Cost: %.2f @ d = %.2f AU"%(min((1-rate)*width),distances[((1-rate)*width).tolist().index(min((1-rate)*width))]))

        ax2.spines['right'].set_color(color)
        ax2.tick_params(axis='y', colors=color, labelcolor=color)
        ax2.set_ylabel('Beam Width on Detector',color=color)
        ax2.legend(loc='center left', bbox_to_anchor=(0.5, -0.2))

        color = 'blue'
        ax2.spines['left'].set_color(color)
        ax.tick_params(axis='y', colors=color, labelcolor=color)
        ax.set_xlabel("Displacement from starting point [AU]")
        ax.set_ylabel("Fraction of particles sent that hit the detector",color=color)
        ax.grid(which='minor', linestyle='-', linewidth='0.05', color='black')
        ax.minorticks_on()
        ax.grid(True)
        ax.legend(loc='center right', bbox_to_anchor=(0.5, -0.2))


    def draw(self,ax,color='k',lw=3):
        ax.plot(self.mesh.T[0],self.mesh.T[1],c=color,lw=lw)
