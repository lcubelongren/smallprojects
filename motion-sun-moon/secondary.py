"""modified from: https://matplotlib.org/stable/gallery/color/colormap_reference.html"""


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from skyfield.api import load


gradient = np.linspace(0, 1, 256)[::-1]
gradient = np.vstack((gradient, gradient))

num = 1 + (365 * 24)
ts = load.timescale()
t0 = ts.utc(2023, 1, 1, 0, 0)
t1 = ts.utc(2024, 1, 1, 0, 0)
t_list = ts.linspace(t0, t1, num=num)

text_positions = np.linspace(0, 230, num)


def update(i):
    print(i, t_list[i].utc)
    annotation.set_text(t_list[i].utc_strftime('%b'))
    annotation.set_position((text_positions[i], -25))
    annotation.xy = (text_positions[i], 10)
    return annotation


figh, figw = 1, 4
fig, ax = plt.subplots(nrows=1, figsize=(figw, figh), dpi=300)

ax.imshow(gradient, aspect='auto', cmap='twilight', animated=True)
annotation = ax.annotate('', xy=(np.nan, np.nan), xytext=(np.nan, np.nan), xycoords='axes points', 
                         fontsize=16, arrowprops=dict(facecolor='k', shrink=0.05))
                         
plt.subplots_adjust(left=0.1, bottom=0.4, right=0.9, top=1, wspace=0, hspace=1)
plt.axis('off')

ts = len(text_positions)
ani = animation.FuncAnimation(fig, update, frames=ts, interval=5.952)
ani.save('colorbar.mp4')

plt.savefig('colorbar.png')