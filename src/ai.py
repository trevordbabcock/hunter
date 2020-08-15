from collections import deque
from numpy.random import randint
from random import randrange

import actions as act
import static_entity

class HunterAI():
    def __init__(self, hunter):
        self.hunter = hunter
        self.action_queue = deque()
        #self.gamemap = gamemap

    def perform(self):
        if len(self.action_queue) == 0:
            actions = self.decide_where_to_go()
            for a in actions:
                self.action_queue.append(a)
                
            self.action_queue.append(act.SearchAreaAction(self.hunter.engine.game_map, self.hunter.x, self.hunter.y, self.hunter.vision_distance, static_entity.BerryBush))

        action = self.action_queue.popleft()
        action.perform(self.hunter)

    def decide_where_to_go(self):
        direction = randint(4)
        num_actions = randrange(1, 5, 1)
        actions = []

        if(direction == 0):
            for i in range(num_actions):
                actions.append(act.MovementAction(-1, 0))
        elif(direction == 1):
            for i in range(num_actions):
                actions.append(act.MovementAction(1, 0))
        elif(direction == 2):
            for i in range(num_actions):
                actions.append(act.MovementAction(0, -1))
        elif(direction == 3):
            for i in range(num_actions):
                actions.append(act.MovementAction(0, 1))
        
        return actions
    
    # def search_for_berry_bush(self):
    #     visible_map = self.hunter.get_visible_map()

    #     for row in visible_map:
    #         for tile in row:
    #             for entity in tile.entities:
    #                 if isinstance(entity, BerryBush)
    #                     print ("FOUND A BERRY BUSH")
    #                     break

class RabbitAI():
    def __init__(self, rabbit):
        self.rabbit = rabbit

    def perform(self):
        num = randint(4)

        if(num == 0):
            act.MovementAction(-1, 0).perform(self.rabbit)
        elif(num == 1):
            act.MovementAction(1, 0).perform(self.rabbit)
        elif(num == 2):
            act.MovementAction(0, -1).perform(self.rabbit)
        elif(num == 3):
            act.MovementAction(0, 1).perform(self.rabbit)
