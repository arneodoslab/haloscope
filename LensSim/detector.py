# Class to represent a Detector
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors.kde import KernelDensity
from ray import *
from lens import *

class Detector:
    
    def __init__ (self, position:np.array=np.array([1,0]), height:float = 1):
        self.position = position
        self.height = height
        self.mesh = self.generateLineMesh()
        self.hits = []
        self.count = 0

    def generateLineMesh(self):
        mesh = []
        mesh.append(self.position+np.array([0,self.height/2]))
        mesh.append(self.position+np.array([0,-self.height/2]))

        return np.array(mesh)

    # Function that given an array of rays counts how many of the hit the detector
    def countHits(self,rays):
        count = 0
        hits = []
        for ray in rays:
            for point in self.mesh:
                rX = ray.points.T[0]
                rY = ray.points.T[1]
                yest = np.interp(point[0],rX,rY)
                if self.belongInMesh(np.array([point[0],yest])):
                    count+=1
                    hits.append([point[0],yest])
                    break
        
        self.count = count
        self.hits = np.array(hits)
        self.rate = count/len(rays)

        return count, self.rate, self.hits

    def belongInMesh(self,p):
        return p[1]<max(self.mesh.T[1]) and p[1]>min(self.mesh.T[1])

    def densityPlot(self,ax=None,Npts = 100, figsize = (7,7), dpi = 100, color = 'k', lw = 1, title="Detector Density Plot",bandwidth=0.5):
        if ax==None:
            fig = plt.figure(figsize=figsize,dpi=dpi)
            ax  = fig.add_subplot(111)

        ax.set_title(title)

        data = self.hits.T[1].reshape(-1,1)
        kde = KernelDensity(kernel='gaussian', bandwidth=bandwidth).fit(data)
        x = np.linspace(min(self.mesh.T[1]),max(self.mesh.T[1]),Npts)

        ax.plot(x,kde.score_samples(x.reshape(-1,1)),c=color,lw=lw,\
            label='Observed Detection Rate: %.2f\nReceived: %d\nSent: %d'%(self.rate,self.count,int(self.count/self.rate)))
        
        ax.set_xlabel('Detector Length [AU]')
        ax.set_ylabel('Gaussian Kernel Density Estimation Plot')
        ax.legend()
        ax.grid()

    def draw(self,ax,color='k',lw=3):
        ax.plot(self.mesh.T[0],self.mesh.T[1],c=color,lw=lw)
