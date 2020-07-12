# Contains ray Clas
from lens import *

class Ray:

    def __init__(self, start:np.array = np.array([-2,1]), direction:np.array = np.array([1,0]), energy:float = 2.0, stoppingDistance:float = 6):
        self.points = np.array([start])
        self.direction = np.array([direction/mag(direction)])
        self.energy = energy
        self.stoppingDistance = stoppingDistance
        self.ncurrent = 1
        self.VERBOSE = False

    def shootThroughLens(self, lens, cnt = 0, cntThresh = 100, extendAtEnd = True):
        arcs = lens.getArcs()
        p = self.points[-1]
        d = self.direction[-1]
        if self.VERBOSE: print("Shootting Through Lens: ",cnt)
        travelDist, toArc = self.distToClosestArc(arcs,p,d)
        if self.VERBOSE: print("\tTravelDist = ",travelDist)
        if self.VERBOSE: print("\tPoints: ",self.points)

        if travelDist == float("inf"):
            if self.VERBOSE: print('\tFound Inf! Exiting')
            if extendAtEnd: travelDist = self.stoppingDistance
            else: travelDist = 0
            if self.VERBOSE: print("\tExtend?: ",extendAtEnd)
            if self.VERBOSE: print("\tFinal Dist = ",travelDist)

            self.points = np.append(self.points, [p+d*travelDist], axis=0)
            if self.VERBOSE: print("Final Points: ",self.points)
            if self.VERBOSE: print("Final Direcs: ",self.direction)
            return

        if cnt > cntThresh:
            return

        # Move the ray
        self.points = np.append(self.points,[p+d*travelDist],axis=0)
        if self.VERBOSE: print("\tNew Point: ",p+d*travelDist)

        self.refract(lens, d,toArc)

        if self.VERBOSE: print()
        self.shootThroughLens(lens,cnt=cnt+1,extendAtEnd=extendAtEnd)
        
        return

    def refract(self, lens, d, toArc):
        # Refract Properly
        n1 = self.ncurrent
        n2 = self.renewRefractiveIndex(lens)
        R = self.points[-1] - toArc.C
        
        theta1 = (np.arccos(abs(d.dot(toArc.C-self.points[-1]))/mag(self.points[-1]-toArc.C)))
        if (n2<n1) and theta1 > np.arcsin(n2/n1): # Account for total internal reflection
            self.direction = np.append(self.direction,[d-2*d.dot(R)/mag(R)**2*R],axis=0)
            theta = 0
            theta2 = 0

        else:
            t = (np.array([R[1],-R[0]]))
            theta2 = (np.arcsin(n1/n2*np.sin(theta1)))
            noise = np.random.normal(0,lens.noiseStd)*lens.noiseAmplitude
            theta = arg(d) - (theta1 - theta2)*np.sign(d[0]*t[1]-d[1]*t[0])*np.sign(d.dot(t)) + noise
            if self.VERBOSE: print("\tCross: ",d[0]*t[1]-d[1]*t[0])
            if self.VERBOSE: print("\tDot  : ",d.dot(t))
            self.direction = np.append(self.direction,[np.array([np.cos(theta),np.sin(theta)])],axis=0)

        if self.VERBOSE: print("\tTheta1: ",theta1*180/np.pi,"\tTheta2: ",theta2*180/np.pi)
        if self.VERBOSE: print("\tTheta : ",theta*180/np.pi)
        if self.VERBOSE: print("\tArcCenter: ",toArc.C)
        if self.VERBOSE: print("n1: ",n1, "\tn2: ", n2)
    
    def distToClosestArc(self,arcs,p,d):
        dists = [float("inf")]
        selectedArcs  = [None]
        for arc in arcs:
            r = (p-arc.C)
            a = -2*(d.dot(r))
            b = mag(r)**2-arc.R**2

            s = []
            if a**2-4*b > 0:
                s.append(0.5*(a+(a**2-4*b)**0.5))
                s.append(0.5*(a-(a**2-4*b)**0.5))
            if self.VERBOSE: print("\t\t\tm:",arc.phi*180/np.pi," M:",(arc.phi+arc.theta)*180/np.pi, " C:",arc.C)
            if self.VERBOSE: print("\t\tDistCandidates: ", s)
            if self.VERBOSE: print("\t\tArgsCandidates: ", [arg(r+S*d)*180/np.pi for S in s])
            if self.VERBOSE: print("\t\tPosiCandidates: ", [(p+S*d) for S in s])

            for S in s:
                if S>1e-10: # If You don't have to spontaneously turn back
                    if isInRange(arg(r+S*d),arc.phi,arc.phi+arc.theta):
                    # if arg(r+S*d)>=arc.phi and arg(r+S*d)<=arc.phi+arc.theta: # If you hit within the arc
                        dists.append(S)
                        selectedArcs.append(arc)
        
        if self.VERBOSE: print("\t\tAllDists: ", dists)

        return min(dists), selectedArcs[dists.index(min(dists))]
    
    def shootThroughLenses(self,lenses):
        for lens in lenses:
            self.shootThroughLens(lens, extendAtEnd=False)
        self.shootThroughLens(lenses[-1])

    def renewRefractiveIndex(self,lens):
        if self.ncurrent != 1: self.ncurrent = 1
        else: self.ncurrent = lens.getRefractiveIndex(self.energy)
        return self.ncurrent

    def draw(self, ax, color = 'lime', lw = 0.5):
        return ax.plot(self.points.T[0],self.points.T[1],c=color,lw=lw)
