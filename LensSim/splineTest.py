import numpy as np
import matplotlib.pyplot as plt 
from curves import *
from ray import *
from tqdm import *

# Create a spline
s1 = Spline([0,0.25,0.5],[0.,0.18,0.1],phi=1,theta=-np.pi/2,position=np.array([0., 2.54]),scale=5.08)
s2 = Spline([0,0.5],[0,0.2],phi=1,theta= np.pi/2,position=np.array([0.,-2.54]),scale=5.08)
arc1 = Arc(point_1=np.array([0.,2.54]),point_2=np.array([1.,0]),point_3=np.array([0,-2.54]))

lens = Lens([arc1,s2])

# Create a bunch of rays emanating from a point
p = np.array([-5,0])
Nrays = 100
theta_min = -np.pi/2
theta_max = np.pi/2
rays = []
for theta in np.linspace(theta_min,theta_max,Nrays):
    k = np.array([np.cos(theta),np.sin(theta)])
    rays.append(Ray(start=p,direction=k))

# # Create only one ray:
# p = np.array([-5,1.5])
# theta = 0*np.pi/4
# rays = []
# k = np.array([np.cos(theta),np.sin(theta)])
# rays.append(Ray(start=p,direction=k))


# Create the figure
fig = plt.figure(figsize=(5,5),dpi = 130)
ax = fig.add_subplot(111,aspect='equal')
lens.draw(ax)

# s1.draw_frenet_frame(ax)
# s2.draw_frenet_frame(ax)

for ray in tqdm(rays):
    ray.shoot_through_lens(lens)
    ray.draw(ax)

# # Check the intersection between each ray
# for ray in tqdm(rays):
#     p = ray.points[-1]
#     k = ray.direction[-1]
#     l,t = s2.get_intersection(p,k)
#     l = 1 if t<0 else l
#     ray.points = np.append(ray.points,[p+l*k],axis=0)
#     ray.draw(ax)
#     plt.quiver([p[0]],[p[1]],[k[0]],[k[1]])

ax.set_xlim(-5,5)
ax.set_ylim(-5,5)
ax.grid()
plt.show()