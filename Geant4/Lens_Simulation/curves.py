# Contains class for lens
import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as c
import pandas as pd
import scipy.linalg as la
from scipy.optimize import fsolve
from collections.abc import Iterable

# Return the magnitude of a vector a
def mag(a:np.array):
    return a.dot(a)**0.5

# Returns the unit vector from a
def hat(a:np.array):
    return a/mag(a)

# Return the argument of curve from 0 to  2π
def arg(a:np.array):
    return np.arccos(hat(a)[0]) if hat(a)[1] >= 0 else (np.pi + np.arccos(hat(a)[0]))

# Returns the angle between two position angles
def delta_theta(theta_1,theta_2):
    theta = theta_1 - theta_2
    return theta if theta >= 0 else 2*np.pi - theta

# Return a random float between m and M
def random(m:float,M:float):
    return np.random.rand()*(M-m) + m

# Return the cross product with k_hat of a 2D vector a
def cross_k(a):
    return np.array([-a[1],a[0]])

# returns the inverse of a 2x2 matrix M
def inverse(M:np.array):
    M_inverse = np.zeros(M.shape)
    M_inverse[0][0] = M[1][1]
    M_inverse[1][1] = M[0][0]
    M_inverse[1][0] = - M[1][0]
    M_inverse[0][1] = - M[0][1]

    M_inverse/= M[0][0]*M[1][1]-M[1][0]*M[0][1]

    return M_inverse

# Return swapped variables a & b
def swap(a):
    temp = a[0]
    a[0] = a[1]
    a[1] = temp

# This function returns the solutions of a cubic polynomial, both real and imaginary
def solve_cubic(e:Iterable):
    # Get the discriminant constants
    D = np.array([0.,0.])
    D[0] = e[2]**2-3*e[3]*e[1]
    D[1] = 2*e[2]**3 - 9*e[3]*e[2]*e[1] + 27*e[1]**2*e[0]

    if VERBOSE: print("\tD: ",D)
    if VERBOSE: print("\te: ",e)
    if VERBOSE: print("\tC+: ",(0.5*(D[1]+(D[1]**2-4*D[0]**3+0j)**0.5)+0j)**(1/3))
    if VERBOSE: print("\tC-: ",(0.5*(D[1]-(D[1]**2-4*D[0]**3+0j)**0.5)+0j)**(1/3))
    C = (0.5*(D[1]-(D[1]**2-4*D[0]**3+0j)**0.5)+0j)**(1/3) if abs((0.5*(D[1]+(D[1]**2-4*D[0]**3+0j)**0.5)+0j)**(1/3)) < 1e-8 else (0.5*(D[1]+(D[1]**2-4*D[0]**3+0j)**0.5)+0j)**(1/3)
    ksi = (-1+3**(1/3)*1j)/2
    if VERBOSE: print("\tksi: ",ksi)
    if VERBOSE: print("\tC: ",C)

    # Finally calculate the solutions
    solns = np.array([-1/(3*e[3])*(e[2]+C*ksi**k+D[0]/(C*ksi**k)) for k in (0,1,2)])

    return solns

# Returns the solution of a linear equation
def solve_linear(e):
    return np.array([-e[0]/e[1]])


class Arc:
    def __init__(self,point_1:np.array,point_2:np.array,point_3:np.array,position:np.array = np.array([0,0])):
        
        # Calculate the center and radius based on the points
        self.C, self.R = self.calculate_center_radius(point_1,point_2,point_3)
        
        # Calculate the start and end angles
        self.theta_1 = arg(point_1 - self.C)
        self.theta_2 = arg(point_3 - self.C)
        self.rate    = delta_theta(self.theta_1,self.theta_2)*np.sign(cross_k(point_1-point_2).dot(point_2-self.C))


    # Returns the center and radius of the circle described by the three points
    def calculate_center_radius(self,point_1,point_2,point_3):
        # Find the center and radius of the arc, and decide its direction
        direction_1 = hat(cross_k(point_2-point_1))
        direction_2 = hat(cross_k(point_3-point_2))
        M = np.append(direction_1,direction_2).reshape((2,2)).T
        M_inverse = inverse(M)

        translation = np.matmul(M_inverse,0.5*(-point_1+point_3))[0] # Get translation constant

        # Calculate center and radius
        C = direction_1*translation + 0.5*(point_1+point_2)
        R = mag(point_1-C)

        # breakpoint()
        return C,R

    # returns the parameter form the angle
    def t(self,theta):
        return delta_theta(self.theta_1,theta)/self.rate

    # Returns the tangent vector to the arc at t
    def t_hat(self,t):
        if isinstance(t,Iterable): return np.array([self.t_hat(i) for i in t]) # Return array of positions if you ask for it
        
        return np.array([-np.sin(self.theta_1 + self.rate*t),np.cos(self.theta_1 + self.rate*t)])
    
    # returns the normal vector to the arc at t
    def n_hat(self,t):
        if isinstance(t,Iterable): return np.array([self.n_hat(i) for i in t]) # Return array of positions if you ask for it
        
        return - np.array([np.cos(self.theta_1 + self.rate*t),np.sin(self.theta_1 + self.rate*t)])
    
    # Returns a vector to a point at an angle t of the curve
    def r(self,t):
        if isinstance(t,Iterable): return np.array([self.r(i) for i in t])
        
        return self.C + self.R*np.array([np.cos(self.theta_1 + self.rate*t),np.sin(self.theta_1 + self.rate*t)])

    # Finds all the intersection points and retuns the shortest one
    def get_intersection(self,p:np.array, k:np.array, VERBOSE:bool = False):
        # First calculate the minimum distance d between the center of the arc and the ray
        d = mag(self.C-p-(self.C-p).dot(k)*k)

        if VERBOSE: print('d: ',d)

        # Initialise return variables
        l_min = float('inf')
        t_min = -1

        # Then check if the ray intersects with circle
        if d < self.R: # In this case there are two solutions:
            a = (mag(self.C-p)**2-d**2)**0.5
            b = (self.R**2-d**2)**0.5

            point1 = (a+b)*k + p        # Solution 1
            point2 = (a-b)*k + p        # Solution 2
            solns = np.array([point for point in [point1,point2] if self.point_in_arc(point)]) # Add them to solns iff they belong to the arc
            if VERBOSE: print("solns: ",solns)
            # Get the smalles solution
            for soln in solns:
                if mag(p-soln) < l_min and (soln-p).dot(k) >= 0:
                    l_min = mag(p-soln)
                    t_min = self.t(arg(soln))
        
        elif d == self.R: # If it's right on top of the arc, 1 soln
            point = p + k * (self.C-p).dot(k)
            if self.point_in_arc(point): # if it is in the arc
                if mag(p-point) < l_min and (point-p).dot(k) >= 0: # if it is less than before update
                    l_min = mag(p-point)
                    t_min = self.t(arg(point))
        
        if VERBOSE: print("final: ",l_min,t_min)
        return l_min, t_min
                
    
    # Checks if the vector is on the arc
    def point_in_arc(self,p:np.array,from_center:bool=False):
        p = p - self.C if not from_center else p # if the vector does not start from the cicle center, make it so

        # get the curve length argument of p, that belongs in [0,2π]
        t = self.t(arg(p))

        return t <= 1 and t >= 0 and (mag(p) - self.R) < 1e-8
    

    # Draws the arc on a predefined ax object
    def draw(self,ax,color='k',Npts=100,label='Lens'):
        t = np.linspace(0,0.5,Npts)
        pts = self.r(t)

        return ax.plot(pts.T[0],pts.T[1], c=color, label=label)

    # Prints the arc's parameters for debugging
    def print(self):
        print("Object of type arc.\n\n\tC = "+str(self.C)\
            +"\n\tR = "+str(self.R))





# This class is to represent a spline
class Spline:

    # Constructor
    def __init__(self, X:np.array, Y:np.array, phi:float = 0, scale:float = 2, theta:float = np.pi/2, position = np.array([0,-1])):
        self.X = X
        self.Y = Y
        self.phi = phi
        self.scale = scale
        self.theta = theta
        self.position = position
        self.n = len(X)
        self.a = self.solve_curvature()

        # breakpoint()

    # Use tridiaognal backsubstitution to solve for the spline coefficients
    def solve_curvature(self):
        # Create the empty matrices
        b = np.zeros([self.n])
        M = np.zeros([self.n,self.n])

        # Construct tridiagonal matrix M
        for i in range(self.n):
            if i == 0:
                M[i][i] = self.h(i)/3
                M[i][i+1] = self.h(i)/6

                b[i] = (self.Y[i+1]-self.Y[i])/self.h(i) - self.phi
                continue

            elif i == self.n-1:
                M[i][i-1] = self.h(i-1)/6
                M[i][i]   = self.h(i-1)/3

                b[i] = (self.Y[i-1]-self.Y[i])/self.h(i-1)
                continue

            M[i][i-1] = self.h(i-1)/6
            M[i][i]   = (self.h(i-1)+self.h(i))/3
            M[i][i+1] = self.h(i)/6

            b[i] = self.Y[i-1]/self.h(i-1) - self.Y[i]*(1/self.h(i-1)+1/self.h(i)) + self.Y[i+1]/self.h(i)

        # Convert matrix M to m only storing the diagonals
        # First diagonal
        m1 = []
        for i in range(0,self.n-1):
            if i == 0:
                m1.append(0)
            m1.append(M[i][i+1])
        m2 = [M[i][i] for i in range(self.n)]
        m3 = [M[i][i-1] for i in range(1,self.n)]
        m3.append(0)

        m = np.array([m1,m2,m3])

        # Solve the Equaiton Ma = b for a, using scipy.linalg
        a = la.solve_banded((1,1),m,b)

        return a

    # Helper function
    def h(self,i):
        return (self.X[i+1]-self.X[i])

    # Finds the index of the interval at which x belongs in
    def index(self,x):
        # Uses binary search
        mi = 0
        Mi = self.n-1
        midi = int((Mi+mi)/2)
        prevmid = -1

        while prevmid != midi and mi < Mi:

            if x > self.X[midi] and x < self.X[midi+1]:
                return midi
            elif x < self.X[midi]:
                Mi = midi
            else:
                mi = midi
    
            prevmid = midi
            midi = int((Mi+mi)/2)
    
        return mi

    # Returns the y value for a partucular arclength x 
    def y(self,x):
        x = 2*max(self.X)-x if x>max(self.X) else x # Adjust if x is halfway through then make it as if it isn't

        i = self.index(x)
        y = self.a[i]*(self.X[i+1]-x)**3/(6*self.h(i)) + self.a[i+1]*(x-self.X[i])**3/(6*self.h(i)) \
            + (self.Y[i]-self.h(i)**2*self.a[i]/6)*(self.X[i+1]-x)/self.h(i) \
            + (self.Y[i+1]-self.h(i)**2*self.a[i+1]/6)*(x-self.X[i])/self.h(i)

        return y

    # Calculates the scalar first derivative at x
    def y_prime(self,x):
        # Adjust if x is halfway through then make it as if it isn't
        if x>max(self.X):
            x = 2*max(self.X)-x
            a = -1
        else: 
            a = 1

        i = self.index(x)
        y_prime = -self.a[i]*(self.X[i+1]-x)**2/(2*self.h(i)) + self.a[i+1]*(x-self.X[i])**2/(2*self.h(i))\
            + (self.Y[i+1]-self.Y[i])/self.h(i) - self.h(i)*(self.a[i+1]-self.a[i])/6

        return y_prime*a

    # Calculates the scalar second derivative at x
    def y_double_prime(self,x):
        i = self.index(x)
        y_double_prime = self.a[i]*(self.X[i+1] - x)/self.h(i) + self.a[i+1]*(x-self.X[i])/self.h(i)

        return y_double_prime

    # Returns rotation matrix for a particular angle
    def R(self,theta):
        R = np.zeros([2,2])
        R[0][0] = np.cos(theta)
        R[0][1] = -np.sin(theta)
        R[1][0] = np.sin(theta)
        R[1][1] = np.cos(theta)

        return R

    # returns a position vector for the spline point taking into account scaling and rotation
    def r(self,t):
        if isinstance(t,Iterable): return np.array([self.r(i) for i in t]) # Return array of positions if you ask for it
        # breakpoint()
        r = np.array([t,self.y(t)]) #- np.array([(max(self.X)-min(self.X)),0])
        r = self.scale * np.matmul(self.R(self.theta),r) + self.position

        return r
    
    # Calculates the first derivative of the position vector r
    def r_prime(self,x):
        r_prime = np.array([1,self.y_prime(x)])
        r_prime = self.scale * np.matmul(self.R(self.theta),r_prime)

        return r_prime

    # Calculates the second derivative of the position vector r
    def r_double_prime(self,x):
        r_double_prime = np.array([0,self.y_double_prime(x)])
        r_double_prime = self.scale * np.matmul(self.R(self.theta),r_double_prime)
        
        return r_double_prime

    # Returns the tangent vector of the thingy
    def t_hat(self,t):
        if isinstance(t,Iterable): return np.array([self.t_hat(i) for i in t]) # Return array of positions if you ask for it
        
        r_prime = self.r_prime(t)         # Get the veolocity and normalise it
        return r_prime/mag(r_prime)

    # Returns the normal of the curve
    def n_hat(self,t):
        if isinstance(t,Iterable): return np.array([self.n_hat(i) for i in t]) # Return array of positions if you ask for it
        
        t = self.t_hat(t)               # Get tortion and rotate it by π/2
        return np.array([-t[1],t[0]])

   

    # Given a position and a direction calculates an intersection
    def get_intersection(self,p:np.array, k:np.array,VERBOSE:bool=False):
        # Get the intersection of a curve by solving the equation r(l) = S(t)
        
        # set the appropriate constants
        n = np.array([-k[1],k[0]]) # Get a unit vector perpendicular to k
        w = np.array([0.,0.]) # Create the array for the W coefficients
        w[0] = self.scale*(n[1]*np.cos(self.theta) - n[0]*np.sin(self.theta))
        w[1] = self.scale*(n[0]*np.cos(self.theta) + n[1]*np.sin(self.theta))
        p_new = p - self.position # Set the new position vector according to notes
        t_max = max(self.X)

        if VERBOSE: print("n: ",n)
        if VERBOSE: print("θ: ",self.theta/np.pi,"π")
        if VERBOSE: print("turn: ",[np.cos(self.theta),np.sin(self.theta)])
        if VERBOSE: print("w: ",w)

        # These variables will store the minimum lambda and t while the loop is going
        l_min = float('inf')
        t_min = -1

        # Find the interesections for all i curves there:
        # Remember the spline is created by having half of controllable and the other half mirrored.
        # As a result, we should solve two cubics. One for the left and one for the right side.
        for i in range(len(self.X)-1):
            # For the left side
            e = np.array([0.,0.,0.,0.]) # Initialise the array for the e cubic coefficients
            e[3] = w[0]/(6*self.h(i))*(self.a[i+1]-self.a[i])
            e[2] = w[0]/(2*self.h(i))*(self.X[i+1]*self.a[i]-self.X[i]*self.a[i+1])
            e[1] = w[0]/(6*self.h(i))*(self.a[i+1]*(3*self.X[i]**2-self.h(i)**2)-self.a[i]*(3*self.X[i+1]**2-self.h(i)**2)+6*(self.Y[i+1]-self.Y[i])) + w[1]
            e[0] = w[0]/(6*self.h(i))*(self.a[i]*self.X[i+1]*(self.X[i+1]**2-self.h(i)**2)-self.a[i+1]*self.X[i]*(self.X[i]**2-self.h(i)**2)+6*(self.Y[i]*self.X[i+1]-self.Y[i+1]*self.X[i])) - p_new.dot(n)

            if VERBOSE: print('Calculating for point i =',i)
            if VERBOSE: print("This has equation: ",e[3]/w[0],"t**3 +",e[2]/w[0],"t**2 +",(e[1]-w[1])/w[0],"t +",(e[0]+p_new.dot(n))/w[0])
            if VERBOSE: print("e: ",e)
            if VERBOSE: print("\tCalculating Left")

            # Calculate the solutions of the cubic polynomial
            # solns_left = solve_cubic(e) if w[0]!=0 else solve_linear(e[0:2])
            solns_left = np.roots(np.flip(e))
            if VERBOSE: print("Uprocessed solns:",solns_left)
            
            # Keep only the real solutions
            solns_left = np.array([soln.real for soln in solns_left if abs(soln.imag) < 1e-8])
            if VERBOSE: print("Real solns:",solns_left)

            # Make sure that the solutions are within the range of each curve
            solns_left = np.array([soln for soln in solns_left if (soln>self.X[i] and soln<self.X[i+1])])
            if VERBOSE: print("Ranged solns:",solns_left)

            # For the right side
            e[1] = w[0]/(6*self.h(i))*(self.a[i+1]*(3*self.X[i]**2-self.h(i)**2)-self.a[i]*(3*self.X[i+1]**2-self.h(i)**2)+6*(self.Y[i+1]-self.Y[i])) - w[1]
            e[0] = w[0]/(6*self.h(i))*(self.a[i]*self.X[i+1]*(self.X[i+1]**2-self.h(i)**2)-self.a[i+1]*self.X[i]*(self.X[i]**2-self.h(i)**2)+6*(self.Y[i]*self.X[i+1]-self.Y[i+1]*self.X[i])) - p_new.dot(n) + 2*t_max*w[1]

            if VERBOSE: print("\tCalculating Right")
            # Solve for the rigth side
            # solns_right = solve_cubic(e) if w[0]!=0 else solve_linear(e[0:2])
            solns_right = np.roots(np.flip(e))
            if VERBOSE: print("Uprocessed solns:",solns_right)
            solns_right = np.array([2*t_max-t for t in solns_right])
            if VERBOSE: print("Coordinated solns:",solns_right)

            # Keep only the real solutions
            solns_right = np.array([soln.real for soln in solns_right if abs(soln.imag) < 1e-8])
            if VERBOSE: print("Real solns:",solns_right)

            # Make sure that the right solutions are within the range of each curve
            solns_right = np.array([soln for soln in solns_right if (2*t_max - soln>self.X[i] and 2*t_max - soln<self.X[i+1])])
            if VERBOSE: print("Ranged solns:",solns_right)

            # Add the remaining solns in 1 array
            solns = []
            for s in solns_left:solns.append(s)
            for s in solns_right:solns.append(s)
            if VERBOSE: print("FINAL SOLNS: ",solns)

            #if there are any solutoins left update the minima
            if len(solns) > 0:
                # Calculate l (the distance between the curve and the intersection point)
                for t in solns:
                    l = (self.r(t) - p).dot(k)  # Calculate the new distance
                    if VERBOSE: print("\tl: ",l)
                    if l > 0 and l < l_min:     # If we are moving in the direction of the direction vector for less of a distance
                        l_min = l               # Update l_min and t_min
                        t_min = t

        # Return the minimum pair
        return l_min,t_min



    # Draws the spline on axis ax
    def draw(self,ax,color='darkblue',Npts=100,label='Spline'):
        x = np.linspace(min(self.X),min(self.X)+2*(max(self.X)-min(self.X)),Npts)

        # y = np.array([self.y(xi) for xi in x])
        # ax.plot(x,y,color='red',label=label)

        # ax.scatter(points.T[0],points.T[1],color=color,s=10)
        rs = np.array([self.r(xi) for xi in x])
        ax.plot(rs.T[0],rs.T[1],color=color)

    def draw_frenet_frame(self,ax,color='darkgreen',Npts=15,label='Frenet Frame of spline'):
        t = np.linspace(min(self.X),min(self.X)+2*(max(self.X)-min(self.X)),Npts)

        rs = self.r(t)
        ns = self.n_hat(t)
        ts = self.t_hat(t)

        ax.quiver(rs.T[0],rs.T[1],ns.T[0],ns.T[1],color='darkgreen',label='Frenet frame')
        ax.quiver(rs.T[0],rs.T[1],ts.T[0],ts.T[1],color='darkred',label='Frenet frame')