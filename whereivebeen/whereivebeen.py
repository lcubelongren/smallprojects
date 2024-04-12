
import json
import datetime
import numpy as np

import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.cm as cm


change_this_folder_name = 'Takeout\Location History (Timeline)\Records.json'

def gps(fname):
    with open(fname) as f:
        data = json.load(f)
        lats = []
        lons = []
        times = []
        for entry in data['locations']:
            if entry['source'] in ['GPS', 'CELL', 'WIFI', 'UNKNOWN']:
                lat, lon, time = entry['latitudeE7'], entry['longitudeE7'], entry['timestamp']
                lats.append(lat/1e7)
                lons.append(lon/1e7)
                times.append(datetime.datetime.strptime(time[:19], '%Y-%m-%dT%H:%M:%S'))
            else:
                print(entry['source'])
    return lats, lons, times


def mapping(lats, lons, times):
    plt.figure(figsize=(16,9), dpi=300)
    
    twist = 67
    projection = ccrs.RotatedPole(pole_longitude=twist,           # twist things around both poles
                                  pole_latitude =    0,           # shift poles, centered up and down
                                  central_rotated_longitude=-33)  # shift poles to be at left and right
    ax = plt.axes(projection=projection)
    ax.set_global()
    
    ax.add_feature(cartopy.feature.OCEAN, color='grey')
    ax.add_feature(cartopy.feature.LAND, color='black')
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='white', linewidth=0.1)
    ax.gridlines(xlocs=np.array([-90, 0, 90, 180])-135+twist, ylocs=[], linewidth=0.5, color='w')
    
    timedelta = [(time - times[0]).total_seconds() for time in times]
    plt.scatter(lons, lats, transform=ccrs.PlateCarree(),
                c=timedelta, s=2, cmap='viridis')
    
    plt.tight_layout()
    plt.savefig('whereivebeen_zoomed.png', transparent=True)

    cbar = plt.colorbar(location='bottom', fraction=0.09, pad=0.00, aspect=50)
    cbar.set_ticks(ticks=[timedelta[0], timedelta[-1]], labels=[str(times[0])[:10], str(times[-1])[:10]], color='w')
    cbar.set_label(label='time', color='w')

    plt.tight_layout()
    plt.savefig('whereivebeen.png', facecolor='black')


if __name__ == '__main__':
    lats, lons, times = gps(change_this_folder_name)
    #lats, lons, times = [40],[20],[datetime.datetime.now()]
    mapping(lats, lons, times)
