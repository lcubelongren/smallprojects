from pathlib import Path
import json
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cartopy
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt


year = 2025
dates = np.linspace(datetime(year+0, 1, 1, 0, 0, 0),
                    datetime(year+1, 1, 1, 0, 0, 0), 365*24*60+1)[:-1]

# background information
aircraft_models = {
    'N42RF': 'Lockheed WP-3D',
    'N43RF': 'Lockheed WP-3D',
    'N46RF': 'DHC-6 Twin Otter',
    'N48RF': 'DHC-6 Twin Otter',
    'N49RF': 'Gulfstream IV',
    'N56RF': 'DHC-6 Twin Otter',
    'N57RF': 'DHC-6 Twin Otter',
    'N65RF': 'Beech King Air',
    'N67RF': 'Beech King Air',
    'N68RF': 'Beech King Air',
}

aircraft_colors = {
    'DHC-6 Twin Otter': 'red',
    'Beech King Air': 'green',
    'Lockheed WP-3D': 'blue',
    'Gulfstream IV': 'yellow',
}

aircraft_previouspoint = {}
for callsign in aircraft_models.keys():
    aircraft_previouspoint[callsign] = {}
    aircraft_previouspoint[callsign]['lat_avg'] = 0
    aircraft_previouspoint[callsign]['lon_avg'] = 0

# process the data
data = {}
paths = list(Path('./data-flightradar24/{}/'.format(year)).rglob('*.json'))[:100]
for path in paths:
    #print(path)
    with open(path, 'r') as f:
        j = json.load(f)
    callsign = j['result']['response']['data']['flight']['aircraft']['identification']['registration']
    track = j['result']['response']['data']['flight']['track']
    if callsign not in data.keys():
        data[callsign] = {}
        data[callsign]['dates'] = []
        data[callsign]['lats'] = []
        data[callsign]['lons'] = []
    for point in track:
        date = datetime.fromtimestamp(point['timestamp'] - point['timestamp'] % 60)
        data[callsign]['dates'].append(date)
        data[callsign]['lats'].append(point['latitude'])
        data[callsign]['lons'].append(point['longitude'])

data_bydate = {}
for date in dates:
    year, month, day, hour, minute = date.year, date.month, date.day, date.hour, date.minute
    if year not in data_bydate.keys():
        data_bydate[year] = {}
    if month not in data_bydate[year].keys():
        data_bydate[year][month] = {}
    if day not in data_bydate[year][month].keys():
        data_bydate[year][month][day] = {}
    if hour not in data_bydate[year][month][day].keys():
        data_bydate[year][month][day][hour] = {}
    if minute not in data_bydate[year][month][day][hour].keys():
        data_bydate[year][month][day][hour][minute] = {}

num_points = 0
for callsign in data.keys():
    for date,(lat,lon) in zip(data[callsign]['dates'], zip(data[callsign]['lats'], data[callsign]['lons'])):
        year, month, day, hour, minute = date.year, date.month, date.day, date.hour, date.minute
        if callsign not in data_bydate[year][month][day][hour][minute].keys():
            data_bydate[year][month][day][hour][minute][callsign] = {}
            data_bydate[year][month][day][hour][minute][callsign]['lats'] = []
            data_bydate[year][month][day][hour][minute][callsign]['lons'] = []
        data_bydate[year][month][day][hour][minute][callsign]['lats'].append(lat)
        data_bydate[year][month][day][hour][minute][callsign]['lons'].append(lon)
        num_points += 1
print('Number of individual points:', num_points)

# plot the data
tiler = cimgt.GoogleTiles(style='satellite', cache=True)
fig = plt.figure(figsize=(6, 5), dpi=600)
ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator(central_longitude=0))
ax.set_extent([-180, -50, 5, 75], crs=ccrs.PlateCarree())
ax.add_image(tiler, 5, interpolation='spline36')


for date in dates:
    year, month, day, hour, minute = date.year, date.month, date.day, date.hour, date.minute
    date_atminute = data_bydate[year][month][day][hour][minute]
    if len(date_atminute) > 0:
        for callsign in date_atminute.keys():
            lat_avg = np.mean(date_atminute[callsign]['lats'])
            lon_avg = np.mean(date_atminute[callsign]['lons'])
            #print(date, callsign, lat_avg, lon_avg)

#for callsign in sorted(data.keys()):
            label = aircraft_models[callsign]
            color = aircraft_colors[label]
            #ax.scatter(data[callsign]['lons'], data[callsign]['lats'], color=color, s=0.1, transform=ccrs.PlateCarree())
            ax.plot([aircraft_previouspoint[callsign]['lon_avg'], lon_avg],
                    [aircraft_previouspoint[callsign]['lat_avg'], lat_avg],
                    color=color, lw=1, transform=ccrs.PlateCarree())

            aircraft_previouspoint[callsign]['lat_avg'] = lat_avg
            aircraft_previouspoint[callsign]['lon_avg'] = lon_avg

handles = [patches.Rectangle((0, 0), 5, 5, color=color) for color in aircraft_colors.values()]
plt.legend(handles=handles, labels=aircraft_colors.keys(), markerscale=25, framealpha=1, loc='upper right')
plt.tight_layout()
plt.savefig('map.png')
