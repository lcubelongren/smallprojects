
import numpy as np
import matplotlib.pyplot as plt


dice_memory = np.load('dice_memory.npy', allow_pickle=True).ravel()[0]

# plotting score for each branch
track = []
count = 0
for key in dice_memory:
    for subkey in dice_memory[key]:
        for subsubkey in dice_memory[key][subkey]:
            track = np.append(track, dice_memory[key][subkey][subsubkey])
            count += 1
            print(count, dice_memory[key][subkey][subsubkey])
            
plt.scatter(np.arange(0, len(track), 1), track, s=2, c='k')
plt.show()