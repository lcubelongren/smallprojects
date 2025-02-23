
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


count = {}
years = np.arange(2003, 2025)
for year in years:
    print(year)
    count[year] = {}
    data = pd.read_excel('data/10-K_{}_Boeing.xls'.format(year), sheet_name=None)
    for sheet_name in data.keys():
        if ('Cumulative deliveries' in data[sheet_name].values) or ('Cumulative Deliveries' in data[sheet_name].values):
            break  # >= 2006
        elif ('Model' in data[sheet_name].values) and (not 'Total' in data[sheet_name].values):
            break  # >= 2002
    if year >= 2006:
        skiprows = np.where(data[sheet_name][data[sheet_name].columns[1]].values == str(year))[0][0] - 1
        data_sheet = pd.read_excel('data/10-K_{}_Boeing.xls'.format(year), sheet_name=sheet_name, skiprows=skiprows, header=1)
        cumulative = data_sheet.loc[1][data_sheet.loc[1].apply(lambda x: isinstance(x, float) and not pd.isna(x))]
        cumulative.rename(index={'737 NG': '737'}, inplace=True)
        for plane in cumulative.index:
            count[year][str(plane)] = int(cumulative[plane])
    elif year >= 2002:
        planes = data[sheet_name][data[sheet_name].columns[1]].dropna()
        planes.drop(planes.loc[planes == 'Model'].index, inplace=True)
        planes.drop(planes.loc[planes == '-'].index, inplace=True)
        cumulative = data[sheet_name][data[sheet_name].columns[3]]
        for row_idx in planes.index:
            count[year][str(planes[row_idx])] = int(cumulative[row_idx])
    else:
        # wrong sheet
        skiprows = data[sheet_name][data[sheet_name][data[sheet_name].columns[3]] == year].index[0]
        data_sheet = pd.read_excel('data/10-K_{}_Boeing.xls'.format(year), sheet_name=sheet_name, skiprows=skiprows, header=1)
        planes = data_sheet[data[sheet_name].columns[1]].dropna()
        planes.drop(planes.loc[planes == '='].index, inplace=True)
        planes.drop(planes.loc[planes == '-'].index, inplace=True)
        cumulative = data_sheet[data_sheet.columns[3]]
        for row_idx in planes.index:
            if planes[row_idx] in count[year]:
                count[year][str(planes[row_idx])] += int(str(cumulative[row_idx]).split('(')[0])
            else:
                count[year][str(planes[row_idx])] = int(str(cumulative[row_idx]).split('(')[0])
    print(count[year])

all_planes = []
for year in years:
    for plane in count[year].keys():
        if not (plane in all_planes):
            all_planes.append(plane)

deliveries_unpacked = {plane: [count[year][plane] if plane in count[year].keys() else np.nan for year in years] for plane in all_planes}

for plane in deliveries_unpacked.keys():
    plt.plot(years, deliveries_unpacked[plane], label=plane)
plt.xticks(years[::-2])
plt.ylabel('Cumulative Deliveries')
plt.xlabel('Year')
plt.legend()
plt.savefig('plot.png')
