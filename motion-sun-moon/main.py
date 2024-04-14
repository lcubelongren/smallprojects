
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from skyfield.api import load, load_file, N, S, E, W, wgs84
from skyfield.almanac import sunrise_sunset


lat_lon_list = [(43.53, 172.62), (77.85, 166.67), (90, 0)]  # S, E
lat_lon_strings = ['Christchurch', 'McMurdo', 'Pole']

obj_strings = ['sun', 'moon']
#obj_strings = ['moon']


def findObject(t, lat, lon, eph, obj_str):
    earth, obj = eph['earth'], eph[obj_str]
    coords = wgs84.latlon(lat * S, lon * E)
    topos = earth + coords
    astrometric = topos.at(t).observe(obj)
    alt, az, d = astrometric.apparent().altaz()
    return coords, az, alt, 


def angle2polar(angle, r):
    angle += 90  # place north up
    x = - r * np.cos(np.deg2rad(angle))  # negative to flip across y-axis
    y = r * np.sin(np.deg2rad(angle))
    return x, y


num = 1 + (365 * 24)
#num = 1 + (365 * 1)
ts = load.timescale()
t0 = ts.utc(2023, 1, 1, 0, 0)
t1 = ts.utc(2024, 1, 1, 0, 0)
t_list = ts.linspace(t0, t1, num=num)


def plotTimepoints(lat, lon, t_list, obj_str):
    eph = load_file('de440_excerpt.bsp')
    x, y = np.zeros((2, len(t_list)))
    for i,t in enumerate(t_list):
        _, az_raw, alt_raw = findObject(t, lat, lon, eph, obj_str)
        az, alt = az_raw.degrees, alt_raw.degrees
        x[i], y[i] = angle2polar(angle=az, r=alt+90)
    return x, y


def animate(i, cax, ln, ttl, x, y, colors):
    #print(i, t_list[i].utc)
    
    cax.set_offsets(np.transpose((x[:i], y[:i])))
    cax.set_color(colors)
    
    ln.set_data(x[i-25:i], y[i-25:i])
    ln.set_color(colors[i-1])
    
    ttl.set_text(t_list[i].utc_strftime('%Y %b %d at %H'))
    return cax, ln, ttl,
    

for lat_lon,lat_lon_str in zip(lat_lon_list,lat_lon_strings):
    print(lat_lon,lat_lon_str)
    for obj_str in obj_strings:
        print(obj_str)
    
        lat, lon = lat_lon
        x, y = plotTimepoints(lat, lon, t_list, obj_str=obj_str)

        fig, ax = plt.subplots(1, 1, figsize=(5, 5), dpi=500)
        colors = plt.cm.twilight(np.linspace(0, 1, num)[::-1])

        cax = ax.scatter([], [], s=5)
        ln, = plt.plot([], [], lw=3)

        horizon = angle2polar(angle=np.linspace(0, 360, 1000), r=90)
        ax.plot(horizon[0], horizon[1], c='k', lw=0.75)

        ttl = ax.text(0.0, 0.0, '', horizontalalignment='left', verticalalignment='bottom', transform=ax.transAxes, fontsize=6)

        ax.axis('square')
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        extent = 90+120
        ax.set_xlim([-extent, extent])
        ax.set_ylim([-extent, extent])

        interval = 5.952  # 1 wk/sec = 168 points/sec => 5.952 ms interval
        #interval *= 24
        
        ts = np.arange(len(t_list))
        ani = animation.FuncAnimation(fig, animate, frames=ts, blit=True,
                                      fargs=(cax, ln, ttl, x, y, colors),
                                      repeat=False, interval=interval)  
                            
        plt.savefig('frame0.png')
                            
        save_str = 'animation_{}_{}'.format(obj_str, lat_lon_str)
        ani.save(save_str + '.mp4')
        
        cax.set_offsets(np.transpose((x, y)))
        cax.set_color(colors)
        ln.set_data([], [])
        plt.savefig(save_str + '.png')