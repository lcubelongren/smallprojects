
import numpy as np
import pandas as pd
import datetime
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.transforms import offset_copy

import cartopy.crs as ccrs
import cartopy.feature as cfeature

import shapely.geometry as sgeom


dates = np.array([str(day).replace('-', '').replace(':', '') for day in pd.period_range(start='2022-08-01', end='2023-08-01', freq='h')])

fig, ax = plt.subplots(1, 1, figsize=(8, 8), dpi=300, frameon=False,
                       subplot_kw={'projection': ccrs.SouthPolarStereo()})
fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
ax.axis('off')
#ax.set_extent([-180, 180, -90, -50], ccrs.PlateCarree())
ax.set_extent([-180, 180, -90, -53], ccrs.PlateCarree())

#ax.gridlines(ylocs=[-66.558], xlocs=[-90, 0, 90, 180], ylim=(-66.558, 0), color='k')

ax.add_feature(cfeature.NaturalEarthFeature('physical', 'ocean', '10m'), color='lightsteelblue', zorder=5)
ax.add_feature(cfeature.NaturalEarthFeature('physical', 'land', '10m'), color='ghostwhite', zorder=6)
ax.add_feature(cfeature.NaturalEarthFeature('physical', 'lakes', '10m'), color='lightsteelblue', zorder=7)
ax.add_feature(cfeature.NaturalEarthFeature('physical', 'rivers_lake_centerlines', '10m'), color='lightsteelblue', zorder=8)
ax.add_feature(cfeature.NaturalEarthFeature('physical', 'antarctic_ice_shelves_polys', '10m'), color=np.array([22, 114, 184])/255, zorder=9)

plt.savefig('antarctic_still_start1.png'); print('saved still')

"""FLIGHTS"""
# Manually determined coordinates for each destination
coordinates_dict = {
'60S': np.nan,
'60s': np.nan,
'AGAP SOUTH': (-84.500, 77.350),
'ALEXANDER TALL TOWER': (-78.996, 170.760),
'ALLAN HILLS': (-76.743, 159.045),
'ALLAN HILLS COLDEX': (-76.743, 159.045),
'ALLAN HILLS HIGGINS': (-76.741, 159.335),
'ALLAN HILLS- COLDEX': (-76.743, 159.045),
'ALLAN HILLS- HIGGINS': (-76.741, 159.335),
'ALLAN HILLS-COLDEX': (-76.743, 159.045),
'ALLEN HILLS HIGGINS': (-76.741, 159.335),
'ALLEN HILLS-COLDEX': (-76.743, 159.045),
'ALLEN HILLS-HIGGINS': (-76.741, 159.335),
'ASCENT GL': (-83.223, 156.557),
'BALLOON SITE': (-86.130, -101.458),  # SPIDER LDB
'BOX': np.nan,
'BOX 2 FUEL CACHE': (-75.036, -105.579), # copying CAVITY CAMP, 20230119
'CAMP A': np.nan,
'CAPE HALLETT':  (-72.440, 169.94),
'CAPE LANKESTER': (-79.248, 160.355),
'CAPE REYNOLDS':  (-75.469, 162.453),
'CAPE ROSS': np.nan,
'CASEY STATION': (-66.288, 110.779),
'CASEY-WILKINS STATION': (-66.690, 111.488),
'CAVITY CAMP': (-75.036, -105.579),
'CHANNEL CAMP': np.nan,
'CHRISTCHURCH': (-43.487, 172.532),
'COLDEX SITE': (-76.743, 159.045),
'COLDEX SITE 1': (-76.743, 159.045),
'COLDEX SITE 2': (-76.743, 159.045),
'COLDEX SITE 3': (-76.743, 159.045),
'CONCORDIA': (-75.102, 123.395),
'CP REYNOLDS': (-75.469, 162.453),
'CTAM': (-84.000, 164.500),
'DA11': np.nan,
'DARWIN GL': (-79.788, 158.636),
'DAVIS STATION': (-68.472, 78.823),
'DAVIS-WARD': (-85.670, 166.830),
'DECEPTION GL': (-78.517, 158.600),
'DISCOVERY DEEP': np.nan,
'DOME C': (-75.102, 123.395),
'DOTSON': np.nan,
'DOTSON 11.5': np.nan,
'DOTSON GPS1': np.nan,
'DUMONT': (-66.663, 140.001),
'DUMONT DURVILLE': (-66.663, 140.001),
'ELAINE AWS': (-83.094, 174.285),
'ELEPHANT MORAINE-1': (-76.283, 156.483),
'EMILIA AWS': (-78.426, 173.186),
'E09': np.nan,
'GABBRO HILLS': (-84.769, -170.810),
'GATEWAY': (-80.000, -169.888),
'GATEWAY FUEL CACHE': (-80.000, -169.888),
'GHOST': (-75.859, -106.741),
'GHOST CAMP': (-75.859, -106.741),
'GHOST DSPS': (-75.859, -106.741),
'GHOST DSPS CAMP': (-75.859, -106.741),
'GHOST LAKE': (-75.859, -106.741),
'GHOST LAKE 1': (-75.859, -106.741),
'GHOST LAKE 2': (-75.859, -106.741),
'GHOST RADAR TRAVERSE': (-75.036, -105.579),  # copying CAVITY CAMP, 20230105
'GHOST WEST': (-75.859, -106.741),
'GHOST WEST 1': (-75.859, -106.741),
'GHOST WEST 2': (-75.859, -106.741),
'HERC DOME': (-86.441, -107.227),
'HERC DOME WEST': (-85.801, -102.941),
'HERCULES DOME': (-86.441, -107.227),
'HERCULES DOME EAST': (-86.441, -107.227),
'HERCULES DOME NORTH': np.nan,
'HERCULES DOME SADDLE': (-86.088, -105.496),
'HERCULES DOME SOUTH': np.nan,
'HERCULES DOME WEST': (-85.801, -102.941),
'HOBART': (-42.881, 147.325),
'HOLLAND RANGE': (-82.937, 167.745),
'HUDSON MTNS': (-74.757, -99.363),
'JUNCTION SKIWAY': (-67.571, -68.123),  # ROTHERA (?), 20221113
'K865 SITE': np.nan,
'K865A SITE #1': np.nan,
'K865A SITE #2': np.nan,
'K865A SITE #5': np.nan,
'K865A SITE #6': np.nan,
'KAM ICE STREAM': (-82.771, -156.574),
'KAMB ICE STREAM': (-82.771, -156.574),
'KAMB ICE STREAM 2': (-82.771, -156.574),
'KIS': (-82.783, -155.329),
'LOWER THWAITES GL': (-76.458, -107.782),
'LTG': (-76.458, -107.782),
'LWR THWAITES GL': (-76.458, -107.782),
'MARGARET AWS': (-79.981, -165.099),
'MARILYN AWS': (-79.904, 165.774),
'MARIO ZUCCHELLI': (-74.660, 164.163),
'MARIO ZUCCHELLI STA': (-74.660, 164.163),
'MARIO ZUCCHELLI STAT': (-74.660, 164.163),
'MARIO ZUCCHELLI STATIO': (-74.660, 164.163),
'MARIO ZUCCHELLI STATION': (-74.660, 164.163),
'MARIO ZUCHELLI STA': (-74.660, 164.163),
'MARIO ZUCHELLI STATI': (-74.660, 164.163),
'MARIO ZUCHELLI STATION': (-74.660, 164.163),
'MELBOURNE': (-37.673, 144.843),
'MILLER SOUTH': (-83.126, 157.050),
'MT TUATARA': (-80.525, 158.707),
'MZS': (-74.719, 164.026),
'MZS BROWNING PASS': (-74.623, 163.916),
'NBY': (-80.018, -119.586),
'ODELL GLACIER': (-76.660, 159.952),
'PGO': np.nan,
'PHOENIX': (-77.937, 166.747),
'PHOENIX0235': (-77.937, 166.747),
'PSR': np.nan,
'PUERTO NATALES': (-51.670, -72.531),
'PUQ': np.nan,
'RD5': np.nan,
'rd12': np.nan,
'RIFT': (-79.063, -179.640),
'RIFT WR4': (-79.063, -179.640),
'RIFT WR4 1': (-79.063, -179.640),
'RIFT WR4 D21B': (-79.063, -179.640),
'RIFT WR4 D25S': (-79.063, -179.640),
'RIFT WR4 SITE': (-79.063, -179.640),
'RIFT WR4 SITE 1': (-79.063, -179.640),
'RIFT/SPOT-D33G': (-79.063, -179.640),
'RIS F/C': (-78.890, -179.834),
'RIS FUEL CACHE': (-78.890, -179.834),
'RIS/YESTERDAT F/C': (-78.890, -179.834),
'RIS/YESTERDAY': (-78.890, -179.834),
'ROAD END': (-79.774, 157.792),
'ROTHERA': (-67.571, -68.123),
'ROTHERA DELAYED': (-67.571, -68.123),
'SB9': np.nan,
'SCHWERDTFEGER AWS': (-79.875, 170.105),
'SHACKLETON GL': (-85.086, -175.289),
'SIPLE DOME': (-81.664, -149.018),
'SKY BLU': (-74.858, -71.573),
'SOUTH +200 FC': (-81.999, 178.421),
'SOUTH POLE': (-89.998, 139.273),
'SOUTH POLE ORBIT': (-89.998, 139.273),
'SOUTH POLE TRAVERSE': (-79.875, 170.105),  # copying SCHWERDTFEGER AWS, 20221205
'SPIDER LDB': (-86.130, -101.458),  # https://www.csbf.nasa.gov/map/balloon7/flight727N.htm
'SUPER TIGER II': (-71.126, 158.585),
'T': np.nan,
'T-1': np.nan,
'T1': np.nan,
'T2': (-76.476, -103.367),
'T2 E': np.nan,
'TANIWHA COVE': (-80.508, 160.843),
'TERRA NOVA BAY': (-74.692, 164.121),
'TIME': (-77.328, -100.058),
'TIME2': (-76.409, -103.486),
'TIME 2': (-76.409, -103.486),
'UNION GL': (-79.751, -82.776),
'UPPER THWAITES GL': (-77.582, -109.044),
'VITO AWS': (-78.408, 177.829),
'WAIS DIVIDE': (-79.483, -112.083),
'WILLIAMS FIELD': (-77.871, 167.024),
'WILLIAMS FIELD AWS': (-77.871, 167.024),
'WITH CASEY': np.nan,
'WR1': np.nan,
'YCAY': (-66.288, 110.779),
'ZHONGSHAN STATION': (-69.374, 76.372),
}

# locations to annotate, with values to rename and label offset
flight_annotations = {
'PHOENIX': ['McMurdo Station', (-100, -20)],
'UNION GL': ['Union Glacier', (25, 5)],
'MARIO ZUCCHELLI STA': ['Zucchelli Station', (15, 10)],
'ROTHERA': ['Rothera Station', (-75, -20)],
'SOUTH POLE': ['South Pole Station', (20, -25)],
'SKY BLU': ['Sky Blu', (-75, -20)],
'DUMONT DURVILLE': ["Dumont d'Urville Station", (0, -30)],
'CASEY STATION': ['Casey Station', (30, 10)],
'TANIWHA COVE': ['Taniwha Cove', (0, 25)],
'ROAD END': ['Road End', (20, 10)],
'ODELL GLACIER': ['Odell Glacier', (20, -10)],
'DAVIS STATION': ['Davis Station', (20, 10)],
'GATEWAY': ['Gateway', (-60, -40)],
'RIS/YESTERDAT F/C': ['RIS', (-40, -45)],
'DECEPTION GL': ['Deception Glacier', (15, 15)],
'CAPE LANKESTER': ['Cape Lankester', (-10, 30)],
'ALLAN HILLS HIGGINS': ['Allan Hills', (-80, -10)],
'MZS BROWNING PASS': ['Terra Nova Bay', (15, 10)],
'CAPE HALLETT': ['Cape Hallett', (-90, -35)],
'CP REYNOLDS': ['Cape Reynolds', (-110, -35)],
'ALEXANDER TALL TOWER': ['Alexander Tall Tower', (10, 45)],
'CONCORDIA': ['Concordia Station', (-25, 10)],
'DARWIN GL': ['Darwin Glacier', (-15, 40)],
'WAIS DIVIDE': ['WAIS Divide', (-48, 15)],
'SIPLE DOME': ['Siple Dome', (-30, -50)],
'LOWER THWAITES GL': ['Lower Thwaites Glacier', (-30, -100)],
'CAVITY CAMP': ['Cavity Camp', (-50, -70)],
'HERCULES DOME WEST': ['Hercules Dome', (0, 35)],
'HUDSON MTNS': ['Hudson Mtns', (-70, -30)],
'GHOST': ['GHOST', (-60, -20)],
'KAMB ICE STREAM 2': ['Kamb Ice Stream', (-80, -60)],
'SPIDER LDB': ['SPIDER LDB', (5, 30)],
'SUPER TIGER II': ['SUPER TIGER LDB', (0, 30)],
'HOLLAND RANGE': ['Holland Range', (70, 10)],
'ASCENT GL': ['Ascent Glacier', (25, 20)],
'SHACKLETON GL': ['Shackleton Glacier', (30, 30)],
'ZHONGSHAN STATION': ['Zhongshan Station', (20, 10)],
}

typecolor_dict = {
'A319': 'whitesmoke',
'B757': 'forestgreen',
'C17': 'grey',
'C-17': 'grey',
'C130': 'royalblue',
'LC-130': 'royalblue',
#'C-130': '',
#'C130J': '',
#'LC130': '',
'CL60': 'yellow',
'CL-60': 'yellow',
'DC3T': 'maroon',
'DC-3T': 'maroon',
'DHC6': 'crimson',
'DHC-6': 'crimson',
}

plane_names = np.array(['A319', 'B757', 'C17', 'C130', 'DHC6', 'DC3T', 'CL60'])

df_flights = pd.read_csv('df_flights.csv')
flights_date = np.array(df_flights['date']).astype(str)  # the day
flights_time = np.array(df_flights['time']).astype('uint16')  # the hour
flights_time -= flights_time % 100  # round to the lower hour
flights_time = flights_time // 100  # disregard the minutes
flights_flight = np.array(df_flights['flight'])
flights_plane = np.array(df_flights['plane'])
flights_position = np.array(df_flights['position'])

epoch = np.array([datetime.datetime.strptime(date, '%Y%m%d').timestamp() for date in flights_date])
flights_hour = (epoch / (60 * 60)) + flights_time
flights_hour -= flights_hour.min()
flights_hour = np.array(flights_hour).astype(int)  # hours from the start of the dataset
flights_hour -= flights_hour[np.where(flights_date == '20220817')[0][0]] - 399  # make 20220801 hour 0

flights_idxs = np.where((0 <= flights_hour) & (flights_hour < 24*365))[0]
total_flights = len(np.unique(flights_flight[flights_idxs]))

flights_hour = flights_hour[flights_idxs]
flights_date = flights_date[flights_idxs]
flights_time = flights_time[flights_idxs]
flights_flight = flights_flight[flights_idxs]

flights_flight -= np.min(flights_flight)
flights_plane = flights_plane[flights_idxs]
flights_position = flights_position[flights_idxs]

flights_by_date = [[] for _ in dates]
for i,flight in enumerate(flights_flight):
    idxs = np.where(flights_flight == flight)[0]
    for idx in np.arange(flights_hour[idxs[0]], flights_hour[idxs[-1]] + 2) + 1:  # add two for removal frame
        if flight not in flights_by_date[idx]:
            flights_by_date[idx].append(flight)

flights_memory = np.zeros((2, len(np.unique(flights_flight))), dtype=int)  # progress, progress_max
for flights in flights_by_date:
    for flight in flights:
        flights_memory[:,flight] += 1
flights_memory -= 1

planes_on_continent = np.zeros(len(plane_names), dtype=int)

location_labels = []
location_fuses = np.zeros(len(flight_annotations))

def animate_flights(i, f_hist, f_ln, f_points, f_annotations):
    flights = flights_by_date[i]
    for flight in flights:
        
        lat_lons = [coordinates_dict[position] for position in flights_position[flights_flight == flight]]
        lats, lons = np.transpose([ll for ll in lat_lons if type(ll) == tuple])
        lats = np.append([lats[j] for j in range(len(lats)-1) if lats[j] != lats[j+1]], lats[-1])
        lons = np.append([lons[j] for j in range(len(lons)-1) if lons[j] != lons[j+1]], lons[-1])
        if len(lats) < 2:
            continue
        
        flight_idx = flight - np.min(flights_flight) 
       
        progress, progress_max = flights_memory[:,flight_idx]
        if progress == 0:
            f_points[flight_idx].set_data([], [])
            f_ln[flight_idx].set_data([], [])
            f_hist[flight_idx].set_linewidth(1)
            f_hist[flight_idx].set_linestyle('-')
            continue
        flights_memory[0,flight_idx] -= 1
        
        plane_type = flights_plane[flights_flight == flight][0]
        if (plane_type == 'C-130') or (plane_type == 'C130J') or (plane_type == 'LC130'):
            plane_type = 'C130'
        if plane_type == 'DHC-6':
            plane_type = 'DHC6'
     
        if progress == progress_max:  # first hour of a flight
            if np.min(lats) < -60:  # intercontinental flight
                if (lats[0] > -60) and (lats[-1] > -60):  # there-and-back
                    pass
                elif (lats[0] > -60) and (lats[-1] < -60):  # final destination on-continent
                    planes_on_continent[plane_names == plane_type] += 1
                elif (lats[0] < -60) and (lats[-1] > -60):  # final destination off-continent
                    planes_on_continent[plane_names == plane_type] -= 1
                    
        for position in flights_position[flights_flight == flight]:  # add labels to new locations
            if type(coordinates_dict[position]) == tuple:
                if position in flight_annotations.keys():
                    if position not in location_labels:
                        print('adding:', position)
                        location_lat, location_lon = coordinates_dict[position]
                        annotation_idx = [idx for idx,key in enumerate(flight_annotations.keys()) if key == position][0]
                        f_annotations[annotation_idx].xy = (location_lon, location_lat)
                        f_annotations[annotation_idx].set_position((list(flight_annotations.values())[annotation_idx][1][0],
                                                                    list(flight_annotations.values())[annotation_idx][1][1]))
                        location_fuses[annotation_idx] = i + int(24*7)
                        location_labels.append(position)
        
        #print(flights_position[flights_flight == flight])
        
        input_line = sgeom.LineString(np.transpose([lons, lats]))
        projected_line = ccrs.AzimuthalEquidistant(0, -90).project_geometry(input_line, ccrs.Geodetic())
        if isinstance(projected_line, sgeom.MultiLineString):
            projected_line = projected_line.geoms[0]
        
        verts = np.array([projected_line.interpolate(distance, normalized=True).xy for distance in np.linspace(0, 1, progress_max)])[:,:,0]
        #ln_hist_verts = np.array(projected_line.coords)
        
        # ensure the line goes all the way to the destinations
        transform = ccrs.AzimuthalEquidistant(0, -90).transform_points(ccrs.Geodetic(), lons, lats)
        true_lats, true_lons = np.transpose(transform)[:2]
        for lat,lon in zip(true_lats, true_lons):
            if not ((lat in verts[:,0]) and (lon in verts[:,1])):
                nearest_idx = np.argmin(abs(verts[:,0] - lat))
                verts[nearest_idx,0] = lat
                verts[nearest_idx,1] = lon
                
        f_hist[flight_idx].set_data([true_lats], [true_lons])
        
        j = int(progress_max - progress)
        f_points[flight_idx].set_data([verts[j, 0]], [verts[j, 1]])
        f_ln[flight_idx].set_data([verts[:j+1, 0]], [verts[:j+1, 1]])
        #f_hist[flight_idx].set_data([verts[:j+1, 0]], [verts[:j+1, 1]])
        
        plane_color = typecolor_dict[plane_type]
        f_ln[flight_idx].set_color(plane_color)
        f_points[flight_idx].set_color(plane_color)

        magnitude = flight % 5 - 2.5  # kindof random offset
        trans_offset = offset_copy(ax.transData, fig=fig, x=magnitude, y=magnitude, units='dots')
        f_ln[flight_idx].set_transform(trans_offset)
        f_points[flight_idx].set_transform(trans_offset)


    for j in range(len(location_fuses)):  # remove old labels
        if location_fuses[j] == i:
            print('removing:', list(coordinates_dict.keys())[j])
            f_annotations[j].set_position((0, 0))
            f_annotations[j].xy = (0, 0)

    # for name,number in zip(plane_names, planes_on_continent):
        # print(name, number)
        
    combination_flights = np.append(np.append(np.append([h for h in f_hist], [ln for ln in f_ln]), 
                                                        [p for p in f_points]), [a for a in f_annotations])
    return combination_flights

display_plane_names = np.array(['A319', 'B757', 'C-17', 'LC-130', 'DHC-6', 'DC-3T', 'CL-60'])
plane_handles = []
for key in display_plane_names[::-1]:
    plane_legend, = ax.plot([], label=key, color=typecolor_dict[key], marker='o')
    plane_handles = np.append(plane_legend, plane_handles)
plane_handles = list(plane_handles)   
plane_legend = ax.legend(handles=plane_handles, frameon=False, ncol=1,
                         loc='center left', bbox_to_anchor=(0.01, 0.350), alignment='left', fontsize='large',
                         title='planes', title_fontproperties={'weight': 'bold', 'size': 'large'})
plane_legend.set_zorder(75)
ax.add_artist(plane_legend)  

f_hist = ax.plot(np.empty((0, total_flights)), 
                 np.empty((0, total_flights)),
                 transform=ccrs.AzimuthalEquidistant(0, -90), zorder=10, animated=True, lw=0, marker='o', markersize=3, c='k')
                 
f_ln = ax.plot(np.empty((0, total_flights)), 
               np.empty((0, total_flights)), 
               transform=ccrs.AzimuthalEquidistant(0, -90), zorder=50, animated=True, lw=3)
                  
f_points = ax.plot(np.empty((0, total_flights)), 
                   np.empty((0, total_flights)), 
                   transform=ccrs.AzimuthalEquidistant(0, -90), zorder=100, animated=True, marker='o', markersize=6)

f_annotations = [ax.annotate('{}'.format(list(flight_annotations.values())[i][0]), xy=(0, 0), xytext=(0, 0), 
                             xycoords=ccrs.PlateCarree()._as_mpl_transform(ax), textcoords='offset points', zorder=101, animated=True,
                             arrowprops=dict(arrowstyle='-|>', fc='ghostwhite', shrinkB=5, lw=1)) for i in range(len(flight_annotations))]


"""VESSELS"""
#df_vessels = pd.read_csv('df_vessels.csv')
with open('vessel_tracks.npy', 'rb') as f:
    vessel_tracks = np.load(f)
with open('vessel_tracks_interp.npy', 'rb') as f:
    vessel_tracks_interp = np.load(f)

# annotation coordinates and text offset
vessel_annotations = {
'Palmer Station': [(-64.8, -64.1), (15, 15)],
'South Georgia': [(-53.9, 321.7), (-40, 20)]
}
vessel_location_fuses = np.zeros(len(vessel_annotations))

vessel_colors = ['sandybrown', 'slateblue']

def animate_vessels(i, v_hist, v_points, v_annotations, v_annotations_hist):
    
    for j in range(vessel_tracks.shape[0]):
        vessel_lat = vessel_tracks_interp[j,i,0]
        vessel_lon = vessel_tracks_interp[j,i,1]

        v_points[j].set_data([vessel_lat], [vessel_lon])
        v_hist[j].set_data(vessel_tracks_interp[j,:i,0], vessel_tracks_interp[j,:i,1])
        
        heading = (vessel_tracks_interp[j,i,2] + 1) * 36  # if DS, 0 - 9
        v_points[j].set_marker((3, 0, heading))
        
        v_points[j].set_color(vessel_colors[j])
        
        original_lat, original_lon = vessel_tracks[j,i,0], vessel_tracks[j,i,1]
        for k,lat_lon in enumerate([list(vessel_annotations.values())[av][0] for av in range(len(vessel_annotations))]):
            position = list(vessel_annotations.keys())[k]
            if position not in location_labels:
                location_lon, location_lat = lat_lon[1], lat_lon[0]
                #print(original_lat, location_lat, original_lon, location_lon)
                if (original_lat == location_lat) and ((original_lon == location_lon) or (original_lon == location_lon+360)):
                    print('adding:', position)
                    v_annotations[k].xy = (location_lon, location_lat)
                    v_annotations[k].set_position((list(vessel_annotations.values())[k][1][0],
                                                   list(vessel_annotations.values())[k][1][1]))
                    vessel_location_fuses[k] = i + int(24*7)
                    location_labels.append(position)
                    v_annotations_hist[k].set_data([vessel_lat], [vessel_lon])

    for j in range(len(vessel_location_fuses)):  # remove old labels
        if vessel_location_fuses[j] == i:
            print('removing:', list(vessel_annotations.keys())[j])
            v_annotations[j].set_position((0, 0))
            v_annotations[j].xy = (0, 0)

    combination_vessels = np.append(np.append(np.append([p for p in v_points], [h for h in v_hist]), 
                                                        [a for a in v_annotations]), [ah for ah in v_annotations_hist])
    return combination_vessels
    
vessel_handles = []
for key,color in zip(['N.B. Palmer', 'L.M. Gould'], vessel_colors):
    vessel_legend, = ax.plot([], label=key, color=color, marker='>')
    vessel_handles = np.append(vessel_legend, vessel_handles)
vessel_handles = list(vessel_handles)   
vessel_legend = ax.legend(handles=vessel_handles, frameon=False, ncols=1,
                          loc='center left', bbox_to_anchor=(0.01, 0.175), alignment='left', fontsize='large',
                          title='vessels', title_fontproperties={'weight': 'bold', 'size': 'large'})
vessel_legend.set_zorder(75)
ax.add_artist(vessel_legend)

v_hist = ax.plot(np.empty((0, vessel_tracks.shape[0])), 
                 np.empty((0, vessel_tracks.shape[0])),
                 transform=ccrs.AzimuthalEquidistant(0, -90), zorder=10, animated=True, c='k', lw=1.5, ls=(0, (1, 0.5)))  
           
v_points = ax.plot(np.empty((0, vessel_tracks.shape[0])),
                   np.empty((0, vessel_tracks.shape[0])),
                   transform=ccrs.AzimuthalEquidistant(0, -90), zorder=100, animated=True, marker='o', markersize=12)

v_annotations = [ax.annotate('{}'.format(list(vessel_annotations.keys())[i]), xy=(0, 0), xytext=(0, 0), 
                             xycoords=ccrs.PlateCarree()._as_mpl_transform(ax), textcoords='offset points', zorder=101, animated=True, 
                             arrowprops=dict(arrowstyle='-|>', fc='ghostwhite', shrinkB=5, lw=1)) for i in range(len(vessel_annotations))]
                             
v_annotations_hist = ax.plot(np.empty((0, len(vessel_annotations))),
                             np.empty((0, len(vessel_annotations))),
                             transform=ccrs.AzimuthalEquidistant(0, -90), zorder=10, animated=True, lw=0, marker='o', markersize=3, c='k')


"""SPOT"""
spot_route = {
'McMurdo Station': (-77.8, 166.7),
'Waypoint 1': (-78.5, 170.0),   # turn from McM
'Waypoint 2': (-82.0, 179.0),   # WISSARD Fuel Cache
'Waypoint 3': (-84.3, 190.0),  # turn to WISSARD Camp 20
'Waypoint 4': (-84.4, 197.0),  # WISSARD Camp 20
'Waypoint 5': (-84.7, 198.0),  # turn from WISSARD Camp 20
'Waypoint 6': (-85.5, 210.0),  # follow inlet
'Waypoint 7': (-86.5, 220.0),  # turn towards Pole
'South Pole': (-90.0, 220.0),
}
spot1_dates = {
'departMcM': '10 Nov 22',
'arrivePole': '09 Dec 22',
'departPole': '16 Dec 22',
'arriveMcM': '30 Dec 22',
}
spot2_dates = {
'departMcM': '29 Nov 22',
'arrivePole': '23 Dec 22',
'departPole': '10 Jan 23',
'arriveMcM': '30 Jan 23',
}
spot3_dates = {
'departMcM': '17 Jan 23',
'arrivePole': '12 Feb 23',
'departPole': '16 Feb 23',
'arriveMcM': '07 Mar 23',
}

spot_route_vectors = np.array(list(spot_route.values())).T
spot_route_lats, spot_route_lons = spot_route_vectors.copy()

distances = (np.diff(spot_route_vectors)[0] * -10).astype(int) + 1

spot_route_lons_interp, spot_route_lats_interp = np.array([]), np.array([])
for i,dist in enumerate(distances):
    spot_route_lons_interp = np.append(spot_route_lons_interp, np.linspace(spot_route_lons[i], spot_route_lons[i+1], dist))
    spot_route_lats_interp = np.append(spot_route_lats_interp, np.linspace(spot_route_lats[i], spot_route_lats[i+1], dist))
spot_route_interp = np.array([spot_route_lons_interp, spot_route_lats_interp])

spot1_days = np.array([time.strptime(date_str, '%d %b %y').tm_yday for date_str in list(spot1_dates.values())])
spot2_days = np.array([time.strptime(date_str, '%d %b %y').tm_yday for date_str in list(spot2_dates.values())])
spot3_days = np.array([time.strptime(date_str, '%d %b %y').tm_yday for date_str in list(spot3_dates.values())])
spot1_days = np.where(spot1_days < 180, spot1_days + 365, spot1_days)
spot2_days = np.where(spot2_days < 180, spot2_days + 365, spot2_days)
spot3_days = np.where(spot3_days < 180, spot3_days + 365, spot3_days)

spot_line = sgeom.LineString(np.transpose([spot_route_lons, spot_route_lats]))
spot_projected_line = ccrs.AzimuthalEquidistant(0, -90).project_geometry(spot_line, ccrs.Geodetic())
if isinstance(spot_projected_line, sgeom.MultiLineString):
    spot_projected_line = spot_projected_line.geoms[0]
spot_route_interp = np.transpose([spot_projected_line.interpolate(distance, normalized=True).xy for distance in np.linspace(0, 1, 100)])[0]

def spot_track(ln, day, spot_days, spot_route_interp, color):
    day = time.strptime(day, '%Y%m%d %M%S').tm_yday
    if day < 213:  # rollover to 2023, Julian day for Aug 1st
        day += 365
    day_num1 = int(spot_days[1] - spot_days[0])
    interval1 = spot_route_interp.shape[1] // day_num1 + 1
    if (day >= spot_days[0]) and (day <= spot_days[1]):
        lons, lats = spot_route_interp[:,::interval1][:,:day-spot_days[0]]
        ln.set_data(lons, lats)
    day_num2 = int(spot_days[3] - spot_days[2])
    interval2 = spot_route_interp.shape[1] // day_num2 + 1
    if (day >= spot_days[2]) and (day <= spot_days[3]):
        lons, lats = spot_route_interp[:,::-interval2][:,:day-spot_days[2]]
        ln.set_data(lons, lats)
    if ((day > spot_days[1]) and (day < spot_days[2])) or (day > spot_days[3]):
        ln.set_color('k')
        ln.set_marker('')
    else:
        ln.set_color(color)
        ln.set_marker('s')
    return ln

def animate_spots(i, s_ln1, s_ln2, s_ln3):
    
    date = dates[i]
        
    s_ln1 = spot_track(s_ln1, date, spot1_days, spot_route_interp, 'darkturquoise')
    s_ln2 = spot_track(s_ln2, date, spot2_days, spot_route_interp, 'darkturquoise')
    s_ln3 = spot_track(s_ln3, date, spot3_days, spot_route_interp, 'darkturquoise')
    
    magnitude = 4
    s_ln2.set_transform(offset_copy(ax.transData, fig=fig, x=+magnitude, y=+magnitude, units='dots'))
    s_ln3.set_transform(offset_copy(ax.transData, fig=fig, x=-magnitude, y=-magnitude, units='dots'))
    
    combination_spots = [s_ln1, s_ln2, s_ln3]
    return combination_spots

spot_handles = []
for key,color in zip(['South Pole (SPOT)'], ['darkturquoise']):
    spot_legend, = ax.plot([], label=key, color=color, marker='s')
    spot_handles = np.append(spot_legend, spot_handles)
spot_handles = list(spot_handles)   
spot_legend = ax.legend(handles=spot_handles, frameon=False, ncols=1,
                        loc='center left', bbox_to_anchor=(0.01, 0.090), alignment='left', fontsize='large',
                        title='traverse', title_fontproperties={'weight': 'bold', 'size': 'large'})
spot_legend.set_zorder(75)
ax.add_artist(spot_legend)

s_ln1, = ax.plot([], [], transform=ccrs.AzimuthalEquidistant(0, -90), lw=3, marker='s', markevery=[0, -1], markersize=6, zorder=21)
s_ln2, = ax.plot([], [], transform=ccrs.AzimuthalEquidistant(0, -90), lw=3, marker='s', markevery=[0, -1], markersize=6, zorder=22)
s_ln3, = ax.plot([], [], transform=ccrs.AzimuthalEquidistant(0, -90), lw=3, marker='s', markevery=[0, -1], markersize=6, zorder=23)


"""MISC"""
highlight_points = {
'01': [(-53.167, -70.933), np.arange(60, 180, 1)],  # Punta Arenas, Chile
'91': [(-64.8, -64.1), np.arange(180, 300, 1)],  # Palmer
'02': ['PHOENIX', np.arange(300, 1380, 1)],
'03': [(-64.8, -64.1), np.arange(1380, 1860, 1)],  # Palmer
'92': ['SIPLE DOME', np.arange(1860, 1980, 1)],
'93': ['SOUTH POLE', np.arange(1980, 2100, 1)],
'94': ['PHOENIX', np.arange(2100, 2580, 1)],
'95': [(-82.0, 179.0), np.arange(2580, 2760, 1)],  # WISSARD Fuel Cache
'96': ['SOUTH POLE', np.arange(2760, 3140, 1)],
'05': ['WAIS DIVIDE', np.arange(3140, 3380, 1)],
'06': [(-64.8, -64.1), np.arange(3380, 3620, 1)],  # Palmer
'07': ['PHOENIX', np.arange(3620, 3800, 1)],
'08': ['ROTHERA', np.arange(3800, 3920, 1)],
'09': ['MARIO ZUCCHELLI', np.arange(3920, 4040, 1)],
'10': ['CONCORDIA', np.arange(4040, 4160, 1)],
'11': ['DUMONT DURVILLE', np.arange(4160, 4280, 1)],
'12': ['CASEY STATION', np.arange(4280, 4400, 1)],
'13': ['DAVIS STATION', np.arange(4400, 4520, 1)],
'14': ['PHOENIX', np.arange(4520, 5240, 1)],
'15': ['SPIDER LDB', np.arange(5240, 5720, 1)],
'16': ['ZHONGSHAN STATION', np.arange(5720, 5900, 1)],
'17': ['PHOENIX', np.arange(5900, 6140, 1)],
'18': [(-64.8, -64.1), np.arange(6140, 6320, 1)],  # Palmer
'19': ['SOUTH POLE', np.arange(6320, 6500, 1)],
'97': [(-57, 172), np.arange(6500, 6680, 1)],  # between CHC & Phoenix
'20': ['PHOENIX', np.arange(6680, 7040, 1)],
'21': [(-64.8, -64.1), np.arange(7040, 7220, 1)],  # Palmer
'22': ['PHOENIX', np.arange(7220, 7580, 1)],
'23': ['SOUTH POLE', np.arange(7580, 7760, 1)],
'24': [(-64.8, -64.1), np.arange(7760, 7880, 1)],  # Palmer
'25': ['SOUTH POLE', np.arange(7880, 8000, 1)],
'26': ['PHOENIX', np.arange(8000, 8240, 1)],
'27': [(-54.283, -36.495), np.arange(8240, 8600, 1)],  # South Georgia
}

def add_highlight(i, h_points):
    
    locations = np.array(list(highlight_points.values()), dtype=object)[:,0]
    idxs  = np.array(list(highlight_points.values()),  dtype=object)[:,1]
    for h in range(len(highlight_points)):
        if i in idxs[h]:
            print('add highlight:', locations[h])
            if type(locations[h]) == str:
                lat, lon = coordinates_dict[locations[h]]
            else:
                lat, lon = locations[h]
            tlon, tlat = ccrs.AzimuthalEquidistant(0, -90).transform_point(lon, lat, ccrs.Geodetic())
            h_points[1][h].set_data([tlon], [tlat])
            h_points[0][h].set_data([tlon], [tlat])
        else:
            h_points[1][h].set_data([], [])
            h_points[0][h].set_data([], [])
            
    return h_points

h_points = [ax.plot(np.empty((0, len(highlight_points))),
                    np.empty((0, len(highlight_points))),
                    transform=ccrs.AzimuthalEquidistant(0, -90), zorder=1000, animated=True, 
                    marker='o', markersize=15, markeredgewidth=2.0, markerfacecolor=(1, 1, 1, 0), markeredgecolor='k'),
            ax.plot(np.empty((0, len(highlight_points))),
                    np.empty((0, len(highlight_points))),
                    transform=ccrs.AzimuthalEquidistant(0, -90), zorder=1000, animated=True, 
                    marker='o', markersize=13, markeredgewidth=1.0, markerfacecolor=(1, 1, 1, 0), markeredgecolor='w')]


"""combined animation"""
print('plotting animation...')

def animate(i, f_hist, f_ln, f_points, f_annotations,
               v_hist, v_points, v_annotations, v_annotations_hist,
               s_ln1, s_ln2, s_ln3,
               h_points):

    #i += 390
    #i += 1550
    #i += 2015
    #i += 2350
    #i += 3500
    #i += 4500
    #i += 5400
    #i += 6620
    #i += 8000
    #i += 8200
    #i += 8755
    print('frame', i + 1, dates[i])
        
    combination_flights = []
    combination_vessels = []
    combination_spots = []
        
    combination_flights = animate_flights(i, f_hist, f_ln, f_points, f_annotations)
    combination_vessels = animate_vessels(i, v_hist, v_points, v_annotations, v_annotations_hist)
    combination_spots = animate_spots(i, s_ln1, s_ln2, s_ln3)
    
    highlight = add_highlight(i, h_points)

    ttl.set_text(datetime.datetime.strptime(dates[i], '%Y%m%d %M%S').strftime('%Y %b %d @ %M:00'))
    #ttl.set_text(datetime.datetime.strptime(dates[i], '%Y%m%d %M%S').strftime('%Y %b %d @ %M:00') + ' ' + str(i))

    combination = np.append(np.append(np.append(np.append([ttl], combination_flights), combination_vessels), combination_spots), highlight)
    return combination
        
ttl = ax.text(0.02, 0.02, '', transform=ax.transAxes, fontsize='x-large')
ttl.set_zorder(75)

plt.savefig('antarctic_still_start2.png'); print('saved still')

ts = np.arange(len(dates))
ani = animation.FuncAnimation(fig, animate, frames=ts, blit=True,
                              fargs=(f_hist, f_ln, f_points, f_annotations,
                                     v_hist, v_points, v_annotations, v_annotations_hist,
                                     s_ln1, s_ln2, s_ln3,
                                     h_points),
                              repeat=False, interval=83.333)  # 12fps
#plt.show()
                    
print('saving animation...');  ani.save('antarctic movements.mp4')

ttl.set_text('')
plane_legend.remove()
vessel_legend.remove()
spot_legend.set_zorder(0)
[v_points[j].set_data([], []) for j in range(len(v_points))]
[s_ln.set_color('k') for s_ln in [s_ln1, s_ln2, s_ln3]]
[s_ln.set_marker('') for s_ln in [s_ln1, s_ln2, s_ln3]]
plt.savefig('antarctic_still_end.png'); print('saved still')