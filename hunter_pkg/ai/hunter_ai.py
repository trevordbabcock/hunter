from __future__ import annotations

from collections import deque
from numpy.random import randint
from random import randrange

from .. import flogging
from .. import log_level
from .. import pathfinder
from .. import static_entity


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class HunterAI():
    def __init__(self, hunter):
        self.hunter = hunter
        self.action_queue = deque()

    def perform(self):
        if len(self.action_queue) > 0:
            action = self.action_queue.popleft()

            if(isinstance(action, MovementAction)):
                action.perform()
            elif(isinstance(action, PickAndEatAction)):
                action.perform()
            elif(isinstance(action, SearchAreaAction)):
                action.perform()
        else:
            actions = self.decide_what_to_do()
            for a in actions:
                self.action_queue.append(a)

    def decide_what_to_do(self):
        actions = []
        if self.hunter.is_hungry():
            flog.debug("hunter is HUNGRY")
            actions.append(SearchAreaAction(self.hunter, self.hunter.engine.game_map, self.hunter.vision_distance, static_entity.BerryBush.__name__, self.decide_where_to_go()))
        else:
            flog.debug("hunter is NOT hungry")
            actions = self.decide_where_to_go()

        return actions

    def decide_where_to_go(self):
        direction = randint(4)
        num_actions = randrange(3, 8, 1)
        actions = []

        if(direction == 0):
            for i in range(num_actions):
                actions.append(MovementAction(self.hunter, -1, 0))
        elif(direction == 1):
            for i in range(num_actions):
                actions.append(MovementAction(self.hunter, 1, 0))
        elif(direction == 2):
            for i in range(num_actions):
                actions.append(MovementAction(self.hunter, 0, -1))
        elif(direction == 3):
            for i in range(num_actions):
                actions.append(MovementAction(self.hunter, 0, 1))
        
        return actions


class Action:
    def perform(self):
        raise NotImplementedError()


class MovementAction(Action):
    def __init__(self, hunter, dy, dx):
        super().__init__()

        self.hunter = hunter
        self.dx = dx
        self.dy = dy

    def perform(self):
        if type(self.hunter).__name__ == "Hunter":
            flog.debug("hunter is moving")
        dest_x = self.hunter.x + self.dx
        dest_y = self.hunter.y + self.dy

        if not self.hunter.engine.game_map.in_bounds(dest_x, dest_y):
            return  # Destination is out of bounds.
        if not self.hunter.engine.game_map.tiles[dest_y][dest_x].terrain.walkable:
            return  # Destination is blocked by a tile.

        self.hunter.move(self.dx, self.dy)


class SearchAreaAction(Action):
    def __init__(self, hunter, game_map, search_radius, search_for_class, plan_b):
        self.hunter = hunter
        self.game_map = game_map
        self.search_radius = search_radius
        self.search_for_class = search_for_class
        self.plan_b = plan_b

    def perform(self):
        flog.debug("hunter is searching area")
        search_area = self.get_search_area()
        found_entities = []
        i = 0
        for y in range(len(search_area)):
            row = search_area[y]
            if row != None:
                for x in range(len(row)):
                    tile = row[x]
                    for e in tile.entities:
                        if e.__class__.__name__ == self.search_for_class:
                            i += 1
                            found_entities.append(e)
                            flog.debug("- found an entity: ({},{})".format(e.x, e.y))
                            break

        nearest_entity = None
        nearest_entity_distance = None
        for e in found_entities:
            if nearest_entity == None:
                nearest_entity = e
                nearest_entity_distance = self.get_distance(self.hunter, e)
            else:
                distance = self.get_distance(self.hunter, e)

                if (distance < nearest_entity_distance):
                    nearest_entity = e
                    nearest_entity_distance = distance

        if nearest_entity != None:
            path = pathfinder.get_path(self.game_map.path_map, (self.hunter.y, self.hunter.x), (nearest_entity.y, nearest_entity.x))
            previous_position = (self.hunter.y, self.hunter.x)

            for i in range(1, len(path)):
                self.hunter.ai.action_queue.append(MovementAction(self.hunter, (path[i][0] - previous_position[0]), (path[i][1] - previous_position[1])))
                previous_position = (path[i][0], path[i][1])

            self.hunter.ai.action_queue.append(PickAndEatAction(self.hunter, nearest_entity))
        else:
            for action in self.plan_b:
                self.hunter.ai.action_queue.append(action)

    def get_distance(self, entity1, entity2):
        return abs(entity1.x - entity2.x) + abs(entity1.y - entity2.y)

    def get_search_area(self):
        search_area = [None] * (self.search_radius * 2)
        y_range_start = max(0, self.hunter.y - self.search_radius)
        y_range_end = min(self.game_map.height - 1, self.hunter.y + self.search_radius)
        x_range_start = max(0, self.hunter.x - self.search_radius)
        x_range_end = min(self.game_map.width - 1, self.hunter.x + self.search_radius)
        tmp_map = self.game_map.tiles[y_range_start:y_range_end]

        for y in range(len(tmp_map)):
            search_area[y] = tmp_map[y][x_range_start:x_range_end]

        return search_area


class PickAndEatAction(Action):
    def __init__(self, hunter, static_entity):
        self.hunter = hunter
        self.static_entity = static_entity

    def perform(self):
        flog.debug("hunter is picking and eating")
        berry = self.static_entity.pick_berry()

        if berry != None:
            self.hunter.eat(berry)
            
            if self.hunter.is_still_hungry():
                flog.debug("hunter is still hungry {}/{}".format(self.hunter.curr_hunger, self.hunter.max_hunger))
                if self.static_entity.num_berries > 0:
                    self.hunter.ai.action_queue.append(PickAndEatAction(self.hunter, self.static_entity))
                else:
                    self.hunter.ai.action_queue.append(SearchAreaAction(self.hunter, self.hunter.engine.game_map, self.hunter.vision_distance, static_entity.BerryBush.__name__, self.hunter.ai.decide_where_to_go()))
        else:
            for action in self.hunter.ai.decide_where_to_go():
                self.hunter.ai.action_queue.append(action)
