
from main import Life

import numpy as np
import matplotlib.pyplot as plt


B, S = [3], [2, 3]
dimensions = (32, 32)

number = np.zeros(int(1e5))
for i in range(len(number)):
    np.random.seed(i)
    old_grid = np.random.choice([0, 1], size=dimensions, p=[0.99, 0.01])
    count, check = 0, 0
    while True:
        count += 1
        new_grid = Life(old_grid, dimensions, B, S)
        delta = np.sum(old_grid) == np.sum(new_grid)
        if delta:
            check += 1
            if check == 10:
                number[i] = count - 10
                break
        else:
            check = 0
            old_grid = new_grid
print(np.argmax(number), np.max(number))
plt.plot(number)
plt.show()