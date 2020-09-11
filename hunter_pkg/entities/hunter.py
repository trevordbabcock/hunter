from __future__ import annotations

from collections import deque
from datetime import timedelta
from numpy.random import randint
from time import time

from hunter_pkg.entities import base_entity
from hunter_pkg.entities import berry_bush as bb
from hunter_pkg.helpers import rng

from hunter_pkg.helpers import math

from hunter_pkg import colors
from hunter_pkg import flogging
from hunter_pkg import log_level
from hunter_pkg import pathfinder
from hunter_pkg import stats
from hunter_pkg import vision_map as vsmap


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class Hunter(base_entity.IntelligentEntity):
    def __init__(self, engine, x: int, y: int):
        super().__init__(engine, x, y, "H", colors.white(), colors.light_gray(), HunterAI(self), [stats.Stats.map()["hunter"]["update-interval-start"], stats.Stats.map()["hunter"]["update-interval-end"]], stats.Stats.map()["hunter"]["update-interval-step"])
        self.alive = True
        self.max_hunger = stats.Stats.map()["hunter"]["max-hunger"]
        self.max_health = stats.Stats.map()["hunter"]["max-health"]
        self.max_energy = stats.Stats.map()["hunter"]["max-energy"]
        self.curr_hunger = stats.Stats.map()["hunter"]["starting-hunger"]
        self.curr_health = stats.Stats.map()["hunter"]["starting-health"]
        self.curr_energy = stats.Stats.map()["hunter"]["starting-energy"]
        self.vision_distance = stats.Stats.map()["hunter"]["vision-distance"]
        self.memory = HunterMemory()
        self.recent_actions = []
        self.max_recent_actions = 100
        self.min_recent_actions = 30
        self.days_survived = 0
        self.rt_spawn_time = time()
    
    def can_see(self, entity):
        vd = self.vision_distance
        visible_x = (self.x - vd) < entity.x and entity.x < (self.x + vd)
        visible_y = (self.y - vd) < entity.y and entity.y < (self.y + vd)

        return visible_x and visible_y

    def eat(self, entity):
        flog.debug("hunter ate something")
        self.curr_hunger += entity.nutritional_value

    def is_hungry(self):
        return self.curr_hunger < stats.Stats.map()["hunter"]["hunger-threshold-low"]

    def is_still_hungry(self):
        return self.curr_hunger < stats.Stats.map()["hunter"]["hunger-threshold-high"]

    def die(self):
        flog.debug("omg hunter died")
        self.alive = False
        self.char = "X"

    def progress(self):
        if self.curr_hunger == 0:
            self.die()
        else:
            self.curr_hunger -= stats.Stats.map()["hunter"]["hunger-loss"]
            self.try_flush_recent_actions()
    
    def try_flush_recent_actions(self):
        #flog.debug(f"hunter recent_actions: {len(self.recent_actions)}")

        if len(self.recent_actions) > self.max_recent_actions:
            self.recent_actions = self.recent_actions[self.max_recent_actions-self.min_recent_actions:]
            flog.debug("flushed hunter recent_actions")

    def get_rt_time_alive(self):
        rt_time_alive = timedelta(seconds=round(time() - self.rt_spawn_time))
        flog.debug(f"time alive: {rt_time_alive}")

        return rt_time_alive
        

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
            self.hunter.recent_actions.append("Hunter is hungry!")
            actions.append(SearchAreaAction(self.hunter, self.hunter.engine.game_map, self.hunter.vision_distance, bb.BerryBush.__name__, self.decide_where_to_go()))
        else:
            flog.debug("hunter is NOT hungry")
            self.hunter.recent_actions.append("Hunter is not hungry.")
            actions = self.decide_where_to_go()

        return actions

    def decide_where_to_go(self):
        direction = randint(4)
        num_actions = rng.range(3, 8, 1)
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


class HunterMemory():
    def __init__(self):
        self.map = {
            "explored-terrain": {}
        }


class MovementAction():
    def __init__(self, hunter, dy, dx):
        super().__init__()

        self.hunter = hunter
        self.dx = dx
        self.dy = dy

    def remember_terrain(self, hunter):
        vision_map = vsmap.normal()
        x_start = self.hunter.x - self.hunter.vision_distance
        x_end = self.hunter.x + self.hunter.vision_distance
        y_start = self.hunter.y - self.hunter.vision_distance
        y_end = self.hunter.y + self.hunter.vision_distance

        for y in range(y_start, y_end+1):
            for x in range(x_start, x_end+1):
                # This is confusing. Basic idea is to apply the vision map to the hunter's memory and the game map, but only
                # set "explored" to True, never to False i.e. don't let the corners of a circular vision map "unexplore" tiles.
                # And clamp everything so we dont accidentally affect the opposite side of the map.
                clamp_width = self.hunter.engine.game_map.width-1
                clamp_height = self.hunter.engine.game_map.height-1
                rel_x = math.clamp(x - x_start, 0, clamp_width)
                rel_y = math.clamp(y - y_start, 0, clamp_height)
                clmp_x = math.clamp(x, 0, clamp_width)
                clmp_y = math.clamp(y, 0, clamp_height)
                prev_visible = f"{clmp_x},{clmp_y}" in self.hunter.memory.map["explored-terrain"].keys() and self.hunter.memory.map["explored-terrain"][f"{clmp_x},{clmp_y}"]
                curr_visible = vision_map[rel_y][rel_x].visible
                self.hunter.memory.map["explored-terrain"][f"{clmp_x},{clmp_y}"] = curr_visible or prev_visible
                self.hunter.engine.game_map.tiles[clmp_y][clmp_x].explored = curr_visible or prev_visible

    def perform(self):
        flog.debug("hunter is moving")
        self.hunter.recent_actions.append("Hunter is moving.")

        dest_x = self.hunter.x + self.dx
        dest_y = self.hunter.y + self.dy

        if not self.hunter.engine.game_map.in_bounds(dest_x, dest_y):
            return  # Destination is out of bounds.
        if not self.hunter.engine.game_map.tiles[dest_y][dest_x].terrain.walkable:
            return  # Destination is blocked by a tile.

        # remove reference from origin tile
        orig_tile = self.hunter.engine.game_map.tiles[self.hunter.y][self.hunter.x]
        for entity in orig_tile.entities:
            if entity == self.hunter:
                orig_tile.entities.remove(entity)
        
        # add reference to destination tile
        self.hunter.engine.game_map.tiles[dest_y][dest_x].entities.append(self.hunter)

        self.hunter.move(self.dx, self.dy)
        self.remember_terrain(self.hunter)


class SearchAreaAction():
    def __init__(self, hunter, game_map, search_radius, search_for_class, plan_b):
        self.hunter = hunter
        self.game_map = game_map
        self.search_radius = search_radius
        self.search_for_class = search_for_class
        self.plan_b = plan_b

    def perform(self):
        flog.debug("hunter is searching area")
        self.hunter.recent_actions.append("Hunter is searching area.")

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

        if len(found_entities) > 0:
            self.hunter.recent_actions.append(f"Hunter found a {self.search_for_class}.")
        else:
            self.hunter.recent_actions.append(f"Hunter couldn't find anything to eat.")

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


class PickAndEatAction():
    def __init__(self, hunter, static_entity):
        self.hunter = hunter
        self.static_entity = static_entity

    def perform(self):
        flog.debug("hunter is picking and eating")
        self.hunter.recent_actions.append("Hunter is picking and eating a berry.")

        berry = self.static_entity.pick_berry()

        if berry != None:
            self.hunter.eat(berry)
            
            if self.hunter.is_still_hungry():
                flog.debug("hunter is still hungry {}/{}".format(self.hunter.curr_hunger, self.hunter.max_hunger))
                if self.static_entity.num_berries > 0:
                    self.hunter.ai.action_queue.append(PickAndEatAction(self.hunter, self.static_entity))
                else:
                    self.hunter.ai.action_queue.append(SearchAreaAction(self.hunter, self.hunter.engine.game_map, self.hunter.vision_distance, bb.BerryBush.__name__, self.hunter.ai.decide_where_to_go()))
            else:
                self.hunter.recent_actions.append("Hunter is full!")
        else:
            for action in self.hunter.ai.decide_where_to_go():
                self.hunter.ai.action_queue.append(action)
