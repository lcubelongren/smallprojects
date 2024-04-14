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


#np.random.seed(0)
#dimensions = (256, 256)
#init_grid = np.random.choice([0, 1], size=dimensions, p=[0.85, 0.15])
#init_grid = np.random.choice([0, 1], size=dimensions, p=[0.95, 0.05])

np.random.seed(3318)
dimensions = (32, 32)
init_grid = np.random.choice([0, 1], size=dimensions, p=[0.99, 0.01])

# dimensions = (38, 12)
# d1, d2 = dimensions
# init_grid = np.zeros(d1*d2, dtype=int)
# init_grid[[1*d1+25]] = 1
# init_grid[[2*d1+23,2*d1+25]] = 1
# init_grid[[3*d1+13,3*d1+14,3*d1+21,3*d1+22,3*d1+35,3*d1+36]] = 1
# init_grid[[4*d1+12,4*d1+16,4*d1+21,4*d1+22,4*d1+35,4*d1+36]] = 1
# init_grid[[5*d1+1,5*d1+2,5*d1+11,5*d1+17,5*d1+21,5*d1+22]] = 1
# init_grid[[6*d1+1,6*d1+2,6*d1+11,6*d1+15,6*d1+17,6*d1+18,6*d1+15,6*d1+23,6*d1+25]] = 1
# init_grid[[7*d1+11,7*d1+17,7*d1+25]] = 1
# init_grid[[8*d1+12,8*d1+16]] = 1
# init_grid[[9*d1+13,9*d1+14]] = 1


rules = {
'B3/S23': 'Life',
# 'B1357/S1357': 'Replicator',
# 'B2/S': 'Seeds',
# 'B25/S4': 'Replicator II',
# 'B3/S012345678': 'Life without Death',
# 'B34/S34': '34 Life',
# 'B35678/S5678': 'Diamoeba',
# 'B36/S125': '2x2',
# 'B36/S23': 'HighLife',
# 'B3678/S34678': 'Day & Night',
# 'B368/S245': 'Morley',
# 'B4678/S35678': 'Anneal',
}

weights = np.array([[1,1,1],
                    [1,0,1],
                    [1,1,1]])
mode = 'wrap'
#mode = 'constant'

def Life(grid, dimensions, B, S):
    conv = convolve(grid, weights, mode=mode)
    convB, convS = [conv == b for b in B], [conv == s for s in S]
    new_grid = np.zeros(dimensions).T
    new_grid[np.logical_or(np.logical_and(grid == 0,
                                          np.logical_or.reduce(convB)),
                           np.logical_and(grid == 1, 
                                          np.logical_or.reduce(convS)))] = 1
    return new_grid
                    
def update(i, B, S):
    grid = im.get_array()
    new_grid = Life(grid, dimensions, B, S)
    im.set_array(new_grid)
    return [im]
    
save = False
if __name__ == '__main__':
    for rule,name in zip(rules.keys(), rules.values()):  
        BS = rule.split('/')
        B, S = [np.array(list(bs[1:]), dtype=int) for bs in BS]
        
        if not os.path.isdir('videos'):
            os.mkdir('videos')
        if os.path.isfile('videos/{} - {}.mp4'.format(BS, name)) and save:
            continue
        print(rule, name)

        fig, ax = plt.subplots(figsize=(5,5), dpi=150)
        im = plt.imshow(init_grid.T, interpolation='none', cmap='binary_r')
        plt.tick_params(top=False, bottom=False, left=False, right=False,
                        labelleft=False, labelbottom=False)
        plt.title('{} - {}'.format(rule, name))

        ani = animation.FuncAnimation(fig, update, fargs=(B, S),
                                      interval=100, frames=200)
        if save:  
            ani.save('videos/{} - {}.mp4'.format(BS, name))
        else:  
            plt.show()