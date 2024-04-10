
import numpy as np
import pandas as pd
import plotly.express as px
from  plotly.io import write_html
from pyairports.airports import Airports


"""
Data is taken from: www.transtats.bts.gov
-> Air Carriers : T-100 Segment (All Carriers)

It includes domestic and international segment data. 
Each segment has either the origin or destination within 
the United States.

Taken data with:
PAX, Distance, Carrier, Origin, Dest, Aircraft Type, Year, Month 
"""

# data taken from: Jan.-Sept., 2020
drange = 'Jan. to Sept. 2020'
fname = '54820610_T_T100_SEGMENT_ALL_CARRIER.csv'
df = pd.read_csv('data/' + fname)
# print(df.columns)


def fill_airports(data, airline_dict):
    airports = Airports()  # from import
    df_airports = pd.DataFrame()
    for code in airline_dict:
        name = airline_dict[code][0]
    
        origin = data['ORIGIN'].where(data['CARRIER'] == code).dropna()
        dest = data['DEST'].where(data['CARRIER'] == code).dropna()
        origin_dest = np.unique([origin, dest])
        
        flightnum = origin.value_counts() + dest.value_counts()
        
        df = pd.DataFrame()
        df['code'] = origin_dest
        df['lat'] = np.nan
        df['lon'] = np.nan
        df['city'] = np.nan
        df['airline'] = name
        df['flightnum'] = 0
        
        for i in range(len(df)):
            code = df.loc[i, 'code']
            try:
                df.loc[i, 'lat'] = airports.lookup(code).lat
                df.loc[i, 'lon'] = airports.lookup(code).lon
                df.loc[i, 'city'] = airports.lookup(code).city
                df.loc[i, 'flightnum'] = flightnum[code]
            except:
                pass

        df_airports = df_airports.append(df.dropna())
    return df_airports


airline_dict = {
'OO': ('SkyWest',       '#00529b', 'circle'), 
'OH': ('PSA',           '#1b93cd', 'diamond'),
'C5': ('CommutAir',     '#aeb3b7', 'pentagon'),
'YX': ('Republic',      '#00263a', 'triangle-up'),
'MQ': ('Envoy',         '#212a86', 'triangle-down'),
'9E': ('Endeavor',      '#e51937', 'triangle-left'),
'YV': ('Mesa',          '#000000', 'triangle-right'),
'QX': ('Horizon',       '#00abd2', 'triangle-ne'),
'G7': ('GoJet',         '#0178c1', 'triangle-se'),
'ZW': ('Air Wisconsin', '#8f5b6d', 'triangle-sw'),
'PT': ('Piedmont',      '#d03524', 'triangle-nw')
}
color_dict, symbol_dict = {}, {}
for code in airline_dict:
    color_dict[airline_dict[code][0]]  = airline_dict[code][1]
    symbol_dict[airline_dict[code][0]] = airline_dict[code][2]

df_airports = fill_airports(df, airline_dict)


def jitter(v=0.15):
    # jitter points that overlap
    # supports up to 10 airlines atm
    df_jitter = pd.DataFrame()
    df_multiple = pd.DataFrame()
    codes = df_airports['code'].unique()
    count = df_airports['code'].value_counts()
    
    for i in range(len(codes)):
        temp = df_airports.where(df_airports['code'] == codes[i]).dropna()
        temp = temp.reset_index()
        del temp['index']
        
        if count[codes[i]] != 1:
            # if more than one airliner per airport
            for j in range(1,count[codes[i]]):
                temp['lat'] = temp['lat'].astype(float)
                temp['lon'] = temp['lon'].astype(float)
                
                if j == 10:  # more than 9
                    temp.loc[temp.index[j], 'lon'] += v
                    temp.loc[temp.index[j], 'lat'] += 2*v
                if j%2 == 1 and j != 1:  # left
                    temp.loc[temp.index[j], 'lon'] -= v
                elif j%2 == 0 and j != 2:  # right
                    temp.loc[temp.index[j], 'lon'] += v
                if j in [7, 2, 8]:  # bottom
                    temp.loc[temp.index[j], 'lat'] -= v
                elif j in [5, 1, 6]:  # top
                    temp.loc[temp.index[j], 'lat'] += v
                
                
        df_jitter = df_jitter.append(temp)
        df_multiple = df_multiple.append(temp.loc[0])
    df_jitter = df_jitter.reset_index()
    del df_jitter['index']

    return df_jitter, df_multiple


df_airports, df_multiple  = jitter()
# print(df_airports)
# print(df_multiple)


def plotMap(df_airports):
    title = '<b>Regional Airlines</b> - Origin/Destination'
    fig = px.scatter_geo(
        df_airports, lat='lat', lon='lon', 
        hover_data={'code': True, 'city': True, 'lat': False, 'lon': False, 'airline': False, 'flightnum': False},
        color='airline', color_discrete_map=color_dict, symbol='airline', symbol_map=symbol_dict, opacity=0.8,
        title=title
    )
    fig.update_traces(
        hovertemplate='<b>%{customdata[0]}</b><br>%{customdata[1]}',
        marker=dict(size=12, line=dict(width=0.5, color='grey'))
    )
    fig.update_geos(
        visible=False, resolution=50, scope='north america', fitbounds='locations',
        showcountries=True, countrycolor='black',
        showsubunits=True, subunitcolor='grey'
    )
    fig.update_layout(
        font=dict(family='Courier New', size=16),
        legend=dict(title=None, yanchor='top', y=0.99, xanchor='left', x=0.0, bordercolor='black', borderwidth=1.5),
        legend_title=' <b>Airline Select</b><br> --------------<br> single click:<br> show/hide<br><br> double click:<br> single out<br>'
    )
    fig.add_annotation(
                x=0, y=0, yshift=-60, showarrow=False,
                text='Data from the BTS: {}'.format(drange)          
    )
                         
    config = dict({'displayModeBar': True, 'displaylogo': False, 'showTips': False,
                   'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'toImage']}) 
    return fig, config


if __name__ == '__main__':
    fig, config = plotMap(df_airports)
    write_html(fig, file='regional_airlines.html', config=config)
    fig.show(config=config)          
               
               