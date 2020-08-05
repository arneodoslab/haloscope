import numpy as np
import matplotlib.pyplot as plt 
from curves import *
from ray import *

# Create a spline
X = np.array([0,0.25,0.5])
Y = np.array([0,0.2,0.5])

s = Spline(X,Y,phi=3)

# Create a bunch of rays emanating from a point
p = np.array([1.5,1])
Nrays = 100
theta_min = -np.pi
theta_max = 0
rays = []
for theta in np.linspace(theta_min,theta_max,Nrays):
    k = np.array([np.cos(theta),np.sin(theta)])
    rays.append(Ray(start=p,direction=k))


# Create the figure
fig = plt.figure(figsize=(5,5),dpi = 130)
ax = fig.add_subplot(111,aspect='equal')

# Plot the spline
s.draw(ax)

# Check the intersection between each ray
for ray in rays:
    p = ray.points[-1]
    k = ray.direction[-1]
    l,t = s.get_intersection(p,k)
    l = 1 if t<0 else l
    ray.points = np.append(ray.points,[p+l*k],axis=0)
    ray.draw(ax)
    plt.quiver([p[0]],[p[1]],[k[0]],[k[1]])

ax.grid()
plt.show()