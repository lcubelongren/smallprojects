
import numpy as np
import pandas as pd
import datetime
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.transforms import offset_copy

import cartopy.crs as ccrs
import cartopy.feature as cfeature


plt.style.use('dark_background')
fig, ax = plt.subplots(1, 1, figsize=(8, 8), dpi=300)
fig.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95)
ax.axis('off')

def animate(i, lons, lats, heights):
    print(i)

    projection = ccrs.NearsidePerspective(central_longitude=lons[i], central_latitude=lats[i], satellite_height=heights[i])
    projection.threshold = 1000
    ax = fig.add_subplot(projection=projection)

    ax.add_feature(cfeature.NaturalEarthFeature('physical', 'ocean', '50m', facecolor='lightsteelblue'), zorder=5)
    ax.add_feature(cfeature.NaturalEarthFeature('physical', 'land', '50m', facecolor='ghostwhite'), zorder=6)
    ax.add_feature(cfeature.NaturalEarthFeature('physical', 'antarctic_ice_shelves_polys', '50m', facecolor=np.array([22, 114, 184])/255), zorder=9)

    return ax
    
frames = 160, 40
lons = np.append(np.linspace(0, 360, frames[0]), np.linspace(360, 360, frames[1]))
lats = np.append(np.linspace(0, -90, frames[0]), np.linspace(-90, -90, frames[1]))
heights = np.append(np.linspace(1e9, 1e9, frames[0]), np.logspace(np.log10(1e9), np.log10(4.5e6), frames[1]))

ani = animation.FuncAnimation(fig, animate, frames=len(heights), blit=False,
                              fargs=(lons, lats, heights),
                              repeat=False, interval=41.666)  # 24fps
#plt.show()
                    
print('saving animation...');  ani.save('intro.mp4')