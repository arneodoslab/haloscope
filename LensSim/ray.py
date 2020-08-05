# Contains ray Clas
from lens import *

class Ray:

    def __init__(self, start:np.array = np.array([-2,1]), direction:np.array = np.array([1,0]), energy:float = 2.0, stoppingDistance:float = 100):
        self.points = np.array([start])
        self.direction = np.array([direction/mag(direction)])
        self.energy = energy
        self.stoppingDistance = stoppingDistance
        self.ncurrent = 1
        self.VERBOSE = False

    def shootThroughLens(self, lens, cnt = 0, cntThresh = 100, extendAtEnd = True):
        p = self.points[-1]
        d = self.direction[-1]
        
        # Get the interseciton with the closest arc
        if self.VERBOSE: print("Shootting Through Lens: ",cnt)
        intersect, param, arc = self.distToClosestArc(lens.curves,p,d)

        if param == float("inf"):
            if self.VERBOSE: print('\tFound Inf! Exiting')
            if extendAtEnd: travelDist = self.stoppingDistance
            else: travelDist = 0
            if self.VERBOSE: print("\tExtend?: ",extendAtEnd)
            if self.VERBOSE: print("\tFinal Dist = ",travelDist)

            self.points = np.append(self.points, [p+d*travelDist], axis=0)
            if self.VERBOSE: print("Final Points: ",self.points)
            if self.VERBOSE: print("Final Direcs: ",self.direction)
            return

        if self.VERBOSE: print("\tTravelDist = ",mag(p-intersect))
        if self.VERBOSE: print("\tPoints: ",self.points)

        if cnt > cntThresh:
            return

        travelDist = mag(intersect-p)

        # Move the ray
        self.points = np.append(self.points,[p+d*travelDist],axis=0)
        if self.VERBOSE: print("\tNew Point: ",p+d*travelDist)

        self.refract(lens, d, param, arc)

        if self.VERBOSE: print()
        self.shootThroughLens(lens,cnt=cnt+1,extendAtEnd=extendAtEnd)
        
        return

    # Returns rotation matrix for a particular angle
    def R(self,theta):
        R = np.zeros([2,2])
        R[0][0] = np.cos(theta)
        R[0][1] = np.sin(theta)
        R[1][0] = -np.sin(theta)
        R[1][1] = np.cos(theta)

        return R

    # This function changes the direction of refraction based on the new thingy
    def refract(self, lens, k, param, arc):
        # Refract Properly
        n1 = self.ncurrent
        n2 = self.renewRefractiveIndex(lens)

        N = arc.Nhat(param)
        theta = np.arccos(abs(k.dot(N)))
        if n1>=n2: thetaCritical = np.arcsin(n2/n1)
        else: thetaCritical = float('inf')

        noise = np.random.normal(0,lens.noiseStd)*lens.noiseAmplitude

        if theta < thetaCritical:
            thetaprime = np.arcsin(n1/n2*np.sin(theta))*np.sign(N[0]*k[1]-N[1]*k[0])*np.sign(N.dot(k))
            kprime = np.matmul(self.R(thetaprime + noise),N*np.sign(k.dot(N)))
        else:
            kprime = - np.matmul(self.R(theta + noise),N*np.sign(k.dot(N)))

        self.direction = np.append(self.direction,[kprime],axis=0)


        # R = self.points[-1] - toArc.C
        
        # theta1 = (np.arccos(abs(d.dot(toArc.C-self.points[-1]))/mag(self.points[-1]-toArc.C)))
        # if (n2<n1) and theta1 > np.arcsin(n2/n1): # Account for total internal reflection
        #     self.direction = np.append(self.direction,[d-2*d.dot(R)/mag(R)**2*R],axis=0)
        #     theta = 0
        #     theta2 = 0

        # else:
        #     t = (np.array([R[1],-R[0]]))
        #     theta2 = (np.arcsin(n1/n2*np.sin(theta1)))
        #     noise = np.random.normal(0,lens.noiseStd)*lens.noiseAmplitude
        #     theta = arg(d) - (theta1 - theta2)*np.sign(d[0]*t[1]-d[1]*t[0])*np.sign(d.dot(t)) + noise
        #     if self.VERBOSE: print("\tCross: ",d[0]*t[1]-d[1]*t[0])
        #     if self.VERBOSE: print("\tDot  : ",d.dot(t))
        #     self.direction = np.append(self.direction,[np.array([np.cos(theta),np.sin(theta)])],axis=0)

        # if self.VERBOSE: print("\tTheta1: ",theta1*180/np.pi,"\tTheta2: ",theta2*180/np.pi)
        # if self.VERBOSE: print("\tTheta : ",theta*180/np.pi)
        # if self.VERBOSE: print("\tArcCenter: ",toArc.C)
        # if self.VERBOSE: print("n1: ",n1, "\tn2: ", n2)
    
    # Finds the distance to the closest arc, and returns the arc, and the point of intersection in said arc
    def distToClosestArc(self,arcs,p,d,threshold = 1e-4):
        params = []
        m = float('inf')
        mini = 0
        for i in range(len(arcs)):
            params.append(arcs[i].getIntersection(p,d))
            if params[-1][1] == float('inf'): continue
            if mag(p - params[-1][0]) < m and mag(p - params[-1][0])>threshold:
                m = mag(p - params[-1][0])
                mini = i

        if m == float('inf'): return p, float('inf'), arcs[0]
        return params[mini][0], params[mini][1], arcs[mini]

        
        # dists = [float("inf")]
        # selectedArcs  = [None]
        # for arc in arcs:
        #     r = (p-arc.C)
        #     a = -2*(d.dot(r))
        #     b = mag(r)**2-arc.R**2

        #     s = []
        #     if a**2-4*b > 0:
        #         s.append(0.5*(a+(a**2-4*b)**0.5))
        #         s.append(0.5*(a-(a**2-4*b)**0.5))
        #     if self.VERBOSE: print("\t\t\tm:",arc.phi*180/np.pi," M:",(arc.phi+arc.theta)*180/np.pi, " C:",arc.C)
        #     if self.VERBOSE: print("\t\tDistCandidates: ", s)
        #     if self.VERBOSE: print("\t\tArgsCandidates: ", [arg(r+S*d)*180/np.pi for S in s])
        #     if self.VERBOSE: print("\t\tPosiCandidates: ", [(p+S*d) for S in s])

        #     for S in s:
        #         if S>1e-10: # If You don't have to spontaneously turn back
        #             if isInRange(arg(r+S*d),arc.phi,arc.phi+arc.theta):
        #             # if arg(r+S*d)>=arc.phi and arg(r+S*d)<=arc.phi+arc.theta: # If you hit within the arc
        #                 dists.append(S)
        #                 selectedArcs.append(arc)
        
        # if self.VERBOSE: print("\t\tAllDists: ", dists)

        # return min(dists), selectedArcs[dists.index(min(dists))]
    
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
