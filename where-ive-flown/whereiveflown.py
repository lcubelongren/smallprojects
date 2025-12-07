
import datetime
from pathlib import Path

import numpy as np
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl

from pyairports.airports import Airports
airports = Airports()


img_dir = r'D:\Projects\collections\Boarding Passes'
missing_fname = '.\missing_list.txt'

def boarding_passes(img_dir):
    img_list = [str(x.stem) for x in Path(img_dir).glob('*_001.png')]
    origins, destinations, dates = [], [], []
    for fname in img_list:
        date, number, origin, destination = fname.split('_')[:-1]
        origins.append(origin)
        destinations.append(destination)
        dates.append(date)
    return origins, destinations, dates
    
def missing_list(missing_fname):
    file = np.loadtxt(missing_fname, dtype=str)
    origins, destinations, dates = file.T
    return origins, destinations, dates

def mapping(origins, destinations, dates):
    plt.figure(figsize=(16,9), dpi=300)
    
    twist = 67
    projection = ccrs.RotatedPole(pole_longitude=twist,           # twist things around both poles
                                  pole_latitude=0,                # shift poles, centered up and down
                                  central_rotated_longitude=-33)  # shift poles to be at left and right
    projection.threshold = projection.threshold / 10  # makes for smoother line plots
    ax = plt.axes(projection=projection)
    ax.set_global()
    
    ax.add_feature(cartopy.feature.OCEAN, color='grey', zorder=0)
    ax.add_feature(cartopy.feature.LAND, color='black', zorder=1)
    ax.add_feature(cartopy.feature.LAKES, color='grey', zorder=2)
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='white', linewidth=0.1, zorder=3)
    ax.add_feature(cartopy.feature.STATES, edgecolor='white', linewidth=0.1, zorder=4)
    ax.gridlines(xlocs=np.array([-90, 0, 90, 180])-135+twist, ylocs=[], linewidth=0.5, color='w', zorder=4)

    times = [datetime.datetime.strptime(date, '%Y%m%d') for date in dates]
    timedeltas = [((time - np.min(times))).total_seconds() for time in times]
    cmap = plt.colormaps['viridis']
    colors = cmap(timedeltas / np.max(timedeltas))
    for origin,destination,color in zip(origins, destinations, colors):
        if len(origin) == 3:  # IATA
            origin_lat = float(airports.airport_iata(origin).lat)
            origin_lon = float(airports.airport_iata(origin).lon)
            destination_lat = float(airports.airport_iata(destination).lat)
            destination_lon = float(airports.airport_iata(destination).lon)
        else:  # already lat, lon
            origin_lat = float(origin.split(',')[0])
            origin_lon = float(origin.split(',')[1])
            destination_lat = float(destination.split(',')[0])
            destination_lon = float(destination.split(',')[1])
        plt.plot([origin_lon, destination_lon], [origin_lat, destination_lat], transform=ccrs.Geodetic(), 
                 color=color, marker='o', markevery=[0, -1], markersize=3, linewidth=2, zorder=5)
    plt.scatter([0, 0], [0, 0], transform=ccrs.PlateCarree(), c=[0, 1], s=0, cmap=cmap)  # to make colorbar

    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.savefig('whereiveflown_zoomed.png', transparent=True, bbox_inches='tight')

    cbar = plt.colorbar(location='bottom', fraction=0.09, pad=0.00, aspect=50)
    cbar.set_ticks(ticks=[0, 1], labels=[str(np.min(times))[:10], str(np.max(times))[:10]], color='w')
    cbar.set_label(label='time', color='w')

    plt.tight_layout()
    plt.savefig('whereiveflown.png', facecolor='black')


if __name__ == '__main__':
    data = (missing_list(missing_fname), boarding_passes(img_dir))
    origins, destinations, dates = np.concatenate(data, axis=1)
    mapping(origins, destinations, dates)
