
import json
import datetime
import numpy as np

import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.cm as cm


## to download from Google Maps
## (Android) Settings -> Google location settings -> Location services -> Timeline -> Export Timeline data
## (iOS)
fnames_dict = {
    'Android': 'data/Timeline_20250703.json',
    'iOS': 'data/location-history_20251206.json'
}

def gps(fnames_dict):
    lats = []
    lons = []
    times = []
    for software in fnames_dict.keys():
        fname = fnames_dict[software]
        with open(fname) as f:
            data = json.load(f)
            if software == 'Android':
                data = data['semanticSegments']
            for entry in data:
                # if 'timelinePath' in entry:
                    # for timelinePath in entry['timelinePath']:
                        # lat, lon = timelinePath['point'].split(', ')
                        # time = timelinePath['time']
                        # lats.append(float(lat[:-2]))
                        # lons.append(float(lon[:-2]))
                        # times.append(datetime.datetime.strptime(time[:19], '%Y-%m-%dT%H:%M:%S'))
                if 'activity' in entry:
                    activity = entry['activity']
                    if not activity['topCandidate']['type'] in ['UNKNOWN', 'UNKNOWN_ACTIVITY_TYPE', 'flying']:
                        for se in ['start', 'end']:
                            if software == 'Android':
                                lat, lon = activity[se]['latLng'].split(', ')
                            if software == 'iOS':
                                lat, lon = activity[se].split('geo:')[-1].split(',')
                            time = entry[se + 'Time']
                            lats.append(float(lat[:-2]))
                            lons.append(float(lon[:-2]))
                            times.append(datetime.datetime.strptime(time[:19], '%Y-%m-%dT%H:%M:%S'))
    return lats, lons, times


def gps_OLD(fname):
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
    
    ax.add_feature(cartopy.feature.OCEAN, color='grey', zorder=0)
    ax.add_feature(cartopy.feature.LAND, color='black', zorder=1)
    ax.add_feature(cartopy.feature.LAKES, color='grey', zorder=2)
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='white', linewidth=0.1, zorder=3)
    ax.gridlines(xlocs=np.array([-90, 0, 90, 180])-135+twist, ylocs=[], linewidth=0.5, color='w', zorder=4)
    
    timedelta = [(time - times[0]).total_seconds() for time in times]
    plt.scatter(lons, lats, transform=ccrs.PlateCarree(),
                c=timedelta, s=8, cmap='viridis', zorder=5)
    
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.savefig('whereivebeen_zoomed.png', transparent=True, bbox_inches='tight')

    cbar = plt.colorbar(location='bottom', fraction=0.09, pad=0.00, aspect=50)
    cbar.set_ticks(ticks=[timedelta[0], timedelta[-1]], labels=[str(times[0])[:10], str(times[-1])[:10]], color='w')
    cbar.set_label(label='time', color='w')

    plt.tight_layout()
    plt.savefig('whereivebeen.png', facecolor='black')


if __name__ == '__main__':
    lats, lons, times = gps(fnames_dict)
    #lats, lons, times = [40],[20],[datetime.datetime.now()]
    mapping(lats, lons, times)
