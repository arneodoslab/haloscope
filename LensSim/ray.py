# Contains ray Clas
from lens import *

class Ray:
    # Constructor
    def __init__(self, start:np.array = np.array([-2,1]), direction:np.array = np.array([1,0]), energy:float = 2.0, stopping_distance:float = 100):
        self.points = np.array([start])
        self.direction = np.array([direction/mag(direction)])
        self.energy = energy
        self.stopping_distance = stopping_distance
        self.n_current = 1
        self.VERBOSE = False

    # This is in charge of shooting the ray through a lens and calculating its path
    def shoot_through_lens(self,lens:Lens, cnt:int = 0, cnt_max:int = 100, extend_at_end:bool = True, VERBOSE:bool = False):
        p = self.points[-1]     # Get the current position of the ray
        k = self.direction[-1]  # Get the current direction fo the ray

        if VERBOSE: print("Shootting Through Lens: ",cnt)
        # Find the closes intersection
        l, t, curve = self.get_closest_intersection(lens,p,k)

        # Identify if you've passed the end of the lens
        if t < 0:
            travel_distance = self.stopping_distance if extend_at_end else 0
            self.points = np.append(self.points, [p + k*travel_distance], axis=0) # Add an extra point further away
            return
        
        # if it has bounced off a shit ton of times exit
        if cnt >= cnt_max:
            return
        
        # Move the ray to the new point
        self.points = np.append(self.points,[p + k*l],axis=0)

        # Refract the ray
        self.refract(lens,curve,k,t)

        # Recursively continue until the end
        self.shoot_through_lens(lens,cnt=cnt+1,extendAtEnd=extendAtEnd,VERBOSE=VERBOSE)

        return 


    # loops through all the curves and finds the closes one in the path, as well as its intersection point
    def get_closest_intersection(self,lens,p,k):
        # Initialise return varibales
        l_min = float('inf')
        t_min = -1
        curve_min = lens.curves[0]

        # for all curves
        for curve in lens.curves:
            l,t = curve.get_intersection(p,k) # Get the distance to curve l and intersection point parameter t

            # Update the minima if this is the case
            if l < l_min and not t < 0: 
                l_min = l
                t_min = t
                curve_min = curve

        return l_min, t_min, curve_min


    # Returns rotation matrix for a particular angle
    def R(self,theta):
        R = np.zeros([2,2])
        R[0][0] = np.cos(theta)
        R[0][1] = np.sin(theta)
        R[1][0] = -np.sin(theta)
        R[1][1] = np.cos(theta)

        return R

    # This function changes the direction of refraction based on the new thingy
    def refract(self, lens:Lens, curve, k, t):
        # Refract Properly
        n1 = self.n_current
        n2 = self.renewRefractiveIndex(lens)

        N = curve.n_hat(t)                              # Get normal vector on the curve
        theta = np.arccos(abs(k.dot(N)))                # Get minimum angle between the direction and normal

        theta_critical = np.arcsin(n2/n1) if n1>=n2 else float('inf') # Define a pseudocritical angle

        # Create noise as predefined by the lens
        noise = np.random.normal(0,lens.noiseStd)*lens.noiseAmplitude

        # Check for total internal reflection
        if theta < theta_critical:
            theta_prime = np.arcsin(n1/n2*np.sin(theta))*np.sign(N[0]*k[1]-N[1]*k[0])*np.sign(N.dot(k))
            kprime = np.matmul(self.R(theta_prime + noise),N*np.sign(k.dot(N)))
        else:
            kprime = - np.matmul(self.R(theta + noise),N*np.sign(k.dot(N)))

        # Append with the new direction
        self.direction = np.append(self.direction,[kprime],axis=0)

    
    def shootThroughLenses(self,lenses):
        for lens in lenses:
            self.shootThroughLens(lens, extendAtEnd=False)
        self.shootThroughLens(lenses[-1])

    def renewRefractiveIndex(self,lens):
        if self.n_current != 1: self.n_current = 1
        else: self.n_current = lens.getRefractiveIndex(self.energy)
        return self.n_current

    def draw(self, ax, color = 'lime', lw = 0.5):
        return ax.plot(self.points.T[0],self.points.T[1],c=color,lw=lw)
