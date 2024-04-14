
import numpy as np
import pandas as pd
import datetime
import time


"""FLIGHTS"""
from bs4 import BeautifulSoup
from pathlib import Path

def ScrapeFlights():
    flight, previous_flight = 0, 0
    df_flights = pd.DataFrame(columns=['flight', 'date', 'time', 'plane', 'position'])
    for html in Path('./data/flights/').rglob('*.html'):
        print(html)

        soup = BeautifulSoup(open(html).read(), 'html.parser')
        
        text = str(soup.find_all('pre')[0].string)
        text_rows = [tr.split() for tr in text.split('\n')]

        
        breaks = [i for i,row in enumerate(text_rows) if len(row) == 0]
        blocks = [np.arange(breaks[i]+1, breaks[i+1]) for i in range(len(breaks)-1)]

        for b,block in enumerate(blocks):
            date = datetime.datetime.strptime(''.join(text_rows[4]), '%d%b%Y')
            time, previous_time = '0000', '0000'
            for r,row in enumerate(block):
                line = np.array(text_rows[row])
                # remove non-flight text
                if row == 4:  # skip date
                    flight = previous_flight
                    continue
                if len(line) == 1:  # INTERCONTINENTAL, INTRACONTINENTAL, and dashes
                    flight = previous_flight
                    continue
                elif list(line) == ['NO', 'FLIGHTS', 'SCHEDULED']:
                    flight = previous_flight
                    continue
                else:  # consider flight text
                    if line[0] not in ['DEPARTED', 'ESTIMATING', 'ARRIVED'] and 'ETD' in line:
                        plane = line[np.where(line == 'ETD')[0][0] - 1]
                        flight += 1
                    else:
                        time_cols = [col.isdigit() if len(col) == 4 else False for col in line]
                        if np.any(time_cols):  # disregard lines without times
                            time = line[time_cols][0]  # 0 idx incorrect for a single 2019 flight
                            position = ' '.join(line[1:np.where(line == time)[0][0]])
                            
                            if (time < previous_time) and (int(previous_time) - int(time) > 1200):  # overnight flight
                                date += datetime.timedelta(days=1)
                            previous_time = time
                            
                            if len(df_flights) > 0:  # check for incorrect flight number
                                next_flight = list(df_flights['flight'])[-1] + 1
                                if flight > next_flight:
                                    flight = next_flight
                            
                            df_new = pd.DataFrame({'flight': flight, 'date': date.strftime('%Y%m%d'), 
                                                   'time': time, 'plane': plane, 'position': position}, index=[0])
                            df_flights = pd.concat([df_flights, df_new], ignore_index=True)
                            previous_flight = flight
    return df_flights

#df_flights = ScrapeFlights()
#print(df_flights.to_string())
#df_flights.to_csv('df_flights.csv')


"""VESSELS"""
import IMMA
import cartopy.crs as ccrs

def ScrapeVessels():
    #fname = 'ICOADS_R3.0_Rqst626893_20220101-20230228.csv'
    #fname = 'ICOADS_R3.0_Rqst666659_20220801-20230630.csv'
    fname = 'ICOADS_R3.0_Rqst669936_20220801-20230731.csv'
    data = pd.read_csv('data/vessels/' + fname)

    callsigns = [
    'WBP3210',  # Nathaniel B. Palmer
    'WCX7445',  # Lawrence M. Gould
    #'KOGC',     # Ocean Gladiator
    #'WDG4379',  # Ocean Giant
    #'WAGB 10',  # Polar Star
    #'PBXF',     # Happy Delta
    ]
    
    fmtDate = lambda x: '{:.0f}'.format(x) if len(str(int(x))) > 1 \
                                           else '0{:.0f}'.format(x)
    
    
    df_vessels = pd.DataFrame(columns=['date', 'time', 'ID', 'LAT', 'LON', 'DS'])
    idxs = [idx for idx in range(len(data['ID'])) if data['ID'][idx] in callsigns]
    for idx in idxs:
    
        yr, mo, dy, hr = int(data['YR'][idx]), fmtDate(data['MO'][idx]), \
                         fmtDate(data['DY'][idx]), fmtDate(data['HR'][idx])
    
        date = str(yr) + str(mo) + str(dy)
        hour = str(hr) + '00'
    
        df_new = pd.DataFrame({'date': date, 'time': hour,
                               'ID': data['ID'][idx], 'LAT': data['LAT'][idx], 'LON': data['LON'][idx], 'DS': data['DS'][idx]}, index=[0])
        df_vessels = pd.concat([df_vessels, df_new], ignore_index=True)
            
    drop_list = []
    for ID in np.unique(df_vessels['ID']):  # remove outliers
        day = datetime.datetime.strptime(df_vessels['date'][idxs[0]], '%Y%m%d')
        lat, lon = df_vessels['LAT'][idxs[0]], df_vessels['LON'][idxs[0]]
        idxs = np.where(df_vessels['ID'] == ID)[0]
        for idx in idxs[1:]:
            long_pause = abs(datetime.datetime.strptime(df_vessels['date'][idx], '%Y%m%d') - day) > datetime.timedelta(days=2)
            far_away = (abs(lat - df_vessels['LAT'][idx]) > 0.5) or (abs(lon - df_vessels['LON'][idx]) > 0.5)
            if long_pause or not far_away:
                day = datetime.datetime.strptime(df_vessels['date'][idx], '%Y%m%d')
                lat, lon = df_vessels['LAT'][idx], df_vessels['LON'][idx]
            else:
                drop_list.append(idx)
    df_vessels = df_vessels.drop(drop_list)
    
    dates = np.array([str(day).replace('-', '').replace(':', '') for day in pd.period_range(start='2022-08-01', end='2023-08-01', freq='h')])
    
    vessel_IDs = np.unique(df_vessels['ID'])
    vessel_tracks = np.full((len(vessel_IDs), len(dates), 3), np.nan)
    for i,ID in enumerate(vessel_IDs):
        df_temp = df_vessels[df_vessels['ID'] == ID]
        for k,(d,t) in enumerate(zip(df_temp['date'], df_temp['time'])):
            date_idxs = np.where(dates == str(d) + ' ' + str(t))[0]
            for j in date_idxs:
                vessel_tracks[i,j,0] = list(df_temp['LAT'])[k]
                vessel_tracks[i,j,1] = list(df_temp['LON'])[k]
                vessel_tracks[i,j,2] = list(df_temp['DS'])[k]
            
    vessel_tracks_interp = vessel_tracks.copy()
    
    # manually cut out incorrect interpolations
    vessel_tracks_interp[0,:3000,:] = np.nan
    #vessel_tracks_interp[1,3750:4575,:] = np.nan
    
    # manually add necessary missing cruises
    vessel_tracks_interp[0,2376:2548,:] = vessel_tracks_interp[1,1488:1660,:]  # initial PAL cruise
    vessel_tracks_interp[0,2549:2621,:] = vessel_tracks_interp[1,1660-1,:]  # staying in PAL until departure
    vessel_tracks_interp[0,2621+150:2621+450,:] = vessel_tracks_interp[0,7620-300:7620,:][::-1]  # artificially keep route to NZ closer to continent
    
    for i in range(vessel_tracks.shape[0]):
        for k in range(vessel_tracks.shape[2]):
            y = vessel_tracks_interp[i,:,k]
            nans, x = np.isnan(y), lambda z: z.nonzero()[0]
            y[nans] = np.interp(x(nans), x(~nans), y[~nans])
            vessel_tracks_interp[i,:,k] = y
            
        # error_idxs = np.where(np.logical_or(np.abs(np.diff(vessel_tracks_interp[i,:,0])) > 5, 
                                            # np.abs(np.diff(vessel_tracks_interp[i,:,1])) > 5))[0]
        # vessel_tracks_interp[i,error_idxs,0] = np.nan
        # vessel_tracks_interp[i,error_idxs,1] = np.nan
        
        # plt.figure()
        # plt.plot(vessel_tracks_interp[i,:,0])
        # plt.plot(vessel_tracks_interp[i,:,1])
        # plt.show()
        
        # for k in range(vessel_tracks.shape[2]):
            # y = vessel_tracks_interp[i,:,k]
            # nans, x = np.isnan(y), lambda z: z.nonzero()[0]
            # y[nans] = np.interp(x(nans), x(~nans), y[~nans])
            # vessel_tracks_interp[i,:,k] = y
            
    for i in range(vessel_tracks.shape[0]):
        lats = vessel_tracks_interp[i,:,0]
        lons = vessel_tracks_interp[i,:,1]
        transform = ccrs.AzimuthalEquidistant(0, -90).transform_points(ccrs.Geodetic(), lons, lats)
        vessel_tracks_interp[i,:,0], vessel_tracks_interp[i,:,1] = np.transpose(transform)[:2]
    
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(vessel_tracks_interp[0,:,0])
    plt.plot(vessel_tracks_interp[0,:,1])
    plt.show()

    return vessel_tracks, vessel_tracks_interp
    
vessel_tracks, vessel_tracks_interp = ScrapeVessels()
with open('vessel_tracks.npy', 'wb') as f:
    np.save(f, vessel_tracks)
with open('vessel_tracks_interp.npy', 'wb') as f:
    np.save(f, vessel_tracks_interp)


"""SPOTS"""
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

dates = np.array([str(day).replace('-', '').replace(':', '') for day in pd.period_range(start='2022-08-01', end='2023-07-31', freq='d')])

def ScrapeSpots():
    # df_spots = pd.DataFrame(columns=['date', 'spot_num', 'note'])
    # for date in dates:
        # for i,spot_dates in enumerate([spot1_dates, spot2_dates, spot3_dates]):
            # for j in range(len(spot_dates)):
                # spot_date = datetime.datetime.strptime(list(spot_dates.values())[j], '%d %b %y').strftime('%Y%m%d')
                # if date == spot_date:
                    # df_new = pd.DataFrame({'date': str(date), 'spot_num': i+1, 'note': list(spot_dates.keys())[j]}, index=[0])
                    # df_spots = pd.concat([df_spots, df_new], ignore_index=True)
    # return df_spots
    return NotImplementedError  # unused code
       
# df_spots = ScrapeSpots()
# print(df_spots.to_string())
# df_spots.to_csv('df_spots.csv')    