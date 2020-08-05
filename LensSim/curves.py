# Contains class for lens
import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as c
import pandas as pd
import scipy.linalg as la
from scipy.optimize import fsolve
from collections.abc import Iterable

def mag(a:np.array):
    return a.dot(a)**0.5

def arg(a):
    if a[0] == 0:
        if a[1]>0:
            return np.pi/2
        else:
            return 3/2*np.pi

    elif a[0]>0:
        if a[1]>0:
            return np.arctan(a[1]/a[0])
        else:
            return np.arctan(a[1]/a[0])+2*np.pi

    else:
        return np.arctan(a[1]/a[0])+np.pi

def random(m,M):
    return np.random.rand()*(M-m) + m

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
    def __init__(self,pointX:np.array,pointY:np.array):
        
        # Find the center and radius of the arc, and decide its direction
        p = 1/2*(pointX + pointY)
        v = pointY - pointX
        v[0] = v[1]
        v[1] = -(pointY-pointX)[0]
        v = v/mag(v)
        l = - p[1]/v[1]

        self.C = p+v*l
        self.R = mag(self.C - pointX)
        self.theta = arg(pointY-self.C)

        dirPositive = (pointX-self.C).dot(np.array([1,0])) >= 0
        if not dirPositive:
            self.phi = self.theta/2
            self.theta = 2*np.pi - self.theta
        else:
            self.phi = 2*np.pi - self.theta/2

    # Returns the tangent vector to the arc at an angle t
    def t_hat(self,t):
        return np.array([-np.sin(self.phi + t),np.cos(self.phi + t)])
    
    # returns the normal vector to the arc at an angle t
    def n_hat(self,t):
        return - np.array([np.cos(self.phi + t),np.sin(self.phi + t)])
    
    # Returns a vector to a point at an angle t of the curve
    def r(self,t):
        if isinstance(t,Iterable): return np.array([self.r(i) for i in t])
        return self.C +self.R*np.array([np.cos(t),np.sin(t)])

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
                    t_min = arg(soln)
        
        elif d == self.R: # If it's right on top of the arc, 1 soln
            point = p + k * (self.C-p).dot(k)
            if self.point_in_arc(point): # if it is in the arc
                if mag(p-point) < l_min and (point-p).dot(k) >= 0: # if it is less than before update
                    l_min = mag(p-point)
                    t_min = arg(point)
        
        if VERBOSE: print("final: ",l_min,t_min)
        return l_min, t_min
                
    
    # Checks if the vector is on the arc
    def point_in_arc(self,p:np.array,from_center:bool=False):
        p = p - self.C if not from_center else p # if the vector does not start from the cicle center, make it so

        # get the argument of p, that belongs in [0,2π]
        theta = arg(p)

        # if argument is within the thingy return true
        theta_prime = theta - self.phi if theta - self.phi >=0 else 2*np.pi + theta - self.phi

        return theta_prime <= self.theta and (mag(p) - self.R) < 1e-8
        

    # Draws the arc on a predefined ax object
    def draw(self,ax,color='k',Npts=100,label='Lens'):
        angles = np.linspace(self.phi,self.phi+self.theta,Npts)
        ptsX = self.R*np.cos(angles) + self.C[0]
        ptsY = self.R*np.sin(angles) + self.C[1]

        ax.scatter(self.R*np.cos(angles[0])+self.C[0],self.R*np.sin(angles[0])+self.C[1])
        
        return ax.plot(ptsX,ptsY, c=color, label=label)

    # Prints the arc's parameters for debugging
    def print(self):
        print("Object of type arc.\n\n\tC = "+str(self.C)\
            +"\n\tR = "+str(self.R)\
            +"\n\tTheta = "+str(self.theta*180/np.pi)\
            +"\n\tphi = "+str(self.phi*180/np.pi)\
            +"\n\tdirPositive = "+str(self.dirPositive)+"\n")





# This class is to represent a spline
class Spline:

    # Constructor
    def __init__(self, X:np.array, Y:np.array, phi:float = 0, alpha = None, scale:float = 2, theta:float = np.pi/2, position:np.array = np.array([0,-1])):
        self.X = X
        self.Y = Y
        self.phi = phi
        self.alpha = alpha
        self.scale = scale
        self.theta = theta
        self.position = position
        self.n = len(X)
        self.a = self.solve_curvature()

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
    def yprime(self,x):
        i = self.index(x)
        yprime = -self.a[i]*(self.X[i+1]-x)**2/(2*self.h(i)) + self.a[i+1]*(x-self.X[i])**2/(2*self.h(i))\
            + (self.Y[i+1]-self.Y[i])/self.h(i) - self.h(i)*(self.a[i+1]-self.a[i])/6

        return yprime

    # Calculates the scalar second derivative at x
    def ydoubleprime(self,x):
        i = self.index(x)
        ydoubleprime = self.a[i]*(self.X[i+1] - x)/self.h(i) + self.a[i+1]*(x-self.X[i])/self.h(i)

        return ydoubleprime

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

        r = np.array([t,self.y(t)]) #- np.array([(max(self.X)-min(self.X)),0])
        r = self.scale * np.matmul(self.R(self.theta),r) + self.position

        return r
    
    # Calculates the first derivative of the position vector r
    def rprime(self,x):
        rprime = np.array([1,self.yprime(x)])
        rprime = self.scale * np.matmul(self.R(self.theta),rprime)

        return rprime

    # Calculates the second derivative of the position vector r
    def rdoubleprime(self,x):
        rdoubleprime = np.array([0,self.ydoubleprime(x)])
        rdoubleprime = self.scale * np.matmul(self.R(self.theta),rdoubleprime)
        
        return rdoubleprime

    # Returns the tangent vector of the thingy
    def t_hat(self,t):
        rprime = self.rprime(t)
        return rprime/mag(rprime)

    # Returns the normal of the curve
    def n_hat(self,t):
        rdoubleprime = self.rdoubleprime(t)
        return rdoubleprime/mag(rdoubleprime)

   

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
