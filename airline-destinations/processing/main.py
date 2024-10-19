
# data source: https://transtats.bts.gov/Fields.asp?gnoyr_VQ=FMG
# airport data from: https://openflights.org/data.php

import os, json

import pandas as pd
import matplotlib.pyplot as plt

import numpy as np
import cartopy
import cartopy.crs as ccrs
import matplotlib.cm as cm


fname_airports = '../data/lookups/airports-extended.dat'
airports = pd.read_csv(fname_airports, names=['AirportID', 'Name', 'City', 'Country', 'IATA', 'ICAO',
                                              'Latitude', 'Longitude', 'Altitude', 'Timezone', 'DST',
                                              'TzDatabaseTimezone', 'Type', 'Source'])

fname_L_AIRCRAFT_GROUP = '../data/lookups/L_AIRCRAFT_GROUP.csv'
fname_L_AIRCRAFT_TYPE = '../data/lookups/L_AIRCRAFT_TYPE.csv'
fname_L_AIRPORT_ID = '../data/lookups/L_AIRPORT_ID.csv'
fname_L_COUNTRY_CODE = '../data/lookups/L_COUNTRY_CODE.csv'
fname_L_UNIQUE_CARRIERS = '../data/lookups/L_UNIQUE_CARRIERS.csv'
L_AIRCRAFT_GROUP = pd.read_csv(fname_L_AIRCRAFT_GROUP)
L_AIRCRAFT_TYPE = pd.read_csv(fname_L_AIRCRAFT_TYPE)
L_AIRPORT_ID = pd.read_csv(fname_L_AIRPORT_ID)
L_COUNTRY_CODE = pd.read_csv(fname_L_COUNTRY_CODE)
L_UNIQUE_CARRIERS = pd.read_csv(fname_L_UNIQUE_CARRIERS, na_filter=False)  # don't filter, ("NA","North American Airlines")

T_T100 = pd.DataFrame()
start_year, end_year = 1990, 2023
for year in range(start_year, end_year + 1):  # T-100 data available for 1990 - Present
    fname_T_T100 = '../data/tables/T_T100_SEGMENT_ALL_CARRIER-{}.csv'.format(year)
    if os.path.isfile(fname_T_T100):
        print('loading data for the year ' + str(year))
        T_T100 = pd.concat([T_T100, pd.read_csv(fname_T_T100)])
    else:
        print('data not found for the year ' + str(year))

airline_counts = {}
airline_data = {}
airline_codes = L_UNIQUE_CARRIERS['Code']
airline_codes = ['UA', 'DL', 'AS', 'AA', 'WN']
for year in range(start_year, end_year + 1):
    print('counting for ' + str(year))
    year_data = {}
    for airline_code in airline_codes:
        #airline_name = L_UNIQUE_CARRIERS['Description'].loc[airline_codes == airline_code].values[0]
        #print('counting for ' + airline_name + ' during ' + str(year))
        airline_T_T100 = T_T100[(T_T100['YEAR'] == year) &
                                (T_T100['UNIQUE_CARRIER'] == airline_code) &
                                (T_T100['DEPARTURES_SCHEDULED'] > 0)]
        origins, destinations = airline_T_T100['ORIGIN'], airline_T_T100['DEST']
        route_pairs = []
        for origin,destination in pd.unique(pd.Series([(o, d) for o,d in zip(origins, destinations)])):
            if not (((origin, destination) in route_pairs) or ((destination, origin) in route_pairs)):
                route_pairs.append(origin + '-' + destination)
        airport_ids = pd.unique(pd.concat([origins, destinations]))
        airport_count = len(airport_ids)
        aircraft_types = pd.unique(airline_T_T100['AIRCRAFT_TYPE'])
        aircraft_count = len(aircraft_types)
        aircraft_groups = pd.unique(airline_T_T100['AIRCRAFT_GROUP'])
        aircraft_group = (6 in aircraft_groups) | (7 in aircraft_groups) | (8 in aircraft_groups)  # airline flies jets
        if (airport_count + aircraft_count) > 0:
            airline_counts[airline_code] = {'airport_count': airport_count, 'aircraft_count': aircraft_count, 'aircraft_group': aircraft_group}
            year_data[airline_code] = {}
            for airport_id in airport_ids:
                try:
                    lat = airports['Latitude'][airports['IATA'] == airport_id].values[0]
                    lon = airports['Longitude'][airports['IATA'] == airport_id].values[0]
                except:
                    print('unknown airport ID: ' + airport_id)
                    lat = 'NaN'
                    lon = 'NaN'
                year_data[airline_code][airport_id] = {'lat': lat, 'lon': lon}
                year_data[airline_code]['route_pairs'] = route_pairs
    airline_data[year] = year_data

airport_counts = [airline_counts[airline_code]['airport_count'] for airline_code in airline_counts.keys()]
aircraft_counts = [airline_counts[airline_code]['aircraft_count'] for airline_code in airline_counts.keys()]
aircraft_groups = [airline_counts[airline_code]['aircraft_group'] for airline_code in airline_counts.keys()]

with open('airline_data.json', 'w') as f:
    json.dump(airline_data, f)

print('plotting...')

# Airline Counts

plt.scatter([a for a,b in zip(aircraft_counts, aircraft_groups) if b], 
            [a for a,b in zip(airport_counts, aircraft_groups) if b], s=5, c='b', label='jets')
plt.scatter([a for a,b in zip(aircraft_counts, aircraft_groups) if not b], 
            [a for a,b in zip(airport_counts, aircraft_groups) if not b], s=5, c='r', label='no jets')
plt.legend()
plt.xticks(range(0, max(aircraft_counts) + 1))
plt.xlabel('# of Aircraft Types')
plt.ylabel('# of Airports Served')
plt.title('# of Airlines Included = {}'.format(len(airline_counts)))
plt.savefig('figure1.png')

# Airline Origins/Destinations

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

years = list(airline_data.keys())
colors = plt.colormaps['viridis'](np.linspace(0, 1, len(years)))
for year,color in zip(years, colors):
    year_data = airline_data[year]
    lats = [year_data[airline_code][airport_id]['lat'] for airline_code in year_data.keys() for airport_id in year_data[airline_code]]
    lons = [year_data[airline_code][airport_id]['lon'] for airline_code in year_data.keys() for airport_id in year_data[airline_code]]
    plt.scatter(lons, lats, transform=ccrs.PlateCarree(), color=color, s=5)
    
plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)

cbar = plt.colorbar(location='bottom', fraction=0.09, pad=0.00, aspect=50)
cbar.set_ticks(ticks=[0, 1], labels=[str(years[0]), str(years[-1])], color='w')
cbar.set_label(label='time', color='w')

plt.tight_layout()
plt.savefig('figure2.png', facecolor='black')
