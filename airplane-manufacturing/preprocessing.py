
import os, xlrd, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Create a dictionary of plane delivery count by year.

def Boeing():
    count = {}
    years = np.arange(1964, 2025)
    for year in years:
        count[year] = {}
        if (1993 <= year <= years[-1]):
            directory = pd.read_csv('data/Boeing_10-K/_directory.txt', index_col=0)
            sheet_name = directory.at[year, 'sheet_name']
            skiprows = directory.at[year, 'skiprows']
            workbook = xlrd.open_workbook('data/Boeing_10-K/10-K_{}_Boeing.xls'.format(year), logfile=open(os.devnull, 'w'))
            data_sheet = pd.read_excel(workbook, sheet_name=sheet_name, skiprows=skiprows-2, header=1)
            if year >= 2006:
                data_sheet.drop([c for c in data_sheet.columns if 
                                 (str(c).split(':')[0] == 'Unnamed') or (c == 'Total') or (str(c)[0] == '*') or (str(c)[0] == '†')], 
                                 axis='columns', inplace=True)
                planes = data_sheet.columns
                for plane in planes:
                    num = data_sheet[plane][2]
                    if pd.isnull(num):
                        count[year][str(plane)] = 0
                    else:
                        count[year][str(plane)] = int(num)
            else:
                planes = data_sheet[data_sheet.columns[1]].dropna()
                planes.drop(planes.loc[planes == '-'].index, inplace=True)
                planes.drop(planes.loc[planes == '='].index, inplace=True)
                planes.drop(planes.loc[planes == 'Total'].index, inplace=True)
                for idx in planes.index:
                    plane = str(planes[idx]).split('*')[0]
                    num = float(str(data_sheet[year][idx]).split('(')[0])
                    if pd.isnull(num):
                        count[year][str(plane)] = 0
                    else:
                        count[year][str(plane)] = int(num)
        elif (years[0] <= year <= 1992):
            data_sheet = pd.read_excel('data/Boeing_Annual-Reports.xlsx', index_col=0, header=0)
            row = data_sheet.loc[year].dropna().drop('Total')
            planes = list(row.index)
            for plane in planes:
                num = row[row.index == plane]
                count[year][str(plane)] = int(num)
        #print(year, count[year])
    target_planes = ['707', '717', '727', '737', '747', '757', '767', '777', '787']
    count, all_planes = combinePlanes(count, years, target_planes)
    plotPlanes(count, years, all_planes, name='Boeing')
    return count

def Airbus():
    count = {}
    years = np.arange(2006, 2024)
    data_sheet = pd.read_excel('data/Airbus_OaD_2024_10.xlsx', sheet_name='Historical deliveries', skiprows=1, header=None)
    data_sheet.dropna(axis=0, how='all', inplace=True)
    data_sheet.dropna(axis=1, how='all', inplace=True)
    for row_idx in data_sheet.index[::2]:
        data_year = data_sheet.loc[row_idx:row_idx+1]
        year = int(data_year.at[row_idx, 0].split(' ')[0])
        count[year] = {}
        for col in range(1, 7):
            plane = data_year.at[row_idx, col]
            if not pd.isnull(plane):
                num = data_year.at[row_idx+1, col]
                if pd.isnull(num):
                    count[year][str(plane)] = 0
                else:
                    count[year][str(plane)] = int(num)
        #print(year, count[year])
    target_planes = ['A220', 'A310/A300-600', 'A320Family', 'A330', 'A340', 'A350', 'A380']
    count, all_planes = combinePlanes(count, years, target_planes)
    plotPlanes(count, years, all_planes, name='Airbus')
    return count

# Helper functions.

def combinePlanes(count, years, target_planes):
    # Combine plane subtypes.
    plane_combos = {}
    for target_plane in target_planes:
        plane_combos[target_plane] = {}
        for year in years:
            plane_combos[target_plane][year] = {}
            for plane in count[year].keys():
                characters = [' ', '-', '/', 'B']
                for c in characters:
                    if (plane.split(c)[0] == target_plane):
                        plane_combos[target_plane][year][plane] = count[year][plane]
    for year in years:
        for target_plane in plane_combos.keys():
            target_plane_num = 0
            sub_plane_list = []
            if year in plane_combos[target_plane].keys():
                for sub_plane in plane_combos[target_plane][year].keys():
                    sub_num = plane_combos[target_plane][year][sub_plane]
                    sub_plane_list.append(sub_plane)
                    target_plane_num += sub_num
                for sub_plane in sub_plane_list:
                    del count[year][sub_plane]
            if target_plane_num > 0:
                count[year][str(target_plane)] = target_plane_num
        #print(year, count[year])

    # Make a list of all planes.
    all_planes = []
    for year in years:
        for plane in count[year].keys():
            if not plane in target_planes:
                continue
            if not (plane in all_planes):
                all_planes.append(plane)
    
    return count, all_planes

def plotPlanes(count, years, all_planes, name):
    print('Plotting for {}...'.format(name))

    # Make a helper variable for plotting.
    deliveries_unpacked = {plane: [count[year][plane] if plane in count[year].keys() else np.nan for year in years] for plane in all_planes}

    # Plot of deliveries over time by plane.
    plt.figure(figsize=(8, 6), dpi=300)
    for plane in np.sort(list(deliveries_unpacked.keys())):
        plt.plot(years, deliveries_unpacked[plane], label=plane)
    plt.xticks(years[::-10])
    plt.ylabel('Deliveries')
    plt.xlabel('Year')
    plt.legend()
    plt.savefig('plots/{}.png'.format(name))

count_boeing = Boeing()
count_airbus = Airbus()

count_all = {}
for year in np.unique(np.append(list(count_boeing.keys()), list(count_airbus.keys()))):
    if (year in count_boeing.keys()) and (year in count_airbus.keys()):
        count_all[int(year)] = { **count_boeing[year], **count_airbus[year] }
    elif (year in count_boeing.keys()):
        count_all[int(year)] = count_boeing[year]
    elif (year in count_airbus.keys()):
        count_all[int(year)] = count_airbus[year]
    print(year, count_all[year])
with open('exports/airplane-manufacturing-preprocessing.json', 'w') as fp:
    json.dump(count_all , fp)
