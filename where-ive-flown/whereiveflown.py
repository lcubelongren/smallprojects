
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


change_this_folder_name = r'E:\Archive\collections\Boarding Passes'

def flights(img_dir):
    img_list = [str(x.stem) for x in Path(img_dir).glob('*_001.png')]
    origins, destinations, dates = [], [], []
    for fname in img_list:
        date, number, origin_name, destination_name = fname.split('_')[:-1]
        origin = float(airports.airport_iata(origin_name).lat), \
                 float(airports.airport_iata(origin_name).lon)
        destination = float(airports.airport_iata(destination_name).lat), \
                      float(airports.airport_iata(destination_name).lon)
        origins.append(origin)
        destinations.append(destination)
        dates.append(date)
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
    
    ax.add_feature(cartopy.feature.OCEAN, color='grey')
    ax.add_feature(cartopy.feature.LAND, color='black')
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='white', linewidth=0.1)
    ax.gridlines(xlocs=np.array([-90, 0, 90, 180])-135+twist, ylocs=[], linewidth=0.5, color='w')
    
    times = [datetime.datetime.strptime(date, '%Y%m%d') for date in dates]
    timedeltas = [((time - np.min(times))).total_seconds() for time in times]
    cmap = plt.colormaps['viridis']
    colors = cmap(timedeltas / np.max(timedeltas))
    for origin,destination,color in zip(origins, destinations, colors):
        plt.plot([origin[1], destination[1]], [origin[0], destination[0]],
                 transform=ccrs.Geodetic(), color=color, marker='o', markevery=[0, -1], markersize=3, linewidth=2)
    plt.scatter([0, 0], [0, 0], transform=ccrs.PlateCarree(), c=[0, 1], s=0, cmap=cmap)  # to make colorbar

    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.savefig('whereiveflown_zoomed.png', transparent=True, bbox_inches='tight')

    cbar = plt.colorbar(location='bottom', fraction=0.09, pad=0.00, aspect=50)
    cbar.set_ticks(ticks=[0, 1], labels=[str(times[0])[:10], str(times[-1])[:10]], color='w')
    cbar.set_label(label='time', color='w')

    plt.tight_layout()
    plt.savefig('whereiveflown.png', facecolor='black')


if __name__ == '__main__':
    origins, destinations, dates = flights(change_this_folder_name)
    mapping(origins, destinations, dates)
