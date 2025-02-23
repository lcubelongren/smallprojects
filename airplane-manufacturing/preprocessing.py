
import os, xlrd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


directory = pd.read_csv('data/Boeing_10-K/_directory.txt', index_col=0)

count = {}
years = np.arange(1970, 2025)
for year in years:
    count[year] = {}
    if (1993 <= year <= 2024):
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
    elif (1970 <= year <= 1992):
        data_sheet = pd.read_excel('data/Boeing_Annual-Reports.xlsx', header=0, index_col=0)
        row = data_sheet.loc[year].dropna().drop('Total')
        planes = list(row.index)
        for plane in planes:
            num = row[row.index == plane]
            count[year][str(plane)] = int(num)
    #print(year, count[year])

plane_combos = {}
target_planes = ['707', '717', '720', '727', '737', '747', '757', '767', '777', '787']
for target_plane in target_planes:
    plane_combos[target_plane] = {}
    for year in years:
        plane_combos[target_plane][year] = {}
        for plane in count[year].keys():
            if (plane.split(' ')[0] == target_plane) or (plane.split('-')[0] == target_plane) or (plane.split('B')[0] == target_plane):
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

all_planes = []
for year in years:
    for plane in count[year].keys():
        if plane.split('-')[0] == 'MD':
            continue
        if not (plane in all_planes):
            all_planes.append(plane)

deliveries_unpacked = {plane: [count[year][plane] if plane in count[year].keys() else np.nan for year in years] for plane in all_planes}

plt.figure(figsize=(8, 6), dpi=300)
for plane in np.sort(list(deliveries_unpacked.keys())):
    plt.plot(years, deliveries_unpacked[plane], label=plane)
plt.xticks(years[::-10])
plt.ylabel('Deliveries')
plt.xlabel('Year')
plt.legend()
plt.savefig('plot.png')
