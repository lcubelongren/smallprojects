#!/usr/bin/env python
# coding: utf-8

# ## Mapping the Terrain of Berlin

# Data is taken from the following source:  
# https://land.copernicus.eu/imagery-in-situ/eu-dem/eu-dem-v1.1?tab=download

# Loading the data with the following:  
# https://github.com/cgohlke/tifffile

# In[1]:


import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import animation
import tifffile


# In[2]:


im = tifffile.imread(r"C:\Users\lcube\Desktop\project_data\eu_dem_v11_E40N30\eu_dem_v11_E40N30.TIF")
# print(np.shape(im))


# A note on coordinates:  
# The standard degree system looks to be EPSG:4326.   
# In this form, Berlin is at 52°31′12″N 13°24′18″E.   
# The source of the data uses the form EPSG:3035.  
# Here, Berlin then becomes X: 4552036.45, Y: 3273268.27.  
# The city lies on the E40N30 tile, thus the lower left  
# point is at 4000km x 3000km from (0,0).
# Resolution for the data is 25m.
# New points within this tile are then,

# In[3]:


res = 25
berlin_x = 4552036.45
berlin_y = 3273268.27
rel_x = 3086656.97
rel_y = -2292253.81
X = int(((berlin_x - 4000*1000)) / res)
Y = int(((berlin_y - 3000*1000)) / res)
# print(X,Y)


# In[4]:


# A = 5000
# vmin, vmax = 25, 35
# plt.figure(dpi=220)
# plt.imshow(im[-Y-A:-Y+A,X-A:X+A], cmap='Blues', vmin=vmin, vmax=vmax)
# plt.title('{} km'.format(res*A*2 / 1e3))
# plt.axis('off')
# plt.colorbar()
# plt.show()


# In[5]:


frames = 25
vmin, vmax = 25, 35

def update(i):
    A = 25*i + 1
    plt.cla()
    ax.imshow(im[-Y-A:-Y+A,X-A:X+A], cmap='Blues', vmin=vmin, vmax=vmax)
    ax.set_title('{} km'.format(res*A*2 / 1e3))
    ax.axis('off')

fig = plt.figure(dpi=220)
ax = fig.add_subplot()
ani = animation.FuncAnimation(fig, update, frames, interval=100)

if __name__ == '__main__':
    # plt.show()
    ani.save('output.gif')


