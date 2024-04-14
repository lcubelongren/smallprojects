
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from skyfield.api import load, load_file, N, S, E, W, wgs84
from skyfield.almanac import sunrise_sunset


lat_lon_list = [(43.53, 172.62), (77.85, 166.67), (90, 0)]  # S, E
lat_lon_strings = ['Christchurch', 'McMurdo', 'Pole']

obj_strings = ['sun', 'moon']


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
num = 1 + (365 * 1)
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

lat, lon = lat_lon_list[2]
x, y = plotTimepoints(lat, lon, t_list, 'sun')

plt.plot(x, label='angle')
plt.plot(y, label='r')
plt.legend()
plt.show()
