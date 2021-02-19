
# the game of Kniffel aka Yahtzee

import sys
import numpy as np
from scipy import stats


def check_quit(user_input):
    if user_input == 'quit':
        print('leaving, goodbye')
        sys.exit(0)

class Kniffel(object):

    def __init__(self, welcome=True):
        self.dice_num = 5
        self.value_fullhouse = 25
        self.value_smallstraight = 30
        self.value_largestraight = 40
        self.value_kniffel = 50
        
        self.section = ['upper', 'lower']
        self.upper_box = ['{}s'.format(i) for i in range(1,7)]
        self.lower_box = ['three_of_a_kind', 'four_of_a_kind', 'full_house', 'small_straight', 'large_straight', 'kniffel', 'chance']
        self.boxes = np.append(self.upper_box, self.lower_box)
        
        self.block_status = {}
        for b in self.boxes:
            self.block_status[b] =  None
            
        if welcome == True:
            print('')
            print('Welcome to Kniffel (aka Yahtzee).')
            print('The goal is to replace dice and obtain pairs.')
            print('Best of luck!')
            
    def Category(self, dice, box):
    
        # section == 'upper'
        
        if box in self.upper_box:
            box = box[0]
            idxs = np.where(dice == int(box))[0]
            return (True, len(idxs) * int(box))
                
        # section == 'lower'
        
        elif box == 'three_of_a_kind':
            for i in range(1,7):
                idxs = np.where(dice == i)[0]
                if len(idxs) >= 3:
                    return (True, np.sum(dice))
            return (False, None)
                    
        elif box == 'four_of_a_kind':
            for i in range(1,7):
                idxs = np.where(dice == i)[0]
                if len(idxs) >= 4:
                    return (True, np.sum(dice))
            return (False, None)
                    
        elif box == 'full_house':
            for i in range(1,7):
                idx_3 = np.where(dice == i)[0]
                if len(idx_3) == 3:
                    for j in range(1,7):
                        if j != i:
                            idx_2 = np.where(dice == j)[0]
                            if len(idx_2) == 2:
                                return (True, self.value_fullhouse)
            return (False, None)
                    
        elif box == 'small_straight':
            if len(np.unique(dice)) == self.dice_num:
                return (True, self.value_smallstraight)
            if len(np.unique(dice)) == self.dice_num-1:
                if np.array_equal(np.diff(np.sort(np.unique(dice))), np.full(self.dice_num-2, 1)):
                    return (True, self.value_smallstraight)
                else:
                    return (False, None)
            else:
                return (False, None)
                
        elif box == 'large_straight':
            if len(np.unique(dice)) == self.dice_num:
                if not (np.min(dice) == 1 and np.max(dice) == 6):
                    return (True, self.value_largestraight)
                return (False, None)
            else:
                return (False, None)
                
        elif box == 'kniffel':
            if len(np.unique(dice)) == 1:
                return (True, self.value_kniffel)
            else:
                return (False, None)
                
        elif box == 'chance':
            return (True, np.sum(dice))
            
        else:
            raise ValueError('No valid section name specified')
            
    def InitialRoll(self):
        dice_result = np.random.randint(1, 7, self.dice_num)
        return dice_result
        
    def Replace(self, dice, switch):
        switch_array = np.array(switch.split(), dtype=int)
        for switch in switch_array:
            idx = np.where(dice == int(switch))[0][0]
            dice = np.delete(dice, idx)
        new_dice = np.random.randint(1, 7, len(switch_array))
        dice = np.append(dice, new_dice)
        return dice
        
    # player selection section    
        
    def PlayerRoll(self, dice, roll_num):
        print('')
        print('Roll #{}: {}'.format(roll_num,dice))
        
        while True:
            try:
                switch = input('Replace which? ')
                new_dice = self.Replace(dice, switch)
            except:
                check_quit(switch)
                print('Not a valid die/dice, try again')
                continue
            else:
                break
                
        return new_dice
        
    def PlayerBox(self, dice):
        print('')
        print('Result: {}'.format(dice))
        print('')
        
        print('Possible boxes ---')
        none_possible = True
        for b in self.boxes:
            if self.block_status[b] == None:
                if self.Category(dice, b)[0]:
                    none_possible = False
                    print(b)  
        if none_possible == True:
            print('*must place a zero*')
            for b in self.boxes:
                if self.block_status[b] == None:
                    print(b)  
                    
        print('')
        
        while True:
            try:
                box = input('Which box would you like? ')
                result = self.Category(dice, box)
            except:
                check_quit(box)
                print('Not a valid box, try again')
                continue
            
            if self.block_status[box] != None:
                print('Box already filled, try again')
            else:
                break
            
        if result[1] == None:
            self.block_status[box] = 0
        else:
            self.block_status[box] = result[1]    
        
    # computer selection section    
        
    def ComputerRoll_Random(self, dice, roll_num):
        switch = np.random.choice(dice, np.random.randint(0, self.dice_num+1), replace=False)
        switch = ' '.join(map(str, switch))
        new_dice = self.Replace(dice, switch)
        return new_dice
        
    def ComputerRoll_Pairs(self, dice, roll_num):
        if len(np.unique(dice)) != self.dice_num:
            mode, count = stats.mode(dice)
            switch = [x for x in dice if x != mode[0]]
        else:
            switch = np.random.choice(dice, np.random.randint(0, self.dice_num+1), replace=False)
        switch = ' '.join(map(str, switch))
        new_dice = self.Replace(dice, switch)
        return new_dice
        
    def ComputerBox_Random(self, dice):
        keys = self.block_status.keys()
        valid_box = [key for key in keys if self.block_status[key] == None]
        box = np.random.choice(valid_box)
        result = self.Category(dice, box)
        if result[1] == None:
            self.block_status[box] = 0
        else:
            self.block_status[box] = result[1]
            
    def ComputerBox_Max(self, dice):
        keys = self.block_status.keys()
        valid_box_result = [(key, self.Category(dice, box=key)[1]) for key in keys if self.block_status[key] == None]
        valid_box_result = [v for v in valid_box_result if v[1] != None]
        if len(valid_box_result) == 0:
            valid_box = [key for key in keys if self.block_status[key] == None]
            box = np.random.choice(valid_box)
            self.block_status[box] = 0
        else:
            box, result = max(valid_box_result, key=lambda x: x[1])
            self.block_status[box] = result

