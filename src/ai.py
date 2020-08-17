from collections import deque
from numpy.random import randint
from random import randrange

import actions as act
import pathfinder
import static_entity

class HunterAI():
    def __init__(self, hunter):
        self.hunter = hunter
        self.action_queue = deque()
        #self.gamemap = gamemap

    def perform(self):
        if len(self.action_queue) > 0:
            action = self.action_queue.popleft()

            if(isinstance(action, act.MovementAction)):
                action.perform()
            elif(isinstance(action, act.PickAndEatAction)):
                action.perform()
            elif(isinstance(action, act.SearchAreaAction)):
                action.perform()
        else:
            actions = self.decide_what_to_do()
            for a in actions:
                self.action_queue.append(a)

    def decide_what_to_do(self):
        actions = []
        if self.hunter.is_hungry():
            print("hunter is HUNGRY")
            actions.append(act.SearchAreaAction(self.hunter, self.hunter.engine.game_map, self.hunter.vision_distance, static_entity.BerryBush, self.decide_where_to_go()))
        else:
            ("hunter is NOT hungry")
            actions = self.decide_where_to_go()

        return actions

    def decide_where_to_go(self):
        direction = randint(4)
        num_actions = randrange(3, 8, 1)
        actions = []

        if(direction == 0):
            for i in range(num_actions):
                actions.append(act.MovementAction(self.hunter, -1, 0))
        elif(direction == 1):
            for i in range(num_actions):
                actions.append(act.MovementAction(self.hunter, 1, 0))
        elif(direction == 2):
            for i in range(num_actions):
                actions.append(act.MovementAction(self.hunter, 0, -1))
        elif(direction == 3):
            for i in range(num_actions):
                actions.append(act.MovementAction(self.hunter, 0, 1))
        
        return actions


class RabbitAI():
    def __init__(self, rabbit):
        self.rabbit = rabbit

    def perform(self):
        num = randint(4)

        if(num == 0):
            act.MovementAction(self.rabbit, -1, 0).perform()
        elif(num == 1):
            act.MovementAction(self.rabbit, 1, 0).perform()
        elif(num == 2):
            act.MovementAction(self.rabbit, 0, -1).perform()
        elif(num == 3):
            act.MovementAction(self.rabbit, 0, 1).perform()
