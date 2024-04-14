"""
Life-like cellular automaton

Any live cell with S live neighbours survives.
Any dead cell with B neighbours becomes a live cell.
All other live cells die in the next generation. 
Similarly, all other dead cells stay dead.
"""

import os
import numpy as np
from scipy.ndimage import convolve

import matplotlib.pyplot as plt
import matplotlib.animation as animation


rules = {
'B1357/S1357': 'Replicator',
'B2/S': 'Seeds',
'B25/S4': 'Replicator II',
'B3/S012345678': 'Life without Death',
'B3/S23': 'Life',
'B34/S34': '34 Life',
'B35678/S5678': 'Diamoeba',
'B36/S125': '2x2',
'B36/S23': 'HighLife',
'B3678/S34678': 'Day & Night',
'B368/S245': 'Morley',
'B4678/S35678': 'Anneal',
}

weights = np.array([[1,1,1],
                    [1,0,1],
                    [1,1,1]])
mode = 'wrap'

def Life(grid, dimensions, B, S):
    conv = convolve(grid, weights, mode=mode)
    convB, convS = [conv == b for b in B], [conv == s for s in S]
    new_grid = np.zeros(dimensions).T
    new_grid[np.logical_or(np.logical_and(grid == 0,
                                          np.logical_or.reduce(convB)),
                           np.logical_and(grid == 1, 
                                          np.logical_or.reduce(convS)))] = 1
    return new_grid
                    
def update(i, rules, axs, jk, hist):
    for x,(rule,name) in enumerate(zip(rules.keys(), rules.values())):
        BS = rule.split('/')
        B, S = [np.array(list(bs[1:]), dtype=int) for bs in BS]
        j, k = jk[x]
        im = axs[j,k].get_images()
        grid = im[0].get_array()
        new_grid = Life(grid, dimensions, B, S)
        if (abs(hist[x] - np.sum(new_grid)) < np.mean(dimensions)) or \
            np.all(new_grid == grid):
            rand = np.random.rand()
            new_grid = np.random.choice([0, 1], size=dimensions, 
                                        p=[rand, 1-rand])
            hist[x] = np.sum(new_grid)                       
            im[0].set_cmap('Oranges_r')
        else:
            n = 10
            hist[x] = (np.sum(new_grid) + n*hist[x]) / (n+1)
            im[0].set_cmap('binary_r')
        im[0].set_data(new_grid)
    return [axs]
    

dimensions = (64, 64)
    
save = True
if __name__ == '__main__':
    d1, d2 = 3, len(rules)//3
    fig, axs = plt.subplots(d1, d2, figsize=(8,6), dpi=150)
    
    hist = np.zeros(len(rules))
    jk = np.zeros((len(rules), 2), dtype=int)
    for j in range(d1):
        for k in range(d2):
            jk[d2*j+k] = (j, k)
            
            rand = np.random.rand()
            init_grid = np.random.choice([0, 1], size=dimensions, 
                                         p=[rand, 1-rand])
            
            axs[j,k].imshow(init_grid.T, interpolation='none', 
                            cmap='binary_r')
            axs[j,k].axis('off')

            hist[d2*j+k] = np.sum(init_grid)

    plt.tight_layout()
    ani = animation.FuncAnimation(fig, update, fargs=(rules, axs, jk, hist),
                                  interval=333, frames=30)
    if save:
        ani.save(filename='all_rules.gif', writer='pillow')
    else:  
        plt.show()