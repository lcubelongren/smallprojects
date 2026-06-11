import numpy as np
import matplotlib.pyplot as plt


fnames = [
    'apollo_8.txt',
    'apollo_9.txt',
    'apollo_10.txt',
    'apollo_11.txt',
    'apollo_12.txt',
    'artemis_I.txt',
    'artemis_II.txt',
    'tiangong-1.txt',
    'international_space_station.txt',
    'mir.txt',
    'moon.txt',
    'earth.txt',
]

for fname in fnames:

    Xs, Ys, Zs = [], [], []

    with open('data/NASA_Horizons/' + fname, 'r') as f:
        read_data = False
        for row in f:
            if len(row.split('$$EOE')) > 1:
                read_data = False
            if read_data:
                X, Y, Z = row.split(',')[2:5]
                Xs.append(float(X))
                Ys.append(float(Y))
                Zs.append(float(Z))
            if len(row.split('$$SOE')) > 1:
                read_data = True

    plt.scatter(Xs, Ys, label=fname.split('.txt')[0], s=1)

plt.scatter(0, 0, c='k', s=10)
plt.legend()
plt.savefig('plot.png')
