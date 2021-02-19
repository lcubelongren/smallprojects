
# the computer agent, starting with completely random

import sys, os
sys.path.append(os.path.abspath(os.path.join('..','..','..','solving_kniffel')))

import game
import numpy as np
import matplotlib.pyplot as plt


def ComputerGame0(game, welcome=False):
    """everything random"""
    game = game.Kniffel(welcome)

    while None in game.block_status.values():
        dice = game.ComputerRoll_Random(game.InitialRoll(), 1)  # move 1
        dice = game.ComputerRoll_Random(dice, 2)                # move 2
        game.ComputerBox_Random(dice)                           # box choice
        
    score = sum(filter(None, game.block_status.values()))
    return score
    
def ComputerGame1(game, welcome=False):
    """random dice swapping, maximum box result"""
    game = game.Kniffel(welcome)

    while None in game.block_status.values():
        dice = game.ComputerRoll_Random(game.InitialRoll(), 1)  # move 1
        dice = game.ComputerRoll_Random(dice, 2)                # move 2
        game.ComputerBox_Max(dice)                              # box choice
        
    score = sum(filter(None, game.block_status.values()))
    return score
    
    
ComputerGameChoice = ComputerGame1
    
if __name__ == '__main__':
    num = int(1e3)
    scores = np.zeros(num)
    for i in range(num):
        scores[i] = ComputerGameChoice(game)
    print('mean score: ', np.mean(scores))
    
    plt.hist(scores, 300, density=False, color='k')
    plt.title('game num = {}'.format(num))
    plt.xlabel('score')
    plt.ylabel('number')
    plt.show()
