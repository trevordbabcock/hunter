from collections import deque

from hunter_pkg.entities import base_entity
from hunter_pkg.entities import entity_actions as enta
from hunter_pkg.entities import rabbit as rbt

from hunter_pkg.helpers import direction
from hunter_pkg.helpers import math
from hunter_pkg.helpers import rng
from hunter_pkg.helpers import time_of_day as tod

from hunter_pkg import colors
from hunter_pkg import flogging
from hunter_pkg import log_level
from hunter_pkg import pathfinder as pf
from hunter_pkg import stats
from hunter_pkg import terrain as trrn
from hunter_pkg import vision_map as vsmap


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class Wolf(base_entity.IntelligentEntity):
    def __init__(self, engine, x: int, y: int):
        super().__init__(engine, x, y, "W", colors.white(), colors.light_gray(), WolfAI(self), [stats.Stats.map()["wolf"]["update-interval-start"], stats.Stats.map()["wolf"]["update-interval-end"]], stats.Stats.map()["wolf"]["update-interval-step"])
        self.alive = True
        self.asleep = False
        self.max_health = stats.Stats.map()["wolf"]["max-health"]
        self.curr_health = stats.Stats.map()["wolf"]["starting-health"]
        self.vision_distance = stats.Stats.map()["wolf"]["vision-distance"]
        self.recent_actions = []
        self.hidden = False

    def is_hungry(self):
        return True
    
    def die(self):
        flog.debug("a wolf died")
        self.alive = False
        self.char = "x"

    def progress(self):
        pass


class WolfAI():
    def __init__(self, wolf):
        self.wolf = wolf
        self.action_queue = deque()

    def perform(self):
        if len(self.action_queue) > 0:
            action = self.action_queue.popleft()
            action.perform()
        else:
            actions = self.decide_what_to_do()
            for a in actions:
                self.action_queue.append(a)

    def decide_what_to_do(self):
        actions = []
        
        if self.wolf.is_hungry():
            flog.debug("wolf is hungry")
            self.action_queue.append(SearchAreaAction(self.wolf, [rbt.Rabbit]))
        else:
            self.roam()
        
        return actions

    def roam(self):
        flog.debug("wolf is roaming")
        dist = stats.Stats.map()["wolf"]["roam-distance"]
        max_x = self.wolf.engine.game_map.width - 1
        max_y = self.wolf.engine.game_map.height - 1
        dest_x = math.clamp(rng.range_int(self.wolf.x - dist, self.wolf.x + dist + 1), 0, max_x)
        dest_y = math.clamp(rng.range_int(self.wolf.y - dist, self.wolf.y + dist + 1), 0, max_y)
        dest = self.wolf.engine.game_map.tiles[dest_y][dest_x]

        for action in pf.path_to(self.wolf, [dest.x, dest.y], MovementAction):
            self.wolf.ai.action_queue.append(action)


class MovementAction():
    def __init__(self, wolf, dy, dx):
        self.wolf = wolf
        self.dx = dx
        self.dy = dy
    
    def perform(self):
        if self.wolf.alive:
            dest_x = self.wolf.x + self.dx
            dest_y = self.wolf.y + self.dy

            if not self.wolf.engine.game_map.in_bounds(dest_x, dest_y):
                return  # Destination is out of bounds.
            if not self.wolf.engine.game_map.tiles[dest_y][dest_x].terrain.walkable:
                return  # Destination is blocked by a tile.

            self.wolf.engine.game_map.tiles[self.wolf.y][self.wolf.x].remove_entities([self.wolf])
            self.wolf.engine.game_map.tiles[dest_y][dest_x].add_entities([self.wolf])

            self.wolf.move(self.dx, self.dy)


class SearchAreaAction(enta.SearchAreaActionBase):
    def __init__(self, wolf, search_for_classes):
        self.wolf = wolf
        self.search_radius = self.wolf.vision_distance[self.wolf.engine.time_of_day]
        self.search_for_classes = [c.__name__ for c in search_for_classes]
    
    def perform(self):
        search_area = self.get_search_area(self.wolf, self.search_radius, vsmap.circle)
        found_entities = self.find_terrain(search_area, self.search_for_classes)

        if len(found_entities) > 0:
            rabbit = rng.pick_rand(found_entities) # should find nearest

            for action in pf.path_to(self.wolf, [rabbit.x, rabbit.y], MovementAction):
                self.wolf.ai.action_queue.append(action)
            
            self.wolf.ai.action_queue.append(EatRabbitAction(self.wolf, rabbit))
        else:
            self.wolf.ai.roam()


class AttackAction():
    def __init__(self, wolf, target):
        self.wolf = wolf
        self.target = target

    def perform(self):
        flog.debug("wolf is attacking")


class EatRabbitAction():
    def __init__(self, wolf, rabbit):
        self.wolf = wolf
        self.rabbit = rabbit

    def perform(self):
        flog.debug("wolf is eating a rabbit")
            