
# the human agent, played through cmd

import game
import numpy as np
import matplotlib.pyplot as plt


def PlayerGame(game):
    game = game.Kniffel()
    
    while None in game.block_status.values():
        dice = game.PlayerRoll(game.InitialRoll(), 1)  # move 1
        dice = game.PlayerRoll(dice, 2)                # move 2
        game.PlayerBox(dice)                           # box choice

    score = sum(filter(None, game.block_status.values()))

    print('************')
    print(' Game Over ')
    print(' Score : {} '.format(score))
    print('************')
    
    
if __name__ == '__main__':
    PlayerGame(game)
