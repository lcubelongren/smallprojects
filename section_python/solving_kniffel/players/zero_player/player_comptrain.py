
# the learning computer agent

import sys, os
sys.path.append(os.path.abspath(os.path.join('..','..','..','solving_kniffel')))

import game
import numpy as np
import matplotlib.pyplot as plt


def ComputerTrainGame(game, welcome=False):  # mean after 100k games: 119 (no change over epochs)
    """adding memory to allow learning over epochs"""
    game.block_status = {}
    for b in game.boxes:
        game.block_status[b] =  None
          
    while None in game.block_status.values():
        dice0 = game.InitialRoll()
        dice1 = game.ComputerRoll_Train(dice0, dice_past = None,  roll_num=1)  # move 1
        dice2 = game.ComputerRoll_Train(dice1, dice_past = dice0, roll_num=2)  # move 2
        result = game.ComputerBox_Train(dice2)                                # box choice
        
        # add dice combos to memory 
        if tuple(dice0) in game.dice_memory:
            if tuple(dice1) in game.dice_memory[tuple(dice0)]:
                if tuple(dice2) in game.dice_memory[tuple(dice0)][tuple(dice1)]:
                    append_array = np.append(game.dice_memory[tuple(dice0)][tuple(dice1)][tuple(dice2)], result)
                    game.dice_memory[tuple(dice0)][tuple(dice1)][tuple(dice2)] = append_array
                else:
                    game.dice_memory[tuple(dice0)][tuple(dice1)][tuple(dice2)] = np.array(result)
            else: 
                game.dice_memory[tuple(dice0)][tuple(dice1)] = {}
                game.dice_memory[tuple(dice0)][tuple(dice1)][tuple(dice2)] = np.array(result)
        else:
            game.dice_memory[tuple(dice0)] = {}
            game.dice_memory[tuple(dice0)][tuple(dice1)] = {}
            game.dice_memory[tuple(dice0)][tuple(dice1)][tuple(dice2)] = np.array(result)

    score = sum(game.block_status.values())
    return score
    
def TrainMemory(num): 
    for i in range(num):
        scores[i] = ComputerTrainGame(game)
    print('mean score: ', np.mean(scores))

num = int(5e5) 
scores = np.zeros(num)   
    
if __name__ == '__main__':
    game = game.Kniffel(welcome=False)
    TrainMemory(num)
    np.save('dice_memory/dice_memory.npy', game.dice_memory, allow_pickle=True)
    
    # # plotting score over epochs
    # bin_num = 10
    # width = num//bin_num
    # running_avg = [np.mean(scores[x:x+width]) for x in range(bin_num)]
    # plt.scatter(np.arange(0, num, 1), scores, s=2, c='k')
    # plt.plot(np.arange(width, num+width, width), running_avg)
    # plt.show()
    
    # # plotting score for each branch
    # track = []
    # for key in game.dice_memory:
        # for subkey in game.dice_memory[key]:
            # for subsubkey in game.dice_memory[key][subkey]:
                # track = np.append(track, game.dice_memory[key][subkey][subsubkey])
    # plt.scatter(np.arange(0, len(track), 1), track, s=2, c='k')
    # plt.show()
            
            
            