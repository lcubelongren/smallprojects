
import os, xlrd, simplejson
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Create a dictionary of plane delivery count by year.

def Boeing():
    print('Preprocessing for Boeing')
    years = np.arange(1958, 2025)
    count = {}
    # 1958 to Present
    fname = 'data/Boeing_OrdersandDeliveries.csv'
    data = pd.read_csv(fname, header=0)
    for year in years:
        count[year] = {}
        planes_listed = data['Model Series'][data['Delivery Year'] == str(year)]
        planes = np.unique(planes_listed)
        for plane in planes:
            num_idxs = data['Delivery Total'].where(np.logical_and(data['Delivery Year'] == str(year), data['Model Series'] == plane))
            num_idxs = num_idxs.dropna().index
            num = np.sum(data['Delivery Total'][num_idxs].values.astype(int))
            count[year][plane] = int(num)
        #print(year, count[year])
    target_planes = ['707', '717', '727', '737', '747', '757', '767', '777', '787']
    count = combinePlanes(count, years, target_planes, name='Boeing')
    plotPlanes(count, years, target_planes, name='Boeing')
    return count

def Airbus():
    print('Preprocessing for Airbus')
    years = np.arange(1974, 2025)
    count = {}
    # 2010 to Present
    years1 = np.arange(2010, 2025)
    fname1 = 'data/Airbus_OaD-2025-01-fl9786.xlsx'
    data1 = pd.read_excel(fname1, sheet_name='Historical deliveries', skiprows=0, header=None)
    data1.dropna(axis=0, how='all', inplace=True)
    data1.dropna(axis=1, how='all', inplace=True)
    for row_idx in data1.index[::2]:
        data_year = data1.loc[row_idx:row_idx+1]
        year = int(data_year.at[row_idx, 0].split(' ')[0])
        if year in years1:
            count[year] = {}
            for col in range(1, 7):
                plane = data_year.at[row_idx, col]
                if not pd.isnull(plane):
                    num = data_year.at[row_idx+1, col]
                    if pd.isnull(num):
                        count[year][str(plane)] = np.nan
                    else:
                        count[year][str(plane)] = int(num)
            #print(year, count[year])
    # 1974 to 2009
    years2 = np.arange(1974, 2010)
    fname2 = 'data/Airbus_Summary_Historial_Orders_Deliveries_1974-2009.xls'
    data2 = pd.read_excel(fname2, sheet_name='HIST&orddel', usecols='O:Y', index_col=0, skiprows=3)
    data2.columns = data2.loc['Year']
    for year in years2:
        count[year] = {}
        for plane in data2.columns:
            num = data2.at[year, plane]
            if pd.isnull(num):
                count[year][str(plane)] = np.nan
            else:
                count[year][str(plane)] = int(num)
        #print(year, count[year])
    target_planes = ['A220', 'A300', 'A310', 'A320', 'A330', 'A340', 'A350', 'A380']
    count = combinePlanes(count, years, target_planes, name='Airbus')
    plotPlanes(count, years, target_planes, name='Airbus')
    return count

# Helper functions.

def combinePlanes(count, years, target_planes, name):
    new_count = {}
    for year in years:
        new_count[year] = {}
        target_planes_num = np.zeros(len(target_planes))
        for plane in count[year].keys():
            for i,target_plane in enumerate(target_planes):
                if name == 'Boeing':
                    if plane[:3] == target_plane[:3]:
                        target_planes_num[i] += count[year][plane]
                if name == 'Airbus':
                    if ((target_plane == 'A320') and (plane in ['A320Family', 'A318', 'A319', 'A320', 'A321'])) or (plane == target_plane):
                        if not np.isnan(count[year][plane]):
                            target_planes_num[i] += count[year][plane]         
        for i,target_plane in enumerate(target_planes):
            if (target_planes_num[i] == 0) or (np.isnan(target_planes_num[i])):
                new_count[year][target_plane] = np.nan
            else:
                new_count[year][target_plane] = int(target_planes_num[i])
        #print(year, new_count[year])
    return new_count

def plotPlanes(count, years, target_planes, name):
    print('Plotting for {}'.format(name))

    # Make a helper variable for plotting.
    data_unpacked = {plane: [count[year][plane] if plane in count[year].keys() else np.nan for year in years] for plane in target_planes}

    # Plot of deliveries over time by plane.
    plt.figure(figsize=(8, 6), dpi=300)
    for plane in np.sort(list(data_unpacked.keys())):
        plt.plot(years, data_unpacked[plane], label=plane)
    plt.ylim([0, 700])
    plt.xlim([1955, 2030])
    plt.ylabel('Deliveries per year')
    plt.xlabel('Year')
    plt.title(name)
    plt.legend(loc='upper left')
    plt.savefig('plots/{}_{}-{}.png'.format(name, years[0], years[-1]))

count_boeing = Boeing()
count_airbus = Airbus()

def exportData(count_boeing, count_airbus):
    print('Exporting data')
    count_all = {}
    for year in np.unique(np.append(list(count_boeing.keys()), list(count_airbus.keys()))):
        if (year in count_boeing.keys()) and (year in count_airbus.keys()):
            count_all[int(year)] = { **count_boeing[year], **count_airbus[year] }
        elif (year in count_boeing.keys()):
            count_all[int(year)] = count_boeing[year]
        elif (year in count_airbus.keys()):
            count_all[int(year)] = count_airbus[year]
    with open('exports/preprocessing.json', 'w') as fp:
        simplejson.dump(count_all , fp, sort_keys=True, indent=4, ignore_nan=True)

exportData(count_boeing, count_airbus)
