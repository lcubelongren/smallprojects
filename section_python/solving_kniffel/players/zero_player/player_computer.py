
# the computer agent, starting with completely random

import sys, os
sys.path.append(os.path.abspath(os.path.join('..','..','..','solving_kniffel')))

import game
import numpy as np
import matplotlib.pyplot as plt


def ComputerGame(game, welcome=False):
    game = game.Kniffel(welcome)

    while None in game.block_status.values():
        dice = game.ComputerRoll(game.InitialRoll(), 1)  # move 1
        dice = game.ComputerRoll(dice, 2)                # move 2
        game.ComputerBox(dice)                           # box choice
        
    score = sum(filter(None, game.block_status.values()))
    return score
    
    
if __name__ == '__main__':
    num = int(5e5)
    scores = np.zeros(num)
    for i in range(num):
        scores[i] = ComputerGame(game)
    print('mean score: ', np.mean(scores))
    
    plt.hist(scores, 500, density=False, color='k')
    plt.title('game num = {}'.format(num))
    plt.xlabel('score')
    plt.ylabel('number (density)')
    plt.show()